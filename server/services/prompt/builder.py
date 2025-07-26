
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
        ("성분명", doc.get("성분명") + "\n"
                                 f"# ⚠️ 중요: 위에 표기된 '{성분명}'(들)은 절대 한글로 번역하지 말고 답변 문장 내에서 반드시 영문 그대로 사용해야 합니다.\n"
                                 f"# '{성분명}'(들)을 절대 한글로 번역하거나, 축약, 생략, 음역, 의역, 또는 유사한 표현으로 바꾸지 마세요.\n"
                                 f"# '{성분명}'(들)은 법적으로 등록된 고유명칭(들)이며, 사용자 혼란을 방지하기 위해 절대 변경해서는 안 됩니다.\n"
                                 f"# '{성분명}'(들)을 절대로 답변 문장 내에서 변경하지 마세요."),
        ("복용법", doc.get("복용법")),
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

    prompt =  f"""당신은 외국인의 복약을 도와주는 약 정보 안내 챗봇입니다.
아래는 사용자의 증상에 맞는 약에 대한 상세 정보이며, 사용자의 질문에 친절하고 정확하게 답변해 주세요.
      
    
[사용자 질문]
{user_input}

         
[질문과 관련된 약 이름]
{제품명} 
# ⚠️ 중요: 위에 표기된 "{제품명}"은(는) 답변 문장 내에서 띄어쓰기까지 포함하여 반드시 그대로 사용해야 합니다.  
# "{제품명}"을(를) 절대 축약, 생략, 음역, 의역, 또는 유사한 다른 표현으로 바꾸지 마세요.  
# "{제품명}"은(는) 법적으로 등록된 고유한 약 이름이며, 사용자 혼란을 방지하기 위해 절대 변경해서는 안됩니다.
# "{제품명}"을(를) 절대로 답변 문장 내에서 변경하지 마세요. 
# "{제품명}"에 띄어쓰기를 추가하거나 제거해서는 절대 안 됩니다.


[질문과 관련된 약의 상세 정보들]
{section_text}
    
답변:"""

    return prompt