class FakeLLM:
    """외부 LLM 호출을 완전히 막고, 체인 로직만 검증하기 위한 가짜 LLM."""
    def __init__(self, mode: str = "echo"):
        self.mode = mode

    def invoke(self, prompt: str) -> str:
        if self.mode == "echo":
            # 프롬프트가 제대로 만들어졌는지만 확인
            return f"[FAKE-LLM-ECHO]\\n{prompt}"
        elif self.mode == "template-ok":
            # 프롬프트 템플릿 키가 잘 치환되었는지 등만 확인할 때
            return "OK"
        else:
            return "[FAKE-LLM] (no-op)"
