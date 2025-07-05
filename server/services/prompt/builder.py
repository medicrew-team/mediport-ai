def build_prompt(user_input: str, doc: dict) -> str:
    return f"""당신은 외국인의 복약을 도와주는 약 정보 안내 챗봇입니다.
아래는 사용자의 증상에 맞는 약에 대한 상세 정보이며, 사용자의 질문에 친절하고 정확하게 답변해 주세요.

[사용자 질문]
{user_input}

[약 이름]
{doc.get("name", "")}

[효능 및 증상]
{", ".join(doc.get("symptoms", []))}

[약 설명]
{doc.get("text", "")}

[복용법]
{doc.get("dosage", "")}

[주의사항]
{doc.get("cautions", "")}

[연령 제한]
{doc.get("age_limit", "")}

[성분]
{", ".join(doc.get("ingredients", []))}

[제형]
{doc.get("form", "")}

답변:"""