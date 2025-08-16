#!/usr/bin/env bash
set -euo pipefail

# ===== 경로 설정 =====
APP_DIR="/home/ubuntu/mediport-ai"
VENV_DIR="$APP_DIR/.venv"         # 서버용 가상환경
PYTHON="python3"
APP_MODULE="server.main:app"      # uvicorn 모듈 경로

cd "$APP_DIR"

# ===== 0 스왑  =====
# 인덱싱 중 OOM 발생 방지
if ! swapon --show | grep -q swapfile; then
  echo "[start] creating 4G swapfile..."
  sudo fallocate -l 4G /swapfile || true
  sudo chmod 600 /swapfile || true
  sudo mkswap /swapfile || true
  sudo swapon /swapfile || true
  grep -q '/swapfile' /etc/fstab || echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab >/dev/null
fi

# ===== 1 가상환경 =====
if [ ! -d "$VENV_DIR" ]; then
  $PYTHON -m venv "$VENV_DIR"
fi
# shellcheck source=/dev/null
source "$VENV_DIR/bin/activate"

# ===== 2) 의존성 설치 (CPU 전용 Torch 먼저, 그 다음 나머지) =====
pip install --upgrade pip
pip cache purge || true

# 2-1) CPU 전용 PyTorch 고정 설치 (CUDA 휠 방지)
pip install --no-cache-dir --index-url https://download.pytorch.org/whl/cpu torch==2.7.1+cpu

# 2-2) requirements.txt에서 torch/torchvision/torchaudio 줄만 제외하고 설치
TMP_REQ="$(mktemp)"
trap 'rm -f "$TMP_REQ"' EXIT

# torch 류 줄(옵션/버전/엑스트라 포함)을 제외
# 예: torch==2.7.1, torch, torch[extra]==2.7.1, torchvision==0.17.*, torchaudio==*, 등
grep -Ev '^(torch|torchvision|torchaudio)(\[.*\])?(==.*)?$' "$APP_DIR/requirements.txt" > "$TMP_REQ"

# 나머지 패키지들은 의존성까지 정상적으로 설치
pip install --no-cache-dir -r "$TMP_REQ"

# ===== 3) 메모리 절약 환경 변수 =====
export OMP_NUM_THREADS=1
export MKL_NUM_THREADS=1
export TOKENIZERS_PARALLELISM=false

# ===== 4) FAISS 인덱스 항상 재생성 =====
echo "[start] Rebuilding FAISS index..."
PYTHONPATH="$APP_DIR" "$PYTHON" "$APP_DIR/server/services/vector_store/save_to_faiss.py"
echo "[start] FAISS index rebuild done."

# ===== 5) FastAPI 실행 =====
PORT="${PORT:-8000}"
exec "$VENV_DIR/bin/uvicorn" "$APP_MODULE" --host 0.0.0.0 --port "$PORT"
