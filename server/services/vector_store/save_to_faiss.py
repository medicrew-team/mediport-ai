import os
import json
import faiss
from sentence_transformers import SentenceTransformer
from server.config import BASE_DIR



EMBEDDING_MODEL_NAME = "jhgan/ko-sroberta-multitask"                        # 임베딩 모델
# EMBEDDING_MODEL_NAME = "snunlp/KR-SBERT-V40K-klueNLI-augSTS"              # 임베딩 모델
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
    embeddings = embedding_model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)

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

    # 필수 필드 체크 (주의사항은 build_warning_text()에서 체크)
    required_fields = ['제품명', '성분명', 'ICD', '복용법']
    for field in required_fields:
        if not item.get(field):
            raise ValueError(f"필수 항목 누락: '{field}' 값이 없습니다.")

    # 각 증상 문자열 뒤에 " 증상" 이라는 단어를 붙임
    icd_sentences = ', '.join([f"{s.strip()} 증상" for s in item.get('ICD', '').split(',')])


    return (
        f"이 약은 {item.get('제품명')}입니다. "
        f"{item.get('성분명', '')}이라는 성분을 포함하고 있으며, "
        f"{icd_sentences} 에 사용하거나 복용할 수 있습니다. "
        # f"복용법 또는 사용법은 다음과 같다: {item.get('복용법', '')}. "
        f"{build_warning_text(item)}"
    )


# 주의사항 문장 생성
def build_warning_text(item: dict) -> str:

    금기 = item.get("금기대상", "").strip()
    보관 = item.get("약품 보관법", "").strip()
    일상 = item.get("일상 상호작용", "").strip()
    의약품 = item.get("의약품 상호작용", "").strip() # 병행 금지 의약품


    # 의약품 상호작용 문장 생성
    names = [name.strip() for name in item.get('의약품 상호작용', '').split(',') if name.strip()]
    if names:
        joined_names = ', '.join(names)
        interaction_sentences = f"{item['제품명']}은(는) {joined_names}과(와) 병용해서 사용하거나 복용하면 안 됩니다."
    else:
        interaction_sentences = ''

    parts = []
    if 금기:
        parts.append(f"{금기}이신 분들은 이 약을 복용하시거나 사용하시면 안 됩니다.")
    if 보관:
        parts.append(f"이 약은 {보관}과(와) 같은 방법으로 보관해야 합니다.")
    if 일상:
        parts.append(f"일상 생활에서의 주의사항: {일상}")
    if 의약품:
        parts.append(interaction_sentences)

    if not parts:
        raise ValueError("주의사항 관련 데이터들이 모두 존재 하지 않습니다. 데이터 오류 확인 필요.")
    return ' '.join(parts)


# ===== FAISS 저장 및 메타데이터 저장 실행 코드 =====
def load_dataset_from_json(json_path: str) -> list[dict]:
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

if __name__ == "__main__":
    dataset = load_dataset_from_json(DATASET_PATH)
    save_dataset_to_faiss(dataset)