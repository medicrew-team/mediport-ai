# CUDA 베이스 + Ubuntu 22.04
FROM nvidia/cuda:12.1.1-devel-ubuntu22.04

# 기본 도구
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates bash git build-essential cmake \
    && rm -rf /var/lib/apt/lists/*


# micromamba 설치 (파이썬 3.12 환경 구성)
ENV MAMBA_ROOT_PREFIX=/opt/micromamba
RUN curl -L https://micro.mamba.pm/api/micromamba/linux-64/latest | bash -s -- -b -p $MAMBA_ROOT_PREFIX
SHELL ["/bin/bash", "-lc"]


# Python 3.12 생성 및 활성화
RUN micromamba create -y -n py312 python=3.12 && micromamba clean -a -y
ENV PATH=$MAMBA_ROOT_PREFIX/envs/py312/bin:$PATH
ENV CONDA_DEFAULT_ENV=py312

WORKDIR /app

#설치
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# GPU 의존 패키지만 Docker 빌드 레이어에서 덮어씌움
# llama-cpp-python: CUDA 빌드로 재설치
RUN (pip uninstall -y llama-cpp-python || true) && \
    CMAKE_ARGS="-DLLAMA_CUBLAS=on" FORCE_CMAKE=1 \
    pip install --no-cache-dir --no-binary :all: llama-cpp-python


# 배포에 필요한 코드 복사
COPY server/ ./server
COPY deploy/start.sh ./start.sh
COPY data/ ./data
COPY secrets/ ./secrets

# 모델 관련 기본 ENV
RUN mkdir -p /app/model
ENV LLM_GGUF_PATH=/app/model/llama-3-Korean-Bllossom-8B-Q4_K_M.gguf \
    LLM_CTX=2048 \
    LLM_N_GPU_LAYERS=40

EXPOSE 8000
RUN chmod +x start.sh
CMD ["./start.sh"]