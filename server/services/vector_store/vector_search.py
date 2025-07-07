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
    for i, idx in enumerate(indices[0]):  # indices[0] -> # 첫 번째 질의에 대한 top_k개 결과의 인덱스 리스트
        if idx < len(metadata):
            result = metadata[idx].copy()  # 원본 변형 방지
            result["score"] = float(distances[0][i]) # 유사도 점수 추가(distances[0] -> 각 인덱스에 대한 거리)
            results.append(result)

    return results


# ===== 테스트 코드 =====
if __name__ == "__main__":
    query = "머리가 아파요"
    result = search_similar_medicines(query)

    print(f"검색 결과:{result}")

    for i, res in enumerate(result):
        print(f"- 유사도 점수: {res['score']}")