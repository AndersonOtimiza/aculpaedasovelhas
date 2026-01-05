#!/usr/bin/env bash
TEXT="$1"
TARGET="$2"
ADAPTER="$3"

jq -nc --arg text "$TEXT" --arg target "$TARGET" --arg adapter "$ADAPTER" \
  '{text:$text, target:( $target|length>0 ? $target : "default"), adapter:( $adapter|length>0 ? $adapter : null)}' \
  | curl -s http://localhost:8090/command -H "Content-Type: application/json" -d @-
