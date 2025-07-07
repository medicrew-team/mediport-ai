import os
import json
import faiss
from sentence_transformers import SentenceTransformer
from server.config import BASE_DIR



EMBEDDING_MODEL_NAME = "jhgan/ko-sroberta-multitask"                        # 임베딩 모델
DATASET_PATH = os.path.join(BASE_DIR, "data/medicine_dataset.json")         # 증상 기반 일반 의약품 추천 데이터셋 (JSON 파일 경로)
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "data/medicine_faiss.index")      # FAISS 인덱스 파일 경로
METADATA_JSON_PATH = os.path.join(BASE_DIR, "data/medicine_metadata.json")  # 메타데이터 JSON 경로


# ===== 모델 로딩 =====
embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)


# ===== FAISS 저장 함수 =====
def save_dataset_to_faiss(dataset: list[dict]):

    # 검색에 사용할 텍스트만 추출
    # texts = [item["text"] for item in dataset]

    # 임베딩 전 데이터 필드들을 문장으로 조립
    texts = [build_text_for_embedding(item) for item in dataset]

    # 텍스트 → 임베딩 벡터
    embeddings = embedding_model.encode(texts, convert_to_numpy=True)

    # FAISS 인덱스 생성
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    # 저장 경로 생성
    os.makedirs(os.path.dirname(FAISS_INDEX_PATH), exist_ok=True)

    # 인덱스 저장
    faiss.write_index(index, FAISS_INDEX_PATH)

    # 메타데이터 저장 (전체 정보)
    with open(METADATA_JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(dataset, f, ensure_ascii=False, indent=2)

    print(f"{len(texts)}개 약 정보 저장 완료")


# 임베딩 전 필드들을 문장으로 조립해주는 함수
def build_text_for_embedding(item: dict) -> str:

    # 필수 필드 체크
    required_fields = ['제품명', '성분명', 'ICD', '복용법', '주의사항']
    for field in required_fields:
        if not item.get(field):
            raise ValueError(f"필수 항목 누락: '{field}' 값이 없습니다.")

    return (
        f"{item.get('제품명', '')}은(는) "
        f"{item.get('성분명', '')} 성분을 포함한 일반의약품입니다. "
        f"사용되는 증상: {item.get('ICD', '')}. "
        f"복용법: {item.get('복용법', '')}. "
        f"주의사항: {item.get('주의사항', '')}."
    )


# ===== FAISS 저장 및 메타데이터 저장 실행 코드 =====
def load_dataset_from_json(json_path: str) -> list[dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    dataset = load_dataset_from_json(DATASET_PATH)
    save_dataset_to_faiss(dataset)