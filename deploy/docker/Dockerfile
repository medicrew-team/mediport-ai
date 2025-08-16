# CUDA 베이스 + Ubuntu 22.04
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# 기본 도구 + micromamba 추출에 필요한 bzip2
RUN apt-get update && apt-get install -y --no-install-recommends \
    bash curl ca-certificates git build-essential cmake bzip2 \
 && rm -rf /var/lib/apt/lists/*

# ── micromamba 단일 바이너리 설치 → /usr/local/bin
RUN curl -L https://micro.mamba.pm/api/micromamba/linux-64/latest \
  | tar -xvj -O bin/micromamba > /usr/local/bin/micromamba \
 && chmod +x /usr/local/bin/micromamba

# micromamba 루트(환경 저장 경로)
ENV MAMBA_ROOT_PREFIX=/opt/micromamba

# Python 3.12 환경 생성(+ pip)  ※ 절대경로 호출로 PATH 이슈 회피
RUN /usr/local/bin/micromamba create -y -n py312 -c conda-forge python=3.12 pip \
 && /usr/local/bin/micromamba clean -a -y

# 새 env를 기본 PATH로
ENV PATH=$MAMBA_ROOT_PREFIX/envs/py312/bin:$PATH
ENV CONDA_DEFAULT_ENV=py312
SHELL ["/bin/bash", "-lc"]

WORKDIR /app

# 프로젝트 요구사항(기존 requirements.txt 그대로 사용)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# GPU 의존 패키지: llama-cpp-python (CUDA 12.1 wheel 사용)
RUN pip install -U pip
RUN pip install --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cu121 \
    llama-cpp-python

# 코드 복사
COPY server/ ./server
COPY deploy/start.sh ./start.sh
COPY data/ ./data
COPY secrets/ ./secrets

# 모델 관련 ENV (RunPod에서 오버라이드 가능)
RUN mkdir -p /app/model
ENV LLM_GGUF_PATH=/app/model/llama-3-Korean-Bllossom-8B-Q4_K_M.gguf \
    LLM_CTX=2048 \
    LLM_N_GPU_LAYERS=40

EXPOSE 8000
RUN chmod +x start_runpod.sh
CMD ["./start.sh"]
