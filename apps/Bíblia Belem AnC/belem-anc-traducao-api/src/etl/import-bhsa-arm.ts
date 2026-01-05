/**
 * ETL: Importador de textos Aramaicos do BHSA (ETCBC)
 *
 * Fonte: https://github.com/ETCBC/bhsa
 * Licença: CC BY-NC 4.0
 *
 * Porções aramaicas do AT:
 * - Daniel 2:4b-7:28
 * - Esdras 4:8-6:18; 7:12-26
 * - Jeremias 10:11 (um versículo)
 * - Gênesis 31:47 (duas palavras)
 */

import { pool } from "../config/db";

// Função para remover vogais hebraicas/aramaicas (mesma função do hebraico)
function removeVowels(text: string): string {
  return text
    .normalize("NFD")
    .replace(/[\u0591-\u05BD\u05BF-\u05C7]/g, "")
    .normalize("NFC");
}

// Parser de morfologia ETCBC para Aramaico
function parseETCBCMorphology(morphCode: string): {
  person?: string;
  number?: string;
  gender?: string;
  state?: string;
  tense?: string;
  voice?: string;
} {
  const result: Record<string, string> = {};

  // ETCBC usa códigos como: vb/perf/peal/p3/m/sg
  const parts = morphCode.toLowerCase().split("/");

  for (const part of parts) {
    // Pessoa
    if (part.startsWith("p")) {
      const personMatch = part.match(/p([123])/);
      if (personMatch) result.person = personMatch[1];
    }

    // Número
    if (part === "sg") result.number = "Singular";
    else if (part === "pl") result.number = "Plural";
    else if (part === "du") result.number = "Dual";

    // Gênero
    if (part === "m") result.gender = "Masculine";
    else if (part === "f") result.gender = "Feminine";
    else if (part === "c") result.gender = "Common";

    // Estado (específico do Aramaico/Hebraico)
    if (part === "a" || part === "abs") result.state = "Absolute";
    else if (part === "c" || part === "cst") result.state = "Construct";
    else if (part === "e" || part === "emph") result.state = "Emphatic"; // Típico do Aramaico

    // Tempo verbal
    if (part === "perf") result.tense = "Perfect";
    else if (part === "impf") result.tense = "Imperfect";
    else if (part === "impv") result.tense = "Imperative";
    else if (part === "ptcp" || part === "ptca") result.tense = "Participle";
    else if (part === "infa" || part === "infc") result.tense = "Infinitive";

    // Voz/Stem (específico do Aramaico)
    if (part === "peal")
      result.voice = "Peal"; // Equivalente ao Qal hebraico
    else if (part === "pael")
      result.voice = "Pael"; // Equivalente ao Piel
    else if (part === "haphel")
      result.voice = "Haphel"; // Equivalente ao Hiphil
    else if (part === "ithpeel")
      result.voice = "Ithpeel"; // Passivo reflexivo
    else if (part === "ithpaal") result.voice = "Ithpaal";
    else if (part === "aphel") result.voice = "Aphel";
  }

  return result;
}

interface AramaicToken {
  text: string;
  lemma?: string;
  morph?: string;
  strong?: string;
}

interface AramaicVerse {
  book: string;
  chapter: number;
  verse: number;
  tokens: AramaicToken[];
}

async function ensureTextSource(): Promise<number> {
  const result = await pool.query(
    `INSERT INTO text_sources (code, name, description, license_name, website_url)
     VALUES ($1, $2, $3, $4, $5)
     ON CONFLICT (code) DO UPDATE SET name = EXCLUDED.name
     RETURNING id`,
    [
      "BHSA-ARM",
      "ETCBC Aramaic (BHSA)",
      "Porções aramaicas do Antigo Testamento com morfologia ETCBC",
      "CC BY-NC 4.0",
      "https://github.com/ETCBC/bhsa"
    ]
  );
  return result.rows[0].id;
}

async function getOrCreateVerse(
  bookCode: string,
  chapter: number,
  verse: number
): Promise<number | null> {
  // Buscar o livro
  const bookResult = await pool.query("SELECT id FROM books WHERE code = $1", [
    bookCode
  ]);

  if (bookResult.rows.length === 0) {
    console.warn(`Book ${bookCode} not found`);
    return null;
  }

  const bookId = bookResult.rows[0].id;
  const canonicalRef = `${bookCode} ${chapter}:${verse}`;

  // Inserir ou buscar versículo
  const verseResult = await pool.query(
    `INSERT INTO verses (book_id, chapter, verse, canonical_ref)
     VALUES ($1, $2, $3, $4)
     ON CONFLICT (book_id, chapter, verse) DO UPDATE SET canonical_ref = EXCLUDED.canonical_ref
     RETURNING id`,
    [bookId, chapter, verse, canonicalRef]
  );

  return verseResult.rows[0].id;
}

async function insertToken(
  verseId: number,
  sourceId: number,
  position: number,
  token: AramaicToken
): Promise<number> {
  const normalized = removeVowels(token.text);

  const tokenResult = await pool.query(
    `INSERT INTO tokens (verse_id, source_id, position, text_utf8, script, normalized, pt_literal)
     VALUES ($1, $2, $3, $4, $5, $6, $7)
     ON CONFLICT (verse_id, source_id, position)
     DO UPDATE SET text_utf8 = EXCLUDED.text_utf8, normalized = EXCLUDED.normalized
     RETURNING id`,
    [verseId, sourceId, position, token.text, "ARM", normalized, null]
  );

  const tokenId = tokenResult.rows[0].id;

  // Inserir morfologia se disponível
  if (token.morph || token.lemma || token.strong) {
    const morphData = token.morph ? parseETCBCMorphology(token.morph) : {};

    await pool.query(
      `INSERT INTO morphology (token_id, lemma, strong_number, morph_code, tense, voice, person, number, gender, state, extra_tags)
       VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11)
       ON CONFLICT (token_id) DO UPDATE SET
         lemma = EXCLUDED.lemma,
         strong_number = EXCLUDED.strong_number,
         morph_code = EXCLUDED.morph_code`,
      [
        tokenId,
        token.lemma || null,
        token.strong || null,
        token.morph || null,
        morphData.tense || null,
        morphData.voice || null,
        morphData.person || null,
        morphData.number || null,
        morphData.gender || null,
        morphData.state || null,
        JSON.stringify({ system: "ETCBC", language: "Aramaic" })
      ]
    );
  }

  return tokenId;
}

export async function importAramaic(data: AramaicVerse[]): Promise<void> {
  const client = await pool.connect();

  try {
    await client.query("BEGIN");

    const sourceId = await ensureTextSource();
    console.log(`Using source ID: ${sourceId}`);

    let versesProcessed = 0;
    let tokensProcessed = 0;

    for (const verseData of data) {
      const verseId = await getOrCreateVerse(
        verseData.book,
        verseData.chapter,
        verseData.verse
      );

      if (!verseId) {
        console.warn(
          `Skipping ${verseData.book} ${verseData.chapter}:${verseData.verse}`
        );
        continue;
      }

      for (let i = 0; i < verseData.tokens.length; i++) {
        await insertToken(verseId, sourceId, i + 1, verseData.tokens[i]);
        tokensProcessed++;
      }

      versesProcessed++;

      if (versesProcessed % 100 === 0) {
        console.log(
          `Processed ${versesProcessed} verses, ${tokensProcessed} tokens...`
        );
      }
    }

    await client.query("COMMIT");
    console.log("\nImport complete!");
    console.log(`Total verses: ${versesProcessed}`);
    console.log(`Total tokens: ${tokensProcessed}`);
  } catch (error) {
    await client.query("ROLLBACK");
    console.error("Import failed:", error);
    throw error;
  } finally {
    client.release();
  }
}

// Exemplo de uso com dados de teste
async function runSampleImport() {
  // Dados de exemplo - Daniel 2:4 (início da seção aramaica)
  const sampleData: AramaicVerse[] = [
    {
      book: "DAN",
      chapter: 2,
      verse: 4,
      tokens: [
        {
          text: "וַיְדַבְּר֧וּ",
          lemma: "דבר",
          morph: "vb/impf/pael/p3/m/pl",
          strong: "H1696"
        },
        {
          text: "הַכַּשְׂדִּ֛ים",
          lemma: "כשדי",
          morph: "subs/m/pl/emph",
          strong: "H3779"
        },
        {
          text: "לְמַלְכָּ֖א",
          lemma: "מלך",
          morph: "subs/m/sg/emph",
          strong: "H4430"
        },
        {
          text: "אֲרָמִ֑ית",
          lemma: "ארמית",
          morph: "subs/f/sg/abs",
          strong: "H762"
        },
        {
          text: "מַלְכָּ֣א",
          lemma: "מלך",
          morph: "subs/m/sg/emph",
          strong: "H4430"
        },
        {
          text: "לְעָלְמִ֣ין",
          lemma: "עלם",
          morph: "subs/m/pl/abs",
          strong: "H5957"
        },
        {
          text: "חֱיִ֔י",
          lemma: "חיה",
          morph: "vb/impv/peal/p2/m/sg",
          strong: "H2418"
        }
      ]
    }
  ];

  console.log("Starting Aramaic sample import...");
  await importAramaic(sampleData);
}

// Se executado diretamente
if (require.main === module) {
  runSampleImport()
    .then(() => {
      console.log("Done!");
      process.exit(0);
    })
    .catch((err) => {
      console.error("Error:", err);
      process.exit(1);
    });
}
