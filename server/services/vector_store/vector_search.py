import faiss
import json
import os
import re

from sentence_transformers import SentenceTransformer
from server.config import BASE_DIR
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
from server.services.vector_store.embedding_loader import encode_texts



FAISS_INDEX_PATH = os.path.join(BASE_DIR, "data/medicine_faiss.index")      # FAISS 인덱스 파일 경로
METADATA_JSON_PATH = os.path.join(BASE_DIR, "data/medicine_metadata.json")  # 메타데이터 JSON 경로



# ===== 전역 리소스 (1회 로드) =====
embedding_model = None          # SentenceTransformer
faiss_index = None              # FAISS IndexFlatL2
metadata: List[Dict[str, Any]] = None

bm25_model: BM25Okapi | None = None
bm25_corpus_tokens: List[List[str]] | None = None
# ===============================


# RRF/부스팅 하이퍼파라미터(필요 시 여기서만 조정)
RRF_K = 60                # RRF 상수(10~60)
ICD_BOOST = 0.2           # ICD 키워드가 질의에 포함되면 가점(0.1~0.5)
BM25_CAND_FACTOR = 5      # 최종 top_k 대비 BM25 후보폭
FAISS_CAND_FACTOR = 5     # 최종 top_k 대비 FAISS 후보폭
MIN_BM25 = 1.0            # 검색 스킵 게이트: BM25 최소값
MIN_COS = 0.40            # 검색 스킵 게이트: 코사인 최소값(0.30~0.45 튜닝)
# ============================== #



# ==============================
# 유틸
# ==============================
def _tok(text: str) -> List[str]:
    """한/영/숫자만 추출하여 소문자 토큰화."""
    if not text:
        return []
    return re.findall(r"[가-힣A-Za-z0-9]+", text.lower())


def _clean_icd_string(icd: str) -> str:
    """ICD 필드에서 '증상' 제거 및 정리."""
    terms = []
    for s in icd.split(","):
        s = s.replace("증상", "").strip()
        if s:
            terms.append(s)
    return " ".join(terms)


def _icd_terms(meta: Dict[str, Any]) -> List[str]:
    """ICD + ICD_요약을 개별 토큰 리스트로 반환."""
    terms = []
    # if meta.get("ICD"):
    #     icd = meta.get("ICD", "") or ""
    #     terms.extend([t for t in (s.replace("증상", "").strip() for s in icd.split(",")) if t])
    if meta.get("ICD_요약"):
        terms.extend(_tok(meta["ICD_요약"]))  # 문장 토큰 단위로 확장

    return terms


def _rrf(rank: int) -> float:
    return 1.0 / (RRF_K + rank)


def _l2_to_cos(l2_dist: float) -> float:
    """
    정규화 임베딩 + IndexFlatL2 사용 시,
    코사인 유사도 ≈ 1 - (L2^2)/2  (faiss는 squared L2를 반환)
    """
    return 1.0 - (l2_dist / 2.0)


def _icd_summary(meta: Dict[str, Any]) -> str:
    return (meta.get("ICD_요약") or "").strip()

def _icd_text(meta: Dict[str, Any]) -> str:
    s = _icd_summary(meta)
    if s:
        return s
    # 요약이 없을 때만 기존 ICD 키워드 사용
    return _clean_icd_string(meta.get("ICD", "") or "")

def _icd_any_overlap(meta: Dict[str, Any], q_tokens: List[str]) -> bool:
    """질의 토큰과 해당 약의 ICD(요약/키워드) 토큰이 하나라도 겹치면 True."""
    icd_tokens = set(_tok(_icd_text(meta)))
    return bool(icd_tokens & set(q_tokens))


# ==============================
# 자원 초기화
# ==============================
def init_resources():

    """모델/인덱스/메타데이터/BM25를 처음 1회만 로딩."""
    global embedding_model, faiss_index, metadata, bm25_model, bm25_corpus_tokens

    # if embedding_model is None:
    #     try:
    #         embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
    #         print(f"[init] 모델 로딩 성공: {EMBEDDING_MODEL_NAME}")
    #     except Exception as e:
    #         raise RuntimeError(f"[init][에러] 모델 로딩 실패: {e}")

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


    # BM25 인덱스 (키워드 검색용)
    if bm25_model is None:
        bm25_corpus_tokens = []
        for item in metadata:
            icd_text = _icd_text(item)  # ICD_요약 우선, 없으면 ICD 키워드 정리본
            fields = " ".join([
                item.get("제품명", "") or "",
                icd_text,  # 의미의 중심
                icd_text,  # 부스팅 1 (중복 삽입로 가중)
                # item.get("성분명", "") or "",
                # item.get("의약품 상호작용", "") or "",
                # _clean_icd_string(item.get("ICD", "") or ""),
            ])
            bm25_corpus_tokens.append(_tok(fields))
        bm25_model = BM25Okapi(bm25_corpus_tokens)
        print("[init] BM25 인덱스 구축 완료")



# ==============================
# 검색
# ==============================
def search_similar_medicines(query: str, top_k: int = 1) -> List[Dict[str, Any]]:
    """
    하이브리드 검색:
      - BM25(키워드) + FAISS(임베딩) → RRF 결합
      - BM25/코사인이 모두 낮으면 검색 '스킵 게이트'로 문서 반환하지 않음
    반환: metadata dict + {"score": <fused_score>}
    """
    if embedding_model is None or faiss_index is None or metadata is None or bm25_model is None:
        init_resources()

    # A) 초단문 노이즈 차단
    q_tokens = _tok(query)
    if len("".join(q_tokens)) <= 1:
        return []

    # B) BM25 랭킹
    bm25_scores = bm25_model.get_scores(q_tokens)
    bm25_topN = max(50, top_k * BM25_CAND_FACTOR)
    bm25_ranked = sorted(range(len(bm25_scores)),
                         key=bm25_scores.__getitem__,
                         reverse=True)[:bm25_topN]


    print("=== BM25 검색 결과 (idx → 제품명, 점수) ===")
    for idx in bm25_ranked[:20]:
        if idx < len(metadata):
            print(f"[BM25 HIT] idx={idx}, 제품명={metadata[idx]['제품명']}, 점수={bm25_scores[idx]:.4f}")
        else:
            print(f"[BM25 HIT] idx={idx}, ( metadata 범위 초과)")
    print("===========================================")


    # C) FAISS 랭킹
    emb_topN = max(50, top_k * FAISS_CAND_FACTOR)
    # q_emb = embedding_model.encode([query], normalize_embeddings=True, convert_to_numpy=True)
    q_emb = encode_texts([query])
    distances, indices = faiss_index.search(q_emb, emb_topN)
    faiss_ranked = [int(i) for i in indices[0] if i < len(metadata)]

    print("=== FAISS 검색 결과 (idx → 제품명) ===")
    for idx in indices[0]:
        if idx < len(metadata):
            print(f"[FAISS HIT] idx={idx}, 제품명={metadata[idx]['제품명']}")
        else:
            print(f"[FAISS HIT] idx={idx}, ( metadata 범위 초과)")
    print("=======================================")


    # D) 검색 스킵 게이트: BM25/코사인이 모두 낮으면 반환 X
    bm25_best = float(max(bm25_scores)) if bm25_scores is not None and len(bm25_scores) else 0.0
    cos_best = 0.0
    if len(indices) and len(indices[0]):
        l2_best = float(distances[0][0])      # squared L2 (작을수록 두 벡터가 가깝다.)
        cos_best = _l2_to_cos(l2_best)        # L2 거리 → 코사인 유사도로 변환 (높을수록 가까움)
    if (bm25_best < MIN_BM25) and (cos_best < MIN_COS):
        return []

    # E) RRF 결합 + ICD 부스팅
    ranks_bm25 = {idx: r for r, idx in enumerate(bm25_ranked, start=1) if bm25_scores[idx] >= MIN_BM25}
    ranks_faiss = {idx: r for r, idx in enumerate(faiss_ranked, start=1)}
    candidates = set(bm25_ranked) | set(faiss_ranked)
    if not candidates:
        return []

    fused_scores: Dict[int, float] = {}
    for idx in candidates:
        s = 0.0
        if idx in ranks_bm25:
            s += _rrf(ranks_bm25[idx])
        if idx in ranks_faiss:
            s += _rrf(ranks_faiss[idx])

        # ICD 정확 키워드 포함 시 가점(강제 추천 제거)
        for term in _icd_terms(metadata[idx]):
            if term and term in query:
                s += ICD_BOOST
                break

        fused_scores[idx] = s

    top_indices = sorted(candidates, key=lambda i: fused_scores[i], reverse=True)[:top_k]

    results: List[Dict[str, Any]] = []
    for i in top_indices:
        rec = metadata[i].copy()
        rec["score"] = round(fused_scores[i], 6)
        results.append(rec)

    return results
