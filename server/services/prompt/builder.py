#
#
# def build_prompt(user_input: str, doc: dict) -> str:
#
#     # 구분 속성 처리
#     purchase_info = ""
#     if doc.get("구분", "") == "상비":
#         purchase_info = "이 약은 약국과 편의점에서 모두 구매할 수 있습니다."
#     elif doc.get("구분", "") == "일반":
#         purchase_info = "이 약은 약국에서만 구매할 수 있습니다."
#
#     return f"""당신은 외국인의 복약을 도와주는 약 정보 안내 챗봇입니다.
#     아래는 사용자의 증상에 맞는 약에 대한 상세 정보이며, 사용자의 질문에 친절하고 정확하게 답변해 주세요.
#
#     [사용자 질문]
#     {user_input}
#
#     [제품명]
#     {doc.get("제품명", "")}
#
#     [사용되는 증상]
#     {doc.get("ICD", "")}
#
#     [성분명]
#     {doc.get("성분명", "")}
#
#     [복용법]
#     {doc.get("복용법", "")}
#
#     [복용 또는 사용 금기 대상]
#     {doc.get("주의사항_금기대상", "")}
#
#     [약품 보관법]
#     {doc.get("약품 보관법", "")}
#
#     [구매 가능 장소]
#     {purchase_info}
#
#     [이미지 URL]
#     {doc.get("약품이미지(URL)", "")}
#
#     [기타 정보]
#     - BIT: {doc.get("BIT", "")}
#
#     답변:"""
#
#


def get_purchase_info(doc: dict) -> str:
    """
    '구분' 필드에 따라 구매 장소 문장 리턴
    """
    구분 = doc.get("구분", "").strip()
    if 구분 == "상비":
        return "이 약은 약국과 편의점에서 모두 구매할 수 있습니다."
    elif 구분 == "일반":
        return "이 약은 약국에서만 구매할 수 있습니다."
    return ""


def format_field(label: str, value: str) -> str:
    """
    빈 값이 아니면 [라벨]\n값 형태로 반환, 아니면 빈 문자열
    """
    value = value.strip()
    return f"[{label}]\n{value}" if value else ""


def build_prompt(user_input: str, doc: dict) -> str:

    fields = [
        ("제품명", doc.get("제품명", "")),
        ("사용되는 증상", doc.get("ICD", "")),
        ("성분명", doc.get("성분명", "")),
        ("복용법", doc.get("복용법", "")),
        ("복용 또는 사용 금기 대상", doc.get("주의사항_금기대상", "")),
        ("약품 보관법", doc.get("약품 보관법", "")),
        ("구매 가능 장소", get_purchase_info(doc)),
        ("이미지 URL", doc.get("약품이미지(URL)", "")),
        ("기타 정보", f"- BIT: {doc.get('BIT', '')}".strip())
    ]

    formatted_sections = [format_field(label, value) for label, value in fields if value.strip()]
    section_text = "\n\n".join(formatted_sections)

    return f"""당신은 외국인의 복약을 도와주는 약 정보 안내 챗봇입니다.
아래는 사용자의 증상에 맞는 약에 대한 상세 정보이며, 사용자의 질문에 친절하고 정확하게 답변해 주세요.

[사용자 질문]
{user_input}

{section_text}

답변:"""