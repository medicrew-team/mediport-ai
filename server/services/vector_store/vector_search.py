import faiss
import json
import os
from sentence_transformers import SentenceTransformer
from server.config import BASE_DIR



EMBEDDING_MODEL_NAME = "jhgan/ko-sroberta-multitask"                        # 임베딩 모델
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "data/medicine_faiss.index")      # FAISS 인덱스 파일 경로
METADATA_JSON_PATH = os.path.join(BASE_DIR, "data/medicine_metadata.json")  # 메타데이터 JSON 경로


# 모델 로딩
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)

# 인덱스 로드
def load_faiss_index():
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(f"FAISS 인덱스 파일이 없습니다: {FAISS_INDEX_PATH}")
    return faiss.read_index(FAISS_INDEX_PATH)

# 메타데이터 로드
def load_metadata():
    if not os.path.exists(METADATA_JSON_PATH):
        raise FileNotFoundError(f"메타데이터 파일이 없습니다: {METADATA_JSON_PATH}")
    with open(METADATA_JSON_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

# 검색 함수
def search_similar_medicines(query: str, top_k: int = 1) -> list[dict]:
    index = load_faiss_index()
    metadata = load_metadata()

    # 질의 벡터화
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)

    # 유사도 검색
    distances, indices = index.search(query_embedding, top_k)

    # 증상과 가장 유사한 약 정보 추출
    results = []
    for idx in indices[0]:
        if idx < len(metadata):
            results.append(metadata[idx])

    return results


# ===== 테스트 코드 =====
if __name__ == "__main__":
    query = "머리가 아파요"
    result = search_similar_medicines(query)

    print(f"검색 결과:{result}")