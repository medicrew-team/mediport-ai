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
    m = re.search(
        r"(\d+\.?\d*)\s*(?:정|포|병)\s*씩\s*(\d+)\s*회\s*(\d+)\s*일\s*분",
        text
    )
    if m:
        return m.groups()
    return None


def _median(vals):
    """중앙값 계산 (줄 간격용)."""
    vals = sorted(vals)
    n = len(vals)
    if n == 0: return 0.0
    return vals[n//2] if n % 2 else (vals[n//2-1] + vals[n//2]) / 2.0


def map_medicines_to_dosages(
    words: List[Dict[str, Any]],
    known_medicine_names: List[str],
    *,
    line_gap_px: float = 16.0,
    band_factor: float = 0.6,
    require_right_on_same_line: bool = True
) -> Dict[str, Dict[str, str]]:

    # 단어 높이 중앙값 기준 줄 간격 계산
    heights = [(max(y for _, y in w["bounding_box"]) - min(y for _, y in w["bounding_box"])) for w in words]
    median_h = _median(heights) or 1.0
    GAP = max(line_gap_px, median_h * band_factor)

    # 줄 단위 묶기
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

    # 줄별 약명 유사 토큰만 사용해서 line_texts, line_norms 구성
    line_texts: List[str] = []
    line_norms: List[str] = []
    filtered_lines: List[List[Dict[str, Any]]] = []

    for line in lines:
        line.sort(key=lambda w: w["x_center"])

        norm_words = [
            w for w in line
            if any(_is_token_of_med(w["text"], med) for med in known_medicine_names)
        ]

        if norm_words:
            text = "".join(w["text"] for w in norm_words)
            norm_text = _norm(text)

            line_texts.append(text)
            line_norms.append(norm_text)
            filtered_lines.append(line)  # 약명이 들어있는 줄만 따로 저장
        else:
            continue

    # 최종 결과 저장
    final_result = {}
    for med in known_medicine_names:
        norm_med = _norm(med)
        if not norm_med:
            continue

        idx = None
        for i, norm in enumerate(line_norms):
            # 원래대로 부분일치 허용 (기존 동작 보존)
            if norm_med in norm:
                idx = i
                break

        m = None
        if idx is not None:
            same_line = filtered_lines[idx]
            same_text = line_texts[idx]

            if require_right_on_same_line:
                # 슬라이딩 윈도우 + 단일 토큰 대응
                med_tokens = []

                for i in range(len(same_line)):
                    for j in range(i + 1, len(same_line) + 1):
                        chunk_tokens = same_line[i:j]
                        chunk_text = "".join(w["text"] for w in chunk_tokens)
                        if _norm(chunk_text) == norm_med:
                            med_tokens = chunk_tokens
                            break
                    if med_tokens:
                        break

                if not med_tokens:
                    med_tokens = [w for w in same_line if _is_token_of_med(w["text"], med)]

                if med_tokens:
                    med_xs = sorted(w["x_center"] for w in med_tokens)
                    med_x = med_xs[len(med_xs) // 2]
                    right_text = "".join(w["text"] for w in same_line if w["x_center"] > med_x)
                    m = _match_dosage(right_text)
                else:
                    m = _match_dosage(same_text)
            else:
                m = _match_dosage(same_text)

        final_result[med] = {
            "투약량": m[0] if m else None,
            "횟수": m[1] if m else None,
            "일수": m[2] if m else None
        }

    return final_result
