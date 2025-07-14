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



def search_similar_medicines(query: str, top_k: int = 1) -> list[dict]:

    # 모델/인덱스/메타데이터가 아직 로딩 안됐으면 로딩
    if embedding_model is None or faiss_index is None or metadata is None:
        init_resources()

    # query_lower = query.lower().strip()
    #
    # # 문자열 우선 검색(제품명, 의약품 상호작용, 성분명)
    # exact_matches = []
    # for item in metadata:
    #     제품명 = item.get('제품명', '').lower()
    #     성분명 = item.get('성분명', '').lower()
    #     의약품_상호작용 = item.get('의약품 상호작용', '').lower()
    #
    #     if (query_lower in 제품명) or (query_lower in 성분명) or (query_lower in 의약품_상호작용):
    #         item_copy = item.copy()
    #         item_copy["score"] = 0.0  # 정확 매칭은 최고 우선순위
    #         exact_matches.append(item_copy)
    #
    # # 문자열 검색 결과가 있으면 바로 반환
    # if exact_matches:
    #     return exact_matches[:top_k]


    # partial_matches: 문자열로 직접 매칭된 약 정보들을 담는 리스트
    partial_matches = []

    for item in metadata:
        # 검색에 사용할 필드들 (제품명, 성분명, 병용금기약)
        searchable_fields = [
            item.get("제품명", ""),
            item.get("성분명", ""),
            item.get("의약품 상호작용", "")
        ]

        # 사용자의 질의(query)에 위 필드들 중 일부라도 정확히 포함되어 있는지 확인
        # ex) query = "트롤락주와 병용하면 안되는 약" → (제품명, 성분명, 병용금기약)중에 트롤락주 데이터가 있다면 매칭
        if any(field in query for field in searchable_fields if field):
            matched_item = item.copy()
            matched_item["score"] = 0
            partial_matches.append(matched_item)

    # 문자열 매칭된 결과가 있으면 벡터 검색은 스킵하고 바로 반환
    if partial_matches:
        return partial_matches[:top_k]


    # 문자열 검색 결과가 없을 경우, 벡터 유사도 검색으로 넘어감
    query_embedding = embedding_model.encode([query], normalize_embeddings=True, convert_to_numpy=True)     # 질의 벡터화
    distances, indices = faiss_index.search(query_embedding, top_k)                                         # 유사도 검색

    results = []
    for i, idx in enumerate(indices[0]):
        if idx < len(metadata):
            result = metadata[idx].copy()
            result["score"] = float(distances[0][i])
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