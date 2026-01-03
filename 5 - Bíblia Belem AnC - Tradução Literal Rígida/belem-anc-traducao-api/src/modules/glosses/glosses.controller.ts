import { Request, Response } from "express";
import {
  getGlossesByToken,
  getGlossesByVerse,
  GlossLayer
} from "./glosses.service";

const validLayers: GlossLayer[] = ["N1", "N2", "N3", "N4", "N5"];

function isValidLayer(layer: string): layer is GlossLayer {
  return validLayers.includes(layer as GlossLayer);
}

export async function handleGetGlossesByToken(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const { tokenId } = req.params;
    const layer = req.query.layer as string | undefined;
    const tokenIdNum = parseInt(tokenId, 10);

    if (isNaN(tokenIdNum)) {
      res.status(400).json({
        success: false,
        error: "Invalid token ID"
      });
      return;
    }

    if (layer && !isValidLayer(layer)) {
      res.status(400).json({
        success: false,
        error: `Invalid layer. Must be one of: ${validLayers.join(", ")}`
      });
      return;
    }

    const glosses = await getGlossesByToken(
      tokenIdNum,
      layer as GlossLayer | undefined
    );

    res.json({
      success: true,
      token_id: tokenIdNum,
      layer: layer || "all",
      count: glosses.length,
      data: glosses
    });
  } catch (error) {
    console.error("Error getting glosses by token:", error);
    res.status(500).json({
      success: false,
      error: "Internal server error"
    });
  }
}

export async function handleGetGlossesByVerse(
  req: Request,
  res: Response
): Promise<void> {
  try {
    const { verseId } = req.params;
    const layer = req.query.layer as string | undefined;
    const verseIdNum = parseInt(verseId, 10);

    if (isNaN(verseIdNum)) {
      res.status(400).json({
        success: false,
        error: "Invalid verse ID"
      });
      return;
    }

    if (layer && !isValidLayer(layer)) {
      res.status(400).json({
        success: false,
        error: `Invalid layer. Must be one of: ${validLayers.join(", ")}`
      });
      return;
    }

    const glosses = await getGlossesByVerse(
      verseIdNum,
      layer as GlossLayer | undefined
    );

    res.json({
      success: true,
      verse_id: verseIdNum,
      layer: layer || "all",
      count: glosses.length,
      data: glosses
    });
  } catch (error) {
    console.error("Error getting glosses by verse:", error);
    res.status(500).json({
      success: false,
      error: "Internal server error"
    });
  }
}
