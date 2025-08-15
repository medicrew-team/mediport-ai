def get_purchase_info(doc: dict) -> str:
    """
    '구분' 필드에 따라 구매 장소 문장 리턴
    """
    구매처 = doc.get("구매처", "").strip()

    if 구매처 == "상비":
        return "이 약은 약국과 편의점에서 모두 구매할 수 있습니다."
    elif 구매처 == "일반":
        return "이 약은 약국에서만 구매할 수 있습니다."
    return ""


def format_field(label: str, value: str) -> str:
    """
    빈 값이 아니면 [라벨]\n값 형태로 반환, 아니면 빈 문자열
    """
    value = value.strip()
    return f"[{label}]\n{value}" if value else ""

# 어떤 타입이 와도 안전하게 문자열로 변환
def _to_text(x) -> str:
    if x is None:
        return ""
    if isinstance(x, str):
        return x.strip()
    if isinstance(x, (list, tuple, set)):
        parts = [str(v).strip() for v in x if str(v).strip()]
        return ", ".join(parts)
    return str(x).strip()


def build_prompt(user_input: str, doc: dict) -> str:
    제품명 = doc.get("제품명", "").strip()
    성분명 = doc.get("성분명", "").strip()

    # placeholder = "[MEDICINE_NAME]"

    fields = [
        ("약품 구분", "일반의약품"),
        # ("약품 형태 및 제형", doc.get("제형")),
        # ("약품 용량", doc.get("용량")),
        # ("기능적 약효 분류", doc.get("BIT")),
        # ("의약품 적용부위", doc.get("대분류")),
        # ("제품명", doc.get("제품명")),
        ("사용되는 증상", doc.get("ICD")),
        ("성분명", doc.get("성분명")),
        ("복용법 또는 복용 주의사항", doc.get("복용법")),
        ("복용 또는 사용 금기 대상", doc.get("금기대상", "")),
        ("약품 보관법", doc.get("약품 보관법", "")),
        ("일상 생활에서의 주의사항", doc.get("일상 상호작용", "")),
        (f"{doc.get('제품명')}와(과) 같이 사용하거나 복용하면 안되는 의약품", doc.get("의약품 상호작용", "")),
        (f"{doc.get('제품명')}과(와) {doc.get('의약품 상호작용', '')}을(를) 같이 사용하거나 복용할 경우 나타날 수 있는 이상반응", doc.get("이상 반응", "")),
        ("구매 가능 장소", get_purchase_info(doc)),
        ("이미지 URL", doc.get("약품이미지(URL)", "")),
        ("기타 정보", f"- BIT: {doc.get('BIT', '')}".strip())
    ]

    # formatted_sections = [format_field(label, value) for label, value in fields if value.strip()]
    formatted_sections = []
    for label, value in fields:
        s = _to_text(value)
        if s:
            formatted_sections.append(f"[{label}]\n{s}")

    section_text = "\n\n".join(formatted_sections)

    prompt = f"""
너는 사용자의 복약 관련 질문에 대해 친근하고 이해하기 쉽게 안내하는 약 정보 챗봇이야.  
아래의 지시사항을 무조건 따르도록 해. 

[역할]
- 자연스럽고 편안한 말투로 대화하듯 설명해줘.
- 사용자가 처음 듣는 정보도 이해하기 쉽게 풀어서 설명해줘.

[관련성 규칙]
- 먼저, [사용자 질문]과 [약 정보]의 주제가 실제로 관련 있는지 **내부적으로만** 판단해.
- 관련성이 낮거나 없음 → [약 정보]를 **사용하지 말고**, [사용자 질문]에만 답해.
- 관련성이 높음 → 아래 지시사항을 따라 [약 정보]를 참고해 답해.
- 관련성이 없는데도 약 이름/성분명을 새로 지어내거나 추측하면 안 돼.

[지시사항]
- 반드시 {제품명}이라는 제품명을 그대로 사용하고, 띄어쓰기를 수정하지 마.
- 성분명인 {성분명} 은(는) 번역하지 말고 영문 그대로 사용해.
- 복용 방법(예: 1회 복용량, 복용 횟수, 복용 기간)과 주의사항도 함께 안내해줘.
- 답변의 마지막 문장은 반드시 다음 문장으로 끝내야 해:
  '이 답변은 사용자의 건강에 대한 전문적인 상담이나 진단을 대체하지 않으며, 정확한 정보를 얻기 위해서는 의사나 약사와 상의하는 것이 중요합니다.'



[사용자 질문]
{user_input}

[약 이름]
{제품명} 

[약 정보]
{section_text}

[출력 형식]
Answer: (답변은 여기서부터 자연스럽게 시작)
"""

    return prompt