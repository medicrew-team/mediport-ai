from __future__ import annotations
import os
from typing import Optional
from llama_cpp import Llama

# ▶ GGUF 경로는 ENV로 주입(없으면 기본값)
LLM_GGUF_PATH = os.getenv(
    "LLM_GGUF_PATH",
    "/app/model/llama-3-Korean-Bllossom-8B-Q4_K_M.gguf",
)
LLM_CTX = int(os.getenv("LLM_CTX", "2048"))
LLM_N_GPU_LAYERS = int(os.getenv("LLM_N_GPU_LAYERS", "40"))
LLM_STOP = os.getenv("LLM_STOP", "</s>").split("|")

_llm: Optional[Llama] = None  # lazy singleton

def _get_llm() -> Llama:
    global _llm
    if _llm is None:
        if not os.path.exists(LLM_GGUF_PATH):
            raise FileNotFoundError(
                f"[inference_cloud] GGUF model not found: {LLM_GGUF_PATH}"
            )
        _llm = Llama(
            model_path=LLM_GGUF_PATH,
            n_ctx=LLM_CTX,
            n_gpu_layers=LLM_N_GPU_LAYERS,  # CUDA 빌드된 llama-cpp-python 필요
            verbose=False,
        )
    return _llm

def run(
    prompt: str,
    *,
    max_new_tokens: int = 512,
    temperature: float = 0.7,
    top_p: float = 0.9,
) -> str:
    """GGUF(llama.cpp) 기반 동기 추론"""
    llm = _get_llm()
    out = llm(
        prompt=prompt,
        max_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        stop=LLM_STOP,
    )
    return out["choices"][0]["text"].strip()
