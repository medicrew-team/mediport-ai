import json
import os
from server.config import BASE_DIR
import re


# 국내 약명 데이터셋 경로
MEDICINE_DATASET_PATH = os.path.join(BASE_DIR, "data/korean_product_name.json")

# 모국 약명 데이터셋 경로
FOREIGN_MEDICINE_DATASET_PATH = os.path.join(BASE_DIR, "data/foreign_product_name.json")


# 국내 약명 리스트 로드
def load_medicine_names() -> list:
    with open(MEDICINE_DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [item["제품명"].strip() for item in data if "제품명" in item]



# 모국 약명 리스트 로드
def load_foreign_medicine_names() -> list:
    with open(FOREIGN_MEDICINE_DATASET_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    return [item["제품명"].strip() for item in data if "제품명" in item]



# 텍스트에서 국내 약명 추출
def extract_medicine_names_from_text(text: str) -> list:

    medicine_names = load_medicine_names()

    if not text:
        return []

    extracted = []

    for name in medicine_names:

        # 빠른 필터: 공백 허용 + 단어 경계 만족하는지 체크
        if not _contains_token_allowing_spaces(text, name):
            continue

        # 정규식 기반 등장 횟수 수집
        pattern = _token_pattern(name)
        matches = list(pattern.finditer(text or ""))

        if matches:
            extracted.extend([name] * len(matches))

    return extracted


# 텍스트에서 모국 약명 추출
def extract_foreign_medicine_names_from_text(text: str) -> list:

    foreign_names = load_foreign_medicine_names()

    if not text:
        return []

    text_norm = text.lower().replace(" ", "")

    extracted = []

    for name in foreign_names:
        name_norm = name.lower().replace(" ", "")
        if _contains_token_allowing_spaces(text_norm, name_norm):
            extracted.append(name)

    return extracted



def _contains_token_allowing_spaces(text: str, token: str) -> bool:
    """
    text 안에 token이 '정확한 단어'로 존재하는지 검사하되,
    token 내부에는 임의의 공백/개행(\s*)이 끼어도 허용한다.

    예: token=닥터베아제정
      - '닥터베아제정'        → 매칭
      - '닥터 베아제정'       → 매칭 (공백 허용)
      - '닥 터  베 아 제 정'  → 매칭 (여러 공백/개행 허용)
      - '닥터베아제정정제형'  → 매칭 (뒤는 설명어. 다음 약명과 충돌 방지용 경계는 아래 짧은 토큰 쪽에서 막힘)
      - '베아제정'(부분문자열) → 단독일 때만 매칭. '닥터베아제정' 안에 끼인 경우는
                                '베'(앞)가 한글/영문/숫자와 붙어 있어 경계에 걸려서 불일치.

    경계 조건:
      (?<![가-힣A-Za-z0-9])  token 앞 문자가 '문자/숫자'가 아니어야 함
      (?![가-힣A-Za-z0-9])   token 뒤 문자가 '문자/숫자'가 아니어야 함
    """

    if not text or not token:
        return False

    # 토큰의 각 글자 사이에 \s* 허용 (공백/개행 허용)
    body = r"\s*".join(map(re.escape, token))
    pattern = rf"(?<![가-힣A-Za-z0-9]){body}(?![가-힣A-Za-z0-9])"

    return re.search(pattern, text, flags=re.IGNORECASE) is not None



# 약명 → 공백/개행 허용 + 단어 경계 정규식
def _token_pattern(token: str) -> re.Pattern:
    # 글자 사이에 \s* 허용, 앞뒤는 한글/영문/숫자와 붙지 않게 경계 지정
    body = r"\s*".join(map(re.escape, token))
    pat  = rf"(?<![가-힣A-Za-z0-9]){body}(?![가-힣A-Za-z0-9])"
    return re.compile(pat, re.IGNORECASE)