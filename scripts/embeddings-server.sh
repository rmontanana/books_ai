#!/usr/bin/env bash
# Levanta el Modelo de Embeddings en llama-server, dentro de un toolbox.
#
# El Modo Consulta habla con el por HTTP y nunca lo carga en proceso: por eso el
# servicio vive aqui, en el stack de llama.cpp, y no entre las dependencias de
# Python (ADR-0003).
#
# Uso:  scripts/embeddings-server.sh [puerto]
set -euo pipefail

TOOLBOX="${BOOKS_AI_TOOLBOX:-llama-vulkan-radv}"
MODELO="${BOOKS_AI_EMBEDDINGS_GGUF:-$HOME/Code/models/bge-m3-GGUF/bge-m3-FP16.gguf}"
PUERTO="${1:-8081}"

# Loopback a proposito: llama-server no lleva autenticacion, y `toolbox run`
# comparte la red del anfitrion, asi que 127.0.0.1 ya se alcanza desde el host.
# Quien es publico en la LAN es el backend del ticket 07, no esto.
HOST="${BOOKS_AI_EMBEDDINGS_HOST:-127.0.0.1}"

# BGE-M3 agrupa por el token CLS: con --pooling mean o none los vectores no son
# los que el modelo fue entrenado para dar. Con none, ademas, llama-server
# devuelve un vector por token y el cliente lo rechaza.
POOLING="${BOOKS_AI_EMBEDDINGS_POOLING:-cls}"

# BGE-M3 admite 8192 tokens de contexto. El ubatch tiene que llegar al contexto
# entero o llama-server trocea la secuencia y el pooling deja de ser el del CLS.
CONTEXTO="${BOOKS_AI_EMBEDDINGS_CTX:-8192}"

if [[ ! -f "$MODELO" ]]; then
  echo "No esta el Modelo de Embeddings en $MODELO" >&2
  echo "Descargalo con:" >&2
  echo "  hf download gpustack/bge-m3-GGUF bge-m3-FP16.gguf \\" >&2
  echo "     --local-dir \"\$HOME/Code/models/bge-m3-GGUF\"" >&2
  exit 1
fi

exec toolbox run -c "$TOOLBOX" llama-server \
  --model "$MODELO" \
  --embeddings \
  --pooling "$POOLING" \
  --ctx-size "$CONTEXTO" \
  --ubatch-size "$CONTEXTO" \
  --host "$HOST" \
  --port "$PUERTO" \
  --no-webui
