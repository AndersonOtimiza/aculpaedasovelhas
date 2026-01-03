/**
 * ETL: Importador do Novo Testamento Grego - Nestle 1904
 *
 * Fonte: sources/nt_nestle1904/Nestle1904-master/xml/*.xml
 * Licença: Public Domain
 *
 * Importa todos os 27 livros do NT com tokens em grego
 */

import { Pool } from "pg";
import * as fs from "fs";
import * as path from "path";

// Configuração do banco (usa variáveis de ambiente ou defaults para execução local)
const pool = new Pool({
  host: process.env.DB_HOST || "localhost",
  port: parseInt(process.env.DB_PORT || "5433"), // Porta 5433 para não conflitar
  user: process.env.DB_USER || "postgres",
  password: process.env.DB_PASSWORD || "postgres",
  database: process.env.DB_NAME || "belem_anc_traducao",
});

// Mapeamento de nomes de arquivo para códigos do banco
const FILE_TO_BOOK_CODE: Record<string, string> = {
  "01-matthew": "MAT",
  "02-mark": "MRK",
  "03-luke": "LUK",
  "04-john": "JHN",
  "05-acts": "ACT",
  "06-romans": "ROM",
  "07-1corinthians": "1CO",
  "08-2corinthians": "2CO",
  "09-galatians": "GAL",
  "10-ephesians": "EPH",
  "11-philippians": "PHP",
  "12-colossians": "COL",
  "13-1thessalonians": "1TH",
  "14-2thessalonians": "2TH",
  "15-1timothy": "1TI",
  "16-2timothy": "2TI",
  "17-titus": "TIT",
  "18-philemon": "PHM",
  "19-hebrews": "HEB",
  "20-james": "JAS",
  "21-1peter": "1PE",
  "22-2peter": "2PE",
  "23-1john": "1JN",
  "24-2john": "2JN",
  "25-3john": "3JN",
  "26-jude": "JUD",
  "27-revelation": "REV",
};

interface ParsedVerse {
  chapter: number;
  verse: number;
  tokens: string[];
}

// Parser simples de XML para extrair palavras
function parseNestleXML(xmlContent: string): ParsedVerse[] {
  const verses: ParsedVerse[] = [];

  // Regex para encontrar milestones de versículo
  const verseRegex = /<milestone unit="verse" id="[^.]+\.(\d+)\.(\d+)"\/>/g;
  // Regex para encontrar palavras
  const wordRegex = /<w[^>]*>([^<]+)<\/w>/g;

  let currentChapter = 0;
  let currentVerse = 0;
  let currentTokens: string[] = [];

  // Processa linha por linha
  const lines = xmlContent.split("\n");

  for (const line of lines) {
    // Verifica se há um milestone de versículo
    const milestoneMatch = /<milestone unit="verse" id="[^.]+\.(\d+)\.(\d+)"/.exec(line);
    if (milestoneMatch) {
      // Salva versículo anterior se existir
      if (currentVerse > 0 && currentTokens.length > 0) {
        verses.push({
          chapter: currentChapter,
          verse: currentVerse,
          tokens: [...currentTokens],
        });
      }

      currentChapter = parseInt(milestoneMatch[1]);
      currentVerse = parseInt(milestoneMatch[2]);
      currentTokens = [];
    }

    // Extrai palavras da linha
    let wordMatch;
    const tempWordRegex = /<w[^>]*>([^<]+)<\/w>/g;
    while ((wordMatch = tempWordRegex.exec(line)) !== null) {
      currentTokens.push(wordMatch[1]);
    }
  }

  // Salva último versículo
  if (currentVerse > 0 && currentTokens.length > 0) {
    verses.push({
      chapter: currentChapter,
      verse: currentVerse,
      tokens: currentTokens,
    });
  }

  return verses;
}

async function getSourceId(): Promise<number> {
  // Usar SBLGNT como fonte (já existe no schema)
  const result = await pool.query(
    `SELECT id FROM text_sources WHERE code = 'SBLGNT'`
  );

  if (result.rows.length === 0) {
    // Inserir se não existir
    const insertResult = await pool.query(
      `INSERT INTO text_sources (code, name, description, license_name, website_url)
       VALUES ('SBLGNT', 'Nestle 1904 Greek NT', 'Nestle 1904 Greek New Testament', 'Public Domain', 'https://github.com/biblicalhumanities/Nestle1904')
       RETURNING id`
    );
    return insertResult.rows[0].id;
  }

  return result.rows[0].id;
}

async function getBookId(code: string): Promise<number | null> {
  const result = await pool.query(`SELECT id FROM books WHERE code = $1`, [code]);
  return result.rows.length > 0 ? result.rows[0].id : null;
}

async function importBook(
  filePath: string,
  bookCode: string,
  sourceId: number
): Promise<{ verses: number; tokens: number }> {
  const bookId = await getBookId(bookCode);
  if (!bookId) {
    console.warn(`Book ${bookCode} not found in database`);
    return { verses: 0, tokens: 0 };
  }

  const xmlContent = fs.readFileSync(filePath, "utf-8");
  const parsedVerses = parseNestleXML(xmlContent);

  let versesCount = 0;
  let tokensCount = 0;

  for (const pv of parsedVerses) {
    // Inserir versículo
    const canonicalRef = `${bookCode} ${pv.chapter}:${pv.verse}`;
    const verseResult = await pool.query(
      `INSERT INTO verses (book_id, chapter, verse, canonical_ref)
       VALUES ($1, $2, $3, $4)
       ON CONFLICT (book_id, chapter, verse) DO UPDATE SET canonical_ref = EXCLUDED.canonical_ref
       RETURNING id`,
      [bookId, pv.chapter, pv.verse, canonicalRef]
    );
    const verseId = verseResult.rows[0].id;
    versesCount++;

    // Inserir tokens
    for (let i = 0; i < pv.tokens.length; i++) {
      const token = pv.tokens[i];
      await pool.query(
        `INSERT INTO tokens (verse_id, source_id, position, text_utf8, script, normalized)
         VALUES ($1, $2, $3, $4, 'GRC', $5)
         ON CONFLICT (verse_id, source_id, position) DO UPDATE SET text_utf8 = EXCLUDED.text_utf8`,
        [verseId, sourceId, i + 1, token, token.toLowerCase()]
      );
      tokensCount++;
    }
  }

  return { verses: versesCount, tokens: tokensCount };
}

async function main() {
  console.log("=".repeat(60));
  console.log("ETL: Importando Novo Testamento Grego (Nestle 1904)");
  console.log("=".repeat(60));

  const sourceDir = path.resolve(
    __dirname,
    "../../../sources/nt_nestle1904/Nestle1904-master/xml"
  );

  if (!fs.existsSync(sourceDir)) {
    console.error(`Diretório não encontrado: ${sourceDir}`);
    process.exit(1);
  }

  const sourceId = await getSourceId();
  console.log(`Source ID: ${sourceId}`);

  let totalVerses = 0;
  let totalTokens = 0;

  const files = fs.readdirSync(sourceDir).filter((f) => f.endsWith(".xml") && !f.includes("nestle1904.xml"));

  for (const file of files) {
    const baseName = path.basename(file, ".xml");
    const bookCode = FILE_TO_BOOK_CODE[baseName];

    if (!bookCode) {
      console.log(`Ignorando arquivo: ${file}`);
      continue;
    }

    console.log(`\nImportando ${bookCode} (${file})...`);
    const filePath = path.join(sourceDir, file);
    const { verses, tokens } = await importBook(filePath, bookCode, sourceId);

    console.log(`  -> ${verses} versículos, ${tokens} tokens`);
    totalVerses += verses;
    totalTokens += tokens;
  }

  console.log("\n" + "=".repeat(60));
  console.log(`TOTAL: ${totalVerses} versículos, ${totalTokens} tokens`);
  console.log("=".repeat(60));

  await pool.end();
}

main()
  .then(() => {
    console.log("\nImportação concluída!");
    process.exit(0);
  })
  .catch((err) => {
    console.error("Erro:", err);
    process.exit(1);
  });
