
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


def build_prompt(user_input: str, doc: dict) -> str:

    제품명 = doc.get("제품명", "").strip()
    # placeholder = "[MEDICINE_NAME]"

    fields = [
        ("약품 구분", "일반의약품"),
        # ("제품명", doc.get("제품명")),
        ("사용되는 증상", doc.get("ICD")),
        ("성분명", doc.get("성분명")),
        ("복용법", doc.get("복용법")),
        ("복용 또는 사용 금기 대상", doc.get("주의사항_금기대상", "")),
        ("약품 보관법", doc.get("약품 보관법", "")),
        ("일상 생활에서의 주의사항", doc.get("일상 상호작용", "")),
        (f"{doc.get('제품명')}와(과) 같이 사용하거나 복용하면 안되는 의약품", doc.get("의약품 상호작용", "")),
        (f"{doc.get('제품명')}과(와) {doc.get('의약품 상호작용', '')}을(를) 같이 사용하거나 복용할 경우 나타날 수 있는 이상반응", doc.get("이상 반응", "")),
        ("구매 가능 장소", get_purchase_info(doc)),
        ("이미지 URL", doc.get("약품이미지(URL)", "")),
        ("기타 정보", f"- BIT: {doc.get('BIT', '')}".strip())
    ]

    formatted_sections = [format_field(label, value) for label, value in fields if value.strip()]
    section_text = "\n\n".join(formatted_sections)

    prompt =  f"""당신은 외국인의 복약을 도와주는 약 정보 안내 챗봇입니다.
아래는 사용자의 증상에 맞는 약에 대한 상세 정보이며, 사용자의 질문에 친절하고 정확하게 답변해 주세요.
      
    
[사용자 질문]
{user_input}

         
[관련 약 이름]
"{제품명}"  # ⚠️ 중요: 이 약 이름은 문장 내에서 반드시 그대로 사용하세요. 절대 변경하거나 줄이지 마세요.

[약품 상세 정보들]
    {section_text}
    
답변:"""

    return prompt