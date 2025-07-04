import re


def preprocess_text(text: str) -> list:
    lines = text.split("\n")
    cleaned = [line.strip() for line in lines if line.strip()]

    # 예: 너무 짧은 숫자, 특수문자 제거 등
    filtered = [line for line in cleaned if re.search("[가-힣a-zA-Z]", line)]

    return filtered