
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
    성분명 = doc.get("성분명", "").strip()

    # placeholder = "[MEDICINE_NAME]"

    fields = [
        ("약품 구분", "일반의약품"),
        # ("제품명", doc.get("제품명")),
        ("사용되는 증상", doc.get("ICD")),
        ("성분명", doc.get("성분명")),
        ("복용법 또는 복용 주의사항", doc.get("복용법")),
        ("복용 또는 사용 금기 대상", doc.get("주의사항_금기대상", "")),
        ("약품 보관법", doc.get("약품 보관법", "") ),
        ("일상 생활에서의 주의사항", doc.get("일상 상호작용", "")),
        (f"{doc.get('제품명')}와(과) 같이 사용하거나 복용하면 안되는 의약품", doc.get("의약품 상호작용", "")),
        (f"{doc.get('제품명')}과(와) {doc.get('의약품 상호작용', '')}을(를) 같이 사용하거나 복용할 경우 나타날 수 있는 이상반응", doc.get("이상 반응", "")),
        ("구매 가능 장소", get_purchase_info(doc)),
        ("이미지 URL", doc.get("약품이미지(URL)", "")),
        ("기타 정보", f"- BIT: {doc.get('BIT', '')}".strip())
    ]

    formatted_sections = [format_field(label, value) for label, value in fields if value.strip()]
    section_text = "\n\n".join(formatted_sections)

    prompt =  f"""
너는 사용자의 복약 관련 질문에 대해 정중하고 간결하게 응답하는 약 정보 안내 챗봇이야.  
아래의 지시사항을 무조건 따르도록 해. 

[지시사항]
- 답변은 맨 아래 'Answer:' 구간에 단 한 번만 출력한다.
- 답변 마지막 문장은 반드시 다음 문장으로 끝내야 한다:
  '이 답변은 사용자의 건강에 대한 전문적인 상담이나 진단을 대체하지 않으며, 정확한 정보를 얻기 위해서는 의사나 약사와 상의하는 것이 중요합니다.'
- 그 이후에는 어떤 텍스트도 생성하지 않는다.
- 답변 문장 내에서 "{제품명}"은(는) 띄어쓰기까지 포함하여 반드시 그대로 사용해라.
- 답변 문장 내에서 "{제품명}"에 띄어쓰기를 추가하거나 제거해서는 절대 안 된다.
- '{성분명}'(들)은 절대 한글로 번역하지 말고 답변 문장 내에서 반드시 영문 그대로 해라.
- 아래에 제공된 약 이름과 약 정보 외의 그 어떤 지식도 참고하지 마라.

[사용자 질문]
{user_input}
         
[약 이름]
{제품명} 

[약 정보]
{section_text}
 
Answer:"""

    return prompt