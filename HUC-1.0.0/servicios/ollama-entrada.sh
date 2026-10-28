#!/bin/sh
set -eu
modelo="${OLLAMA_MODEL:-qwen3:4b-instruct-2507-q4_K_M}"
ollama serve &
servidor=$!
hasta=0
until ollama list >/dev/null 2>&1; do
  hasta=$((hasta + 1))
  if [ "$hasta" -gt 60 ]; then
    echo "Ollama no respondió." >&2
    exit 1
  fi
  sleep 2
done
if ! ollama list | grep -q "$modelo"; then
  ollama pull "$modelo"
fi
wait "$servidor"
