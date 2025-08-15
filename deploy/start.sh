#!/usr/bin/env bash
set -euo pipefail

# -------------------------
# 0) micromamba/py312 경로 보장
# -------------------------
export MAMBA_ROOT_PREFIX="${MAMBA_ROOT_PREFIX:-/opt/micromamba}"
export PATH="${MAMBA_ROOT_PREFIX}/envs/py312/bin:${MAMBA_ROOT_PREFIX}/bin:${PATH}"
PY_BIN="${PY_BIN:-${MAMBA_ROOT_PREFIX}/envs/py312/bin/python}"

echo "[start] Python: $("$PY_BIN" -V 2>&1)"

# -------------------------
# 1) GPU 감지 → llama-cpp-python 런타임 폴백
# -------------------------
if command -v nvidia-smi >/dev/null 2>&1 && nvidia-smi -L >/dev/null 2>&1; then
  echo "[start] GPU 감지됨 → CUDA wheel 사용"
  : "${LLM_N_GPU_LAYERS:=40}"
else
  echo "[start] GPU 미감지 → CPU wheel로 전환"
  "$PY_BIN" -m pip install -q -U pip
  "$PY_BIN" -m pip install -q --force-reinstall --no-cache-dir llama-cpp-python
  export LLM_N_GPU_LAYERS=0
fi

# -------------------------
# 2) 모델 경로/리포 기본값
#    (/workspace 유지: 모델을 영구 보관)
# -------------------------
: "${LLM_GGUF_PATH:=/workspace/model/llama-3-Korean-Bllossom-8B-Q4_K_M.gguf}"
: "${LLM_MODEL_REPO:=MLP-KTLim/llama-3-Korean-Bllossom-8B-gguf-Q4_K_M}"
: "${LLM_INCLUDE_PATTERN:=*.gguf}"

# 앱 프로세스가 보게 환경변수로 내보내기
export LLM_GGUF_PATH LLM_MODEL_REPO LLM_INCLUDE_PATTERN LLM_N_GPU_LAYERS LLM_CTX

MODEL_DIR="$(dirname "$LLM_GGUF_PATH")"
mkdir -p "$MODEL_DIR"

# -------------------------
# 3) GGUF 모델 다운로드(없을 때만)
#    - 우선: huggingface-cli download
#    - 실패 시: Python API snapshot_download 폴백
# -------------------------
if [ ! -f "$LLM_GGUF_PATH" ]; then
  echo "[start] 모델이 없습니다: $LLM_GGUF_PATH"

  "$PY_BIN" -m pip install -q -U huggingface_hub

  if [ -n "${HUGGINGFACE_TOKEN:-}" ]; then
    echo "[start] Hugging Face 로그인..."
    huggingface-cli login --token "$HUGGINGFACE_TOKEN" --add-to-git-credential || true
  fi

  HF_CACHE_DIR="$MODEL_DIR/.hf_cache"
  mkdir -p "$HF_CACHE_DIR"

  echo "[start] 모델 다운로드 시도 (huggingface-cli download)..."
  set +e
  huggingface-cli download "$LLM_MODEL_REPO" \
    --include "$LLM_INCLUDE_PATTERN" \
    --local-dir "$MODEL_DIR"
  HF_CLI_RC=$?
  set -e

  if [ $HF_CLI_RC -ne 0 ]; then
    echo "[start] CLI 다운로드 실패 → Python API(snapshot_download)로 폴백"
    "$PY_BIN" - <<'PY'
import os
from huggingface_hub import snapshot_download

repo = os.environ["LLM_MODEL_REPO"]
local_dir = os.environ["MODEL_DIR"]
cache_dir = os.path.join(local_dir, ".hf_cache")
patterns = os.environ.get("LLM_INCLUDE_PATTERN", "*.gguf")

# 여러 패턴 지원 (패턴을 '|' 로 구분해서 전달 가능)
allow_patterns = [p.strip() for p in patterns.split("|") if p.strip()]

snapshot_download(
    repo_id=repo,
    cache_dir=cache_dir,
    local_dir=local_dir,
    local_dir_use_symlinks=False,
    allow_patterns=allow_patterns,
    resume_download=True,
    max_workers=4,
)
PY
  fi

  rm -rf "$HF_CACHE_DIR" || true
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
