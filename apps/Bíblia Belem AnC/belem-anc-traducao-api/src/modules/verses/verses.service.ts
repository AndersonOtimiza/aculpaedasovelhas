import { query } from "../../config/db";

export interface Verse {
  id: number;
  book_id: number;
  book_code: string;
  book_name: string;
  chapter: number;
  verse: number;
  canonical_ref: string;
  testament: string;
  trad_group: string;
}

export interface VerseWithTokens extends Verse {
  tokens: VerseToken[];
  translations?: VerseTranslation[];
}

export interface VerseToken {
  position: number;
  text_utf8: string;
  script: string;
  normalized: string | null;
  pt_literal: string | null;
  lemma?: string | null;
  strong_number?: string | null;
  morph_code?: string | null;
}

export interface VerseTranslation {
  layer: string;
  literal_pt: string | null;
  readable_pt: string | null;
  translator?: string | null;
  method?: string | null;
  rigidity_level?: string | null;
  source?: string | null;
  created_at?: Date;
  updated_at?: Date;
}

export async function listVersesByChapter(
  bookCode: string,
  chapter: number
): Promise<Verse[]> {
  const result = await query(
    `SELECT
       v.id, v.book_id, b.code as book_code, b.name_pt as book_name,
       v.chapter, v.verse, v.canonical_ref, b.testament, b.trad_group
     FROM verses v
     JOIN books b ON v.book_id = b.id
     WHERE b.code = $1 AND v.chapter = $2
     ORDER BY v.verse`,
    [bookCode.toUpperCase(), chapter]
  );
  return result.rows as Verse[];
}

export async function getVerseById(verseId: number): Promise<Verse | null> {
  const result = await query(
    `SELECT
       v.id, v.book_id, b.code as book_code, b.name_pt as book_name,
       v.chapter, v.verse, v.canonical_ref, b.testament, b.trad_group
     FROM verses v
     JOIN books b ON v.book_id = b.id
     WHERE v.id = $1`,
    [verseId]
  );
  return result.rows[0] || null;
}

export async function getVerseWithTokens(
  bookCode: string,
  chapter: number,
  verse: number,
  includeGlosses?: string
): Promise<VerseWithTokens | null> {
  // Primeiro buscar o versículo
  const verseResult = await query(
    `SELECT
       v.id, v.book_id, b.code as book_code, b.name_pt as book_name,
       v.chapter, v.verse, v.canonical_ref, b.testament, b.trad_group
     FROM verses v
     JOIN books b ON v.book_id = b.id
     WHERE b.code = $1 AND v.chapter = $2 AND v.verse = $3`,
    [bookCode.toUpperCase(), chapter, verse]
  );

  if (verseResult.rows.length === 0) {
    return null;
  }

  const verseData = verseResult.rows[0] as Verse;

  // Buscar tokens do versículo
  const tokenSql = `
    SELECT
      t.position, t.text_utf8, t.script, t.normalized, t.pt_literal,
      m.lemma, m.strong_number, m.morph_code
    FROM tokens t
    LEFT JOIN morphology m ON t.id = m.token_id
    WHERE t.verse_id = $1
    ORDER BY t.position
  `;

  const tokenResult = await query(tokenSql, [verseData.id]);

  // Buscar traduções consolidadas por versículo (se existirem)
  const translationsResult = await query(
    `
    SELECT
      layer, literal_pt, readable_pt, translator, method, rigidity_level, source,
      created_at, updated_at
    FROM verse_translations
    WHERE verse_id = $1
    ORDER BY layer
    `,
    [verseData.id]
  );

  return {
    ...verseData,
    tokens: tokenResult.rows as VerseToken[],
    translations: translationsResult.rows as VerseTranslation[]
  };
}

export async function searchVerses(
  searchQuery: string,
  script?: string,
  limit: number = 50
): Promise<Verse[]> {
  let sql = `
    SELECT DISTINCT
       v.id, v.book_id, b.code as book_code, b.name_pt as book_name,
       v.chapter, v.verse, v.canonical_ref, b.testament, b.trad_group
     FROM verses v
     JOIN books b ON v.book_id = b.id
     JOIN tokens t ON v.id = t.verse_id
     WHERE (t.text_utf8 ILIKE $1 OR t.normalized ILIKE $1 OR t.pt_literal ILIKE $1)
  `;
  const values: unknown[] = [`%${searchQuery}%`];
  let paramIndex = 2;

  if (script) {
    sql += ` AND t.script = $${paramIndex++}`;
    values.push(script.toUpperCase());
  }

  sql += ` ORDER BY b.canon_order, v.chapter, v.verse LIMIT $${paramIndex}`;
  values.push(limit);

  const result = await query(sql, values);
  return result.rows as Verse[];
}
