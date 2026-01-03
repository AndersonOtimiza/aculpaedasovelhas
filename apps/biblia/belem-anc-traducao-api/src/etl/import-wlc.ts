/**
 * ETL: Importador do Antigo Testamento Hebraico - WLC (Westminster Leningrad Codex)
 *
 * Fonte: bible-pd/sources/AT/WLC/Books/*.xml
 * Licença: Public Domain
 *
 * Importa todos os 39 livros do AT com tokens em hebraico
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

// Mapeamento de nomes de arquivo WLC para códigos do banco
const FILE_TO_BOOK_CODE: Record<string, string> = {
  Genesis: "GEN",
  Exodus: "EXO",
  Leviticus: "LEV",
  Numbers: "NUM",
  Deuteronomy: "DEU",
  Joshua: "JOS",
  Judges: "JDG",
  Ruth: "RUT",
  Samuel_1: "1SA",
  Samuel_2: "2SA",
  Kings_1: "1KI",
  Kings_2: "2KI",
  Chronicles_1: "1CH",
  Chronicles_2: "2CH",
  Ezra: "EZR",
  Nehemiah: "NEH",
  Esther: "EST",
  Job: "JOB",
  Psalms: "PSA",
  Proverbs: "PRO",
  Ecclesiastes: "ECC",
  Song_of_Songs: "SNG",
  Isaiah: "ISA",
  Jeremiah: "JER",
  Lamentations: "LAM",
  Ezekiel: "EZK",
  Daniel: "DAN",
  Hosea: "HOS",
  Joel: "JOL",
  Amos: "AMO",
  Obadiah: "OBA",
  Jonah: "JON",
  Micah: "MIC",
  Nahum: "NAM",
  Habakkuk: "HAB",
  Zephaniah: "ZEP",
  Haggai: "HAG",
  Zechariah: "ZEC",
  Malachi: "MAL",
};

interface ParsedVerse {
  chapter: number;
  verse: number;
  tokens: string[];
}

// Função para remover vogais hebraicas (cantilação e niqud)
function removeVowels(text: string): string {
  return text
    .normalize("NFD")
    .replace(/[\u0591-\u05BD\u05BF-\u05C7]/g, "")
    .normalize("NFC");
}

// Parser de XML WLC para extrair palavras
function parseWLCXML(xmlContent: string): ParsedVerse[] {
  const verses: ParsedVerse[] = [];

  // Encontrar a seção <tanach>
  const tanachMatch = /<tanach>([\s\S]*)<\/tanach>/.exec(xmlContent);
  if (!tanachMatch) {
    console.warn("Seção <tanach> não encontrada");
    return verses;
  }

  const tanachContent = tanachMatch[1];

  // Regex para capítulos
  const chapterRegex = /<c n="(\d+)">([\s\S]*?)<\/c>/g;
  let chapterMatch;

  while ((chapterMatch = chapterRegex.exec(tanachContent)) !== null) {
    const chapterNum = parseInt(chapterMatch[1]);
    const chapterContent = chapterMatch[2];

    // Regex para versículos dentro do capítulo
    const verseRegex = /<v n="(\d+)">([\s\S]*?)<\/v>/g;
    let verseMatch;

    while ((verseMatch = verseRegex.exec(chapterContent)) !== null) {
      const verseNum = parseInt(verseMatch[1]);
      const verseContent = verseMatch[2];

      // Extrair palavras
      const wordRegex = /<w>([^<]+)<\/w>/g;
      const tokens: string[] = [];
      let wordMatch;

      while ((wordMatch = wordRegex.exec(verseContent)) !== null) {
        // Limpar a palavra (remover espaços extras e caracteres especiais)
        const word = wordMatch[1].trim();
        if (word) {
          tokens.push(word);
        }
      }

      if (tokens.length > 0) {
        verses.push({
          chapter: chapterNum,
          verse: verseNum,
          tokens,
        });
      }
    }
  }

  return verses;
}

async function getSourceId(): Promise<number> {
  // Usar OSHB como fonte
  const result = await pool.query(
    `SELECT id FROM text_sources WHERE code = 'OSHB'`
  );

  if (result.rows.length === 0) {
    // Inserir se não existir
    const insertResult = await pool.query(
      `INSERT INTO text_sources (code, name, description, license_name, website_url)
       VALUES ('OSHB', 'Westminster Leningrad Codex', 'Unicode/XML Leningrad Codex (UXLC)', 'Public Domain', 'https://tanach.us')
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
  const parsedVerses = parseWLCXML(xmlContent);

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
      const normalized = removeVowels(token);

      await pool.query(
        `INSERT INTO tokens (verse_id, source_id, position, text_utf8, script, normalized)
         VALUES ($1, $2, $3, $4, 'HE', $5)
         ON CONFLICT (verse_id, source_id, position) DO UPDATE SET text_utf8 = EXCLUDED.text_utf8`,
        [verseId, sourceId, i + 1, token, normalized]
      );
      tokensCount++;
    }
  }

  return { verses: versesCount, tokens: tokensCount };
}

async function main() {
  console.log("=".repeat(60));
  console.log("ETL: Importando Antigo Testamento Hebraico (WLC)");
  console.log("=".repeat(60));

  const sourceDir = path.resolve(
    __dirname,
    "../../../bible-pd/sources/AT/WLC/Books"
  );

  if (!fs.existsSync(sourceDir)) {
    console.error(`Diretório não encontrado: ${sourceDir}`);
    process.exit(1);
  }

  const sourceId = await getSourceId();
  console.log(`Source ID: ${sourceId}`);

  let totalVerses = 0;
  let totalTokens = 0;

  // Filtrar apenas arquivos XML principais (sem .DH)
  const files = fs
    .readdirSync(sourceDir)
    .filter((f) => f.endsWith(".xml") && !f.includes(".DH.") && !f.includes("Index") && !f.includes("Header"));

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
