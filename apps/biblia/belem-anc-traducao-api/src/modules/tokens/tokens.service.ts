import { query } from "../../config/db";

export interface Token {
  id: number;
  verse_id: number;
  position: number;
  text_utf8: string;
  script: string;
  normalized: string | null;
  pt_literal: string | null;
  source_code: string;
}

export interface TokenWithMorphology extends Token {
  lemma: string | null;
  strong_number: string | null;
  morph_code: string | null;
  tense: string | null;
  voice: string | null;
  mood: string | null;
  person: string | null;
  number: string | null;
  gender: string | null;
  case_gram: string | null;
  state: string | null;
}

export interface InterlinearToken {
  position: number;
  original: string;
  script: string;
  literal_pt: string | null;
  lemma: string | null;
  strong_number: string | null;
  morph_code: string | null;
}

export async function listTokensByVerse(verseId: number): Promise<Token[]> {
  const result = await query(
    `SELECT
       t.id, t.verse_id, t.position, t.text_utf8, t.script,
       t.normalized, t.pt_literal, ts.code as source_code
     FROM tokens t
     JOIN text_sources ts ON t.source_id = ts.id
     WHERE t.verse_id = $1
     ORDER BY t.position`,
    [verseId]
  );
  return result.rows as Token[];
}

export async function getTokenById(tokenId: number): Promise<TokenWithMorphology | null> {
  const result = await query(
    `SELECT
       t.id, t.verse_id, t.position, t.text_utf8, t.script,
       t.normalized, t.pt_literal, ts.code as source_code,
       m.lemma, m.strong_number, m.morph_code,
       m.tense, m.voice, m.mood, m.person, m.number, m.gender, m.case_gram, m.state
     FROM tokens t
     JOIN text_sources ts ON t.source_id = ts.id
     LEFT JOIN morphology m ON t.id = m.token_id
     WHERE t.id = $1`,
    [tokenId]
  );
  return result.rows[0] || null;
}

export async function getInterlinear(verseId: number): Promise<InterlinearToken[]> {
  const result = await query(
    `SELECT
       t.position,
       t.text_utf8 as original,
       t.script,
       t.pt_literal as literal_pt,
       m.lemma,
       m.strong_number,
       m.morph_code
     FROM tokens t
     LEFT JOIN morphology m ON t.id = m.token_id
     WHERE t.verse_id = $1
     ORDER BY t.position`,
    [verseId]
  );
  return result.rows as InterlinearToken[];
}

export async function getTokensWithMorphology(verseId: number): Promise<TokenWithMorphology[]> {
  const result = await query(
    `SELECT
       t.id, t.verse_id, t.position, t.text_utf8, t.script,
       t.normalized, t.pt_literal, ts.code as source_code,
       m.lemma, m.strong_number, m.morph_code,
       m.tense, m.voice, m.mood, m.person, m.number, m.gender, m.case_gram, m.state
     FROM tokens t
     JOIN text_sources ts ON t.source_id = ts.id
     LEFT JOIN morphology m ON t.id = m.token_id
     WHERE t.verse_id = $1
     ORDER BY t.position`,
    [verseId]
  );
  return result.rows as TokenWithMorphology[];
}
