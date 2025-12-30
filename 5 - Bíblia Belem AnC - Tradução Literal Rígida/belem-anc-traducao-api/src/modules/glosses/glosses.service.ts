import { query } from "../../config/db";

export interface Gloss {
  id: number;
  token_id: number;
  layer: string;
  content: string;
  metadata: Record<string, unknown>;
}

export type GlossLayer = "N1" | "N2" | "N3" | "N4" | "N5";

export async function getGlossesByToken(tokenId: number, layer?: GlossLayer): Promise<Gloss[]> {
  let sql = `
    SELECT id, token_id, layer, content, metadata
    FROM glosses
    WHERE token_id = $1
  `;
  const values: unknown[] = [tokenId];

  if (layer) {
    sql += ` AND layer = $2`;
    values.push(layer);
  }

  sql += ` ORDER BY layer`;

  const result = await query(sql, values);
  return result.rows as Gloss[];
}

export async function getGlossesByVerse(verseId: number, layer?: GlossLayer): Promise<Gloss[]> {
  let sql = `
    SELECT g.id, g.token_id, g.layer, g.content, g.metadata
    FROM glosses g
    JOIN tokens t ON g.token_id = t.id
    WHERE t.verse_id = $1
  `;
  const values: unknown[] = [verseId];

  if (layer) {
    sql += ` AND g.layer = $2`;
    values.push(layer);
  }

  sql += ` ORDER BY t.position, g.layer`;

  const result = await query(sql, values);
  return result.rows as Gloss[];
}

export async function createGloss(
  tokenId: number,
  layer: GlossLayer,
  content: string,
  metadata?: Record<string, unknown>
): Promise<Gloss> {
  const result = await query(
    `INSERT INTO glosses (token_id, layer, content, metadata)
     VALUES ($1, $2, $3, $4)
     RETURNING id, token_id, layer, content, metadata`,
    [tokenId, layer, content, metadata || {}]
  );
  return result.rows[0] as Gloss;
}

export async function updateGloss(
  glossId: number,
  content: string,
  metadata?: Record<string, unknown>
): Promise<Gloss | null> {
  const result = await query(
    `UPDATE glosses
     SET content = $2, metadata = COALESCE($3, metadata)
     WHERE id = $1
     RETURNING id, token_id, layer, content, metadata`,
    [glossId, content, metadata]
  );
  return result.rows[0] || null;
}

export async function deleteGloss(glossId: number): Promise<boolean> {
  const result = await query(
    `DELETE FROM glosses WHERE id = $1 RETURNING id`,
    [glossId]
  );
  return result.rowCount !== null && result.rowCount > 0;
}
