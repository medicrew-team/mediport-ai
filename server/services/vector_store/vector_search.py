import faiss
import json
import os
from sentence_transformers import SentenceTransformer
from server.config import BASE_DIR



EMBEDDING_MODEL_NAME = "jhgan/ko-sroberta-multitask"                        # 임베딩 모델
# EMBEDDING_MODEL_NAME = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"              # 임베딩 모델
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "data/medicine_faiss.index")      # FAISS 인덱스 파일 경로
METADATA_JSON_PATH = os.path.join(BASE_DIR, "data/medicine_metadata.json")  # 메타데이터 JSON 경로


# 모듈 불러올 때 한 번만 로딩
embedding_model = None
faiss_index = None
metadata = None


# ===== 자원 초기화 함수 =====
def init_resources():
    """모델, 인덱스, 메타데이터를 처음 1회만 로딩"""
    global embedding_model, faiss_index, metadata

    if embedding_model is None:
        try:
            embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            print(f"[init] 모델 로딩 성공: {EMBEDDING_MODEL_NAME}")
        except Exception as e:
            raise RuntimeError(f"[init][에러] 모델 로딩 실패: {e}")

    if faiss_index is None:
        if not os.path.exists(FAISS_INDEX_PATH):
            raise FileNotFoundError(f"[init] FAISS 인덱스 파일 없음: {FAISS_INDEX_PATH}")
        try:
            faiss_index = faiss.read_index(FAISS_INDEX_PATH)
            print("[init] FAISS 인덱스 로딩 완료")
        except Exception as e:
            raise RuntimeError(f"[init][에러] FAISS 인덱스 로딩 실패: {e}")

    if metadata is None:
        if not os.path.exists(METADATA_JSON_PATH):
            raise FileNotFoundError(f"[init] 메타데이터 파일 없음: {METADATA_JSON_PATH}")
        try:
            with open(METADATA_JSON_PATH, "r", encoding="utf-8") as f:
                metadata = json.load(f)
            print(f"[init] 메타데이터 로딩 완료 (총 {len(metadata)}개)")
        except Exception as e:
            raise RuntimeError(f"[init][에러] 메타데이터 로딩 실패: {e}")



# 검색 함수
def search_similar_medicines(query: str, top_k: int = 1) -> list[dict]:

    # 모델/인덱스/메타데이터가 아직 로딩 안됐으면 로딩
    if embedding_model is None or faiss_index is None or metadata is None:
        init_resources()


    # 질의 벡터화
    query_embedding = embedding_model.encode([query], convert_to_numpy=True)

    # 유사도 검색
    distances, indices = faiss_index.search(query_embedding, top_k)

    # 증상과 가장 유사한 약 정보 추출
    results = []
    for i, idx in enumerate(indices[0]):  # indices[0] -> # 첫 번째 질의에 대한 top_k개 결과의 인덱스 리스트
        if idx < len(metadata):
            result = metadata[idx].copy()  # 원본 변형 방지
            result["score"] = float(distances[0][i]) # 유사도 점수 추가(distances[0] -> 각 인덱스에 대한 거리)
            results.append(result)

    return results


# ===== 테스트 코드 =====
# if __name__ == "__main__":
#
#     # 자원 미리 로딩
#     init_resources()
#
#     query = "머리가 너무 아픈데 어떤 약을 먹어야 할까?"
#     result = search_similar_medicines(query)
#
#     print(f"검색 결과:{result}")
#
#     for i, res in enumerate(result):
#         print(f"- 유사도 점수: {res['score']}")