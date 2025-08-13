# 목적: 같은 줄(X축)일 때만 약명 - 복약정보를 매핑. 아래 줄 보조 탐색 없음.

import re
from typing import List, Dict, Any, Tuple


def _norm(s: str) -> str:
    """약/기호/공백을 날리고 한글/영문/숫자만 남긴다 (간단 정규화)."""
    return re.sub(r"[^가-힣A-Za-z0-9]", "", s or "")


def _is_token_of_med(token_text: str, med: str) -> bool:
    """유사도 없이 ‘포함’만 허용: 토큰⊂약명 또는 약명⊂토큰 이면 같은 글자로 본다."""
    t, m = _norm(token_text), _norm(med)
    if not t or not m:
        return False
    return (t in m) or (m in t)


def _match_dosage(text: str):
    """복약정보 정규식: 붙여쓰기/띄어쓰기 다양성 대응."""
    m = re.search(r"(\d+\.?\d*)\s*정\s*씩\s*(\d+)\s*회\s*(\d+)\s*일\s*분", text)
    if m: return m.groups()
    m = re.search(r"(\d+\.?\d*)정\s*씩\s*(\d+)회\s*(\d+)일\s*분", text)
    if m: return m.groups()
    m = re.search(r"(\d+\.?\d*)정씩(\d+)회(\d+)일분", text)
    if m: return m.groups()
    return None



# def map_medicines_to_dosages(
#     words: List[Dict[str, Any]],
#     known_medicine_names: List[str],
#     *,
#     line_merge_thresh: int = 16,   # 같은 줄로 묶는 y경계 여유(px)
#     band_factor: float = 0.6,
#     require_right_on_same_line: bool = True  # 같은 줄에서 약명 오른쪽만 볼지 여부
# ) -> Dict[str, Dict[str, str]]:
#
#     """
#     같은 줄(X축)일 때만 매핑한다.
#     - 줄 묶기: bounding box 상·하 경계 겹침 기준
#     - 약명은 ‘정규화 후 포함’으로 같은 줄 판단(유사도 X)
#     - 복약정보는 같은 줄에서만 추출, 없으면 None 유지 (아래 줄 보조 탐색 없음)
#     - (옵션) 같은 줄 안에서도 약명보다 오른쪽(x 큰)만 본다
#     """
#
#     # 1) 줄 묶기 (상·하 경계 겹침)
#     lines: List[List[Dict[str, Any]]] = []
#     for w in sorted(words, key=lambda x: x["y_center"]):
#         y_vals = [yy for _, yy in w["bounding_box"]]
#         y_min, y_max = min(y_vals), max(y_vals)
#
#         placed = False
#         for line in lines:
#             ref_y = [yy for _, yy in line[0]["bounding_box"]]
#             ref_min, ref_max = min(ref_y), max(ref_y)
#             if y_max >= (ref_min - line_merge_thresh) and y_min <= (ref_max + line_merge_thresh):
#                 line.append(w)
#                 placed = True
#                 break
#         if not placed:
#             lines.append([w])
#
#     # 각 줄을 x 오름차순으로 정렬 + 줄 텍스트/정규화 텍스트 준비
#     line_texts: List[str] = []
#     line_norms:  List[str] = []
#     for line in lines:
#         line.sort(key=lambda w: w["x_center"])
#         text = "".join(w["text"] for w in line)
#         line_texts.append(text)
#         line_norms.append(_norm(text))
#
#     # 2) 결과 초기화
#     result = {med: {"투약량": None, "횟수": None, "일수": None} for med in known_medicine_names}
#
#     # 3) 약명별로 같은 줄에서만 복약정보 찾기
#     for med in known_medicine_names:
#         norm_med = _norm(med)
#         if not norm_med:
#             continue
#
#         # 3-1) 약명이 포함된 줄 찾기 (정확 포함만; 유사도 X)
#         idx = None
#         for i, norm in enumerate(line_norms):
#             if norm_med in norm or norm in norm_med:
#                 idx = i
#                 break
#         if idx is None:
#             # 같은 줄 자체를 못 찾았으면 이 약은 None 유지
#             continue
#
#         same_line = lines[idx]
#         same_text = line_texts[idx]
#
#         # 3-2) 같은 줄에서도 "약명 오른쪽만" 볼지 결정
#         if require_right_on_same_line:
#             # 약명의 대략적인 x 기준: 약명 토큰들의 x 중앙값(토큰⊂약명/약명⊂토큰 허용)
#             med_tokens = [w for w in same_line if _is_token_of_med(w["text"], med)]
#             if med_tokens:
#                 med_x = sorted(w["x_center"] for w in med_tokens)
#                 med_x = med_x[len(med_x)//2]  # 중앙값
#                 right_text = "".join(w["text"] for w in same_line if w["x_center"] > med_x)
#             else:
#                 # 약명 토큰을 줄에서 못 찾으면 줄 전체를 사용(보수적으로)
#                 right_text = same_text
#
#             m = _match_dosage(right_text)
#         else:
#             m = _match_dosage(same_text)
#
#         if m:
#             result[med] = {"투약량": m[0], "횟수": m[1], "일수": m[2]}
#         # 못 찾으면 그대로 None
#
#     return result


def _median(vals):
    vals = sorted(vals)
    n = len(vals)
    if n == 0: return 0.0
    return vals[n//2] if n % 2 else (vals[n//2-1] + vals[n//2]) / 2.0



def map_medicines_to_dosages(
    words: List[Dict[str, Any]],
    known_medicine_names: List[str],
    *,
    line_gap_px: float = 16.0,     # 최소 줄 간격 임계치(px) — 사진에 따라 14~24에서 튜닝
    band_factor: float = 0.6,      # 단어 높이 기반 여유 비율(0.5~0.8 권장)
    require_right_on_same_line: bool = True  # 같은 줄에서 약명 오른쪽만 볼지
) -> Dict[str, Dict[str, str]]:
    """
    같은 줄(X축)일 때만 매핑. 줄 묶기는 'y 중앙값 기준의 간격 임계치'로 엄격하게.
    다른 줄/아래 줄은 절대 보지 않음.
    """

    # 0) 단어 높이의 중앙값으로 대략적인 줄 높이 추정
    heights = [(max(y for _, y in w["bounding_box"]) - min(y for _, y in w["bounding_box"])) for w in words]
    median_h = _median(heights) or 1.0
    GAP = max(line_gap_px, median_h * band_factor)  # <- 이 값으로 줄 분리 민감도 조절

    # 1) 줄 묶기: y_center 오름차순으로 훑으며, 현재 줄 중앙값과의 차이가 크면 새 줄 시작
    words_sorted = sorted(words, key=lambda w: w["y_center"])
    lines: List[List[Dict[str, Any]]] = []
    cur: List[Dict[str, Any]] = []
    cur_y_vals: List[float] = []

    for w in words_sorted:
        if not cur:
            cur = [w]
            cur_y_vals = [w["y_center"]]
            continue

        y_med = _median(cur_y_vals)
        if abs(w["y_center"] - y_med) <= GAP:
            cur.append(w)
            cur_y_vals.append(w["y_center"])
        else:
            lines.append(cur)
            cur = [w]
            cur_y_vals = [w["y_center"]]
    if cur:
        lines.append(cur)

    # 2) 줄별 x 정렬 + 텍스트 합치기
    line_texts: List[str] = []
    line_norms:  List[str] = []
    for line in lines:
        line.sort(key=lambda w: w["x_center"])
        text = "".join(w["text"] for w in line)
        line_texts.append(text)
        line_norms.append(_norm(text))

    # 3) 결과 초기화
    result = {med: {"투약량": None, "횟수": None, "일수": None} for med in known_medicine_names}

    # 4) 약명별로, 같은 줄에서만 복약정보 추출
    for med in known_medicine_names:
        norm_med = _norm(med)
        if not norm_med:
            continue

        # 4-1) 약명이 들어있는 줄 찾기
        idx = None
        for i, norm in enumerate(line_norms):
            if norm_med in norm or norm in norm_med:
                idx = i
                break
        if idx is None:
            continue  # 줄 자체가 잘못 묶였거나 약명 인식 실패

        same_line = lines[idx]
        same_text = line_texts[idx]

        # 4-2) 같은 줄에서도 약명 오른쪽만 볼지
        if require_right_on_same_line:
            med_tokens = [w for w in same_line if _is_token_of_med(w["text"], med)]
            if med_tokens:
                med_xs = sorted(w["x_center"] for w in med_tokens)
                med_x = med_xs[len(med_xs)//2]
                right_text = "".join(w["text"] for w in same_line if w["x_center"] > med_x)
                m = _match_dosage(right_text)
            else:
                m = _match_dosage(same_text)
        else:
            m = _match_dosage(same_text)

        if m:
            result[med] = {"투약량": m[0], "횟수": m[1], "일수": m[2]}

    return result