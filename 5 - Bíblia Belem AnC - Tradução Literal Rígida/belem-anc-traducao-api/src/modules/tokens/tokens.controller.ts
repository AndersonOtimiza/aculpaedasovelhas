import { Request, Response } from "express";
import {
  listTokensByVerse,
  getInterlinear,
  getTokensWithMorphology
} from "./tokens.service";

export async function handleListTokens(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const { verseId } = req.params;
    const verseIdNum = parseInt(verseId, 10);

    if (isNaN(verseIdNum)) {
      res.status(400).json({
        success: false,
        error: "Invalid verse ID"
      });
      return;
    }

    const tokens = await listTokensByVerse(verseIdNum);

    res.json({
      success: true,
      verse_id: verseIdNum,
      count: tokens.length,
      data: tokens
    });
  } catch (error) {
    console.error("Error listing tokens:", error);
    res.status(500).json({
      success: false,
      error: "Internal server error"
    });
  }
}

export async function handleGetInterlinear(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const { verseId } = req.params;
    const verseIdNum = parseInt(verseId, 10);

    if (isNaN(verseIdNum)) {
      res.status(400).json({
        success: false,
        error: "Invalid verse ID"
      });
      return;
    }

    const interlinear = await getInterlinear(verseIdNum);

    if (interlinear.length === 0) {
      res.status(404).json({
        success: false,
        error: `No tokens found for verse ID ${verseId}`
      });
      return;
    }

    res.json({
      success: true,
      verse_id: verseIdNum,
      count: interlinear.length,
      data: interlinear
    });
  } catch (error) {
    console.error("Error getting interlinear:", error);
    res.status(500).json({
      success: false,
      error: "Internal server error"
    });
  }
}

export async function handleGetMorphology(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const { verseId } = req.params;
    const verseIdNum = parseInt(verseId, 10);

    if (isNaN(verseIdNum)) {
      res.status(400).json({
        success: false,
        error: "Invalid verse ID"
      });
      return;
    }

    const tokens = await getTokensWithMorphology(verseIdNum);

    if (tokens.length === 0) {
      res.status(404).json({
        success: false,
        error: `No tokens found for verse ID ${verseId}`
      });
      return;
    }

    res.json({
      success: true,
      verse_id: verseIdNum,
      count: tokens.length,
      data: tokens
    });
  } catch (error) {
    console.error("Error getting morphology:", error);
    res.status(500).json({
      success: false,
      error: "Internal server error"
    });
  }
}
