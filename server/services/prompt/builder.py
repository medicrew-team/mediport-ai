def build_prompt(user_input: str, doc: dict) -> str:
    return f"""당신은 외국인의 복약을 도와주는 약 정보 안내 챗봇입니다.
아래는 사용자의 증상에 맞는 약에 대한 상세 정보이며, 사용자의 질문에 친절하고 정확하게 답변해 주세요.

[사용자 질문]
{user_input}

[제품명]
{doc.get("제품명", "")}

[사용되는 증상]
{doc.get("ICD", "")}

[성분명]
{doc.get("성분명", "")}

[복용법]
{doc.get("복용법", "")}

[주의사항]
{doc.get("주의사항", "")}

[이미지 URL]
{doc.get("약품이미지(URL)", "")}

[기타 정보]
- BIT: {doc.get("BIT", "")}
- 구분: {doc.get("구분", "")}
- ATC 코드: {doc.get("ATC코드", "")}
- 제품 코드: {doc.get("제품코드", "")}
- 주성분코드: {doc.get("주성분코드", "")}

답변:"""