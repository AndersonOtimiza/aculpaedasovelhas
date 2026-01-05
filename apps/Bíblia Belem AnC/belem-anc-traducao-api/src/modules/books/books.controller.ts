import { Request, Response } from "express";
import { listBooks, getBookByCode, ListBooksParams } from "./books.service";

export async function handleListBooks(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const params: ListBooksParams = {
      testament: req.query.testament as string | undefined,
      trad_group: req.query.trad_group as string | undefined
    };

    const books = await listBooks(params);
    res.json({
      success: true,
      count: books.length,
      data: books
    });
  } catch (error) {
    console.error("Error listing books:", error);
    res.status(500).json({
      success: false,
      error: "Internal server error"
    });
  }
}

export async function handleGetBook(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const { code } = req.params;
    const book = await getBookByCode(code);

    if (!book) {
      res.status(404).json({
        success: false,
        error: `Book with code '${code}' not found`
      });
      return;
    }

    res.json({
      success: true,
      data: book
    });
  } catch (error) {
    console.error("Error getting book:", error);
    res.status(500).json({
      success: false,
      error: "Internal server error"
    });
  }
}
