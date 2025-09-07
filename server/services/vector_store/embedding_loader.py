from server.config import EMBEDDING_PROVIDER, OPENAI_API_KEY
from server.config import BASE_DIR

import openai
import numpy as np
import os


# ===== huggingface 임베딩 모델 =====
EMBEDDING_MODEL_NAME = "jhgan/ko-sroberta-multitask"                        # 임베딩 모델
# EMBEDDING_MODEL_NAME = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"              # 임베딩 모델
# EMBEDDING_MODEL_NAME = "BM-K/KoSimCSE-roberta-multitask"                  # 임베딩 모델
# EMBEDDING_MODEL_NAME = "nlpai-lab/KURE-v1"                                # 임베딩 모델
# EMBEDDING_MODEL_NAME = "nlpai-lab/KoE5"                                   # 임베딩 모델
# EMBEDDING_MODEL_NAME = "intfloat/multilingual-e5-large-instruct"          # 임베딩 모델
# EMBEDDING_MODEL_NAME = "dragonkue/BGE-m3-ko"                                # 임베딩 모델
# ===== huggingface 임베딩 모델 =====

# 사용자 정의 모델 경로
CUSTOM_MODEL_PATH = os.path.join(BASE_DIR, "models/med-embed-finetune")

if EMBEDDING_PROVIDER == "huggingface":
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer(CUSTOM_MODEL_PATH)
    def encode_texts(texts: list[str]) -> np.ndarray:
        return embedding_model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)

elif EMBEDDING_PROVIDER == "openai":
    openai.api_key = OPENAI_API_KEY
    OPENAI_EMBEDDING_MODEL = "text-embedding-3-large"
    EMBEDDING_DIM = 1536  # 또는 모델에 따라 다름 (e.g., 3072 for "large")

    def encode_texts(texts: list[str]) -> np.ndarray:
        import numpy as np
        import time

        embeddings = []
        for text in texts:
            while True:
                try:
                    res = openai.embeddings.create(
                        input=text,
                        model=OPENAI_EMBEDDING_MODEL
                    )
                    break
                except openai.RateLimitError:
                    time.sleep(1)

            embedding = res.data[0].embedding
            embeddings.append(embedding)

        return np.array(embeddings, dtype=np.float32)
