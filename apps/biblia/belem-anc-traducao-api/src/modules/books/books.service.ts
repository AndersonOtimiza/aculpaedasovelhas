import { query } from "../../config/db";

export interface Book {
  id: number;
  canon_order: number;
  code: string;
  name_original: string;
  name_pt: string;
  testament: string;
  trad_group: string;
  chapters_count: number | null;
}

export interface ListBooksParams {
  testament?: string;
  trad_group?: string;
}

export async function listBooks(params?: ListBooksParams): Promise<Book[]> {
  let sql = `
    SELECT id, canon_order, code, name_original, name_pt, testament, trad_group, chapters_count
    FROM books
    WHERE 1=1
  `;
  const values: unknown[] = [];
  let paramIndex = 1;

  if (params?.testament) {
    sql += ` AND testament = $${paramIndex++}`;
    values.push(params.testament);
  }

  if (params?.trad_group) {
    sql += ` AND trad_group = $${paramIndex++}`;
    values.push(params.trad_group);
  }

  sql += ` ORDER BY canon_order`;

  const result = await query(sql, values);
  return result.rows as Book[];
}

export async function getBookByCode(code: string): Promise<Book | null> {
  const result = await query(
    `SELECT id, canon_order, code, name_original, name_pt, testament, trad_group, chapters_count
     FROM books
     WHERE code = $1`,
    [code.toUpperCase()]
  );
  return result.rows[0] || null;
}

export async function getBookById(id: number): Promise<Book | null> {
  const result = await query(
    `SELECT id, canon_order, code, name_original, name_pt, testament, trad_group, chapters_count
     FROM books
     WHERE id = $1`,
    [id]
  );
  return result.rows[0] || null;
}
