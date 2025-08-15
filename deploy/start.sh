#!/usr/bin/env bash
set -euo pipefail

# ---- micromamba/py312 실행 경로 보장 ----
export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-/opt/micromamba}"
export PATH="${MAMBA_ROOT_PREFIX}/envs/py312/bin:${MAMBA_ROOT_PREFIX}/bin:${PATH}"
PY_BIN="${PY_BIN:-${MAMBA_ROOT_PREFIX}/envs/py312/bin/python}"

# ---- 모델 경로/리포 기본값 (RunPod ENV로 덮어쓰기 가능) ----
: "${LLM_GGUF_PATH:=/app/model/llama-3-Korean-Bllossom-8B-Q4_K_M.gguf}"
: "${LLM_MODEL_REPO:=MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M}"
: "${LLM_INCLUDE_PATTERN:=*.gguf}"

MODEL_DIR="$(dirname "$LLM_GGUF_PATH")"
mkdir -p "$MODEL_DIR"

# ---- GGUF 모델 다운로드(없을 때만) ----
if [ ! -f "$LLM_GGUF_PATH" ]; then
  echo "[start] 모델이 없습니다: $LLM_GGUF_PATH"

  # huggingface_hub 설치 (pip 대신 python -m pip 사용)
  "$PY_BIN" -m pip install -q -U huggingface_hub

  # 토큰 있으면 로그인 (없으면 건너뜀)
  if [ -n "${HUGGINGFACE_TOKEN:-}" ]; then
    echo "[start] Hugging Face 로그인..."
    huggingface-cli login --token "$HUGGINGFACE_TOKEN" --add-to-git-credential || true
  fi

  echo "[start] 모델 다운로드..."
  huggingface-cli download "$LLM_MODEL_REPO" \
    --include "$LLM_INCLUDE_PATTERN" \
    --local-dir "$MODEL_DIR"

  echo "[start] 모델 다운로드 완료."
else
  echo "[start] 모델 존재: $LLM_GGUF_PATH"
fi



# ===== FAISS 벡터 DB 준비 =====\
echo "FAISS 벡터 DB 저장 여부 확인 중..."

if [ ! -f "./data/medicine_faiss.index" ]; then
    echo "벡터 DB가 없어서 save_to_faiss.py 실행합니다."
    PYTHONPATH=./ python server/services/vector_store/save_to_faiss.py
else
    echo "벡터 DB가 이미 존재합니다. 그대로 서버 실행합니다."
fi


# Cloudflare Tunnel 실행 (백그라운드)
echo "Cloudflare Tunnel 실행 중..."
/workspace/bin/cloudflared tunnel --config /workspace/.cloudflared/config.yml run &

# FastAPI 서버 실행
echo "FastAPI 서버 실행 시작"
exec "$PY_BIN" -m uvicorn server.main:app --host 0.0.0.0 --port 8000
