import { Request, Response } from "express";
import {
  listVersesByChapter,
  getVerseWithTokens,
  searchVerses,
} from "./verses.service";

export async function handleListVerses(req: Request, res: Response): Promise<void> {
  try {
    const { book, chapter } = req.params;
    const chapterNum = parseInt(chapter, 10);

    if (isNaN(chapterNum) || chapterNum < 1) {
      res.status(400).json({
        success: false,
        error: "Invalid chapter number",
      });
      return;
    }

    const verses = await listVersesByChapter(book, chapterNum);

    if (verses.length === 0) {
      res.status(404).json({
        success: false,
        error: `No verses found for ${book} chapter ${chapter}`,
      });
      return;
    }

    res.json({
      success: true,
      book: book.toUpperCase(),
      chapter: chapterNum,
      count: verses.length,
      data: verses,
    });
  } catch (error) {
    console.error("Error listing verses:", error);
    res.status(500).json({
      success: false,
      error: "Internal server error",
    });
  }
}

export async function handleGetVerse(req: Request, res: Response): Promise<void> {
  try {
    const { book, chapter, verse } = req.params;
    const chapterNum = parseInt(chapter, 10);
    const verseNum = parseInt(verse, 10);
    const layer = req.query.layer as string | undefined;

    if (isNaN(chapterNum) || chapterNum < 1) {
      res.status(400).json({
        success: false,
        error: "Invalid chapter number",
      });
      return;
    }

    if (isNaN(verseNum) || verseNum < 1) {
      res.status(400).json({
        success: false,
        error: "Invalid verse number",
      });
      return;
    }

    const verseData = await getVerseWithTokens(book, chapterNum, verseNum, layer);

    if (!verseData) {
      res.status(404).json({
        success: false,
        error: `Verse ${book} ${chapter}:${verse} not found`,
      });
      return;
    }

    res.json({
      success: true,
      layer: layer || "N0",
      data: verseData,
    });
  } catch (error) {
    console.error("Error getting verse:", error);
    res.status(500).json({
      success: false,
      error: "Internal server error",
    });
  }
}

export async function handleSearchVerses(req: Request, res: Response): Promise<void> {
  try {
    const { q, script, limit } = req.query;

    if (!q || typeof q !== "string" || q.trim().length < 2) {
      res.status(400).json({
        success: false,
        error: "Search query must be at least 2 characters",
      });
      return;
    }

    const limitNum = limit ? parseInt(limit as string, 10) : 50;
    const verses = await searchVerses(q, script as string | undefined, limitNum);

    res.json({
      success: true,
      query: q,
      script: script || "all",
      count: verses.length,
      data: verses,
    });
  } catch (error) {
    console.error("Error searching verses:", error);
    res.status(500).json({
      success: false,
      error: "Internal server error",
    });
  }
}
