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
    texts = [item["text"] for item in dataset]

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



# ===== 실행용 =====
def load_dataset_from_json(json_path: str) -> list[dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    dataset = load_dataset_from_json(DATASET_PATH)
    save_dataset_to_faiss(dataset)