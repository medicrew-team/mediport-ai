# server/services/rag/lc_llm_adapter.py
# 목적: 기존 run_inference(prompt)를 LangChain LLM처럼 사용할 수 있게 어댑터로 감싼다.

from typing import Any, List, Optional
from langchain_core.language_models.llms import LLM
from langchain_core.callbacks import CallbackManagerForLLMRun

# 기존 코드에서 사용 중인 실행 함수 import.
from server.services.inference.inference_selector import run_inference


class LocalInferenceLLM(LLM):
    # 필요한 경우 옵션을 더 받을 수 있도록 필드만 남겨 둔다
    model_name: str = "local-llm"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any
    ) -> str:
        # 기존 로컬/클라우드 선택 로직을 내장한 run_inference를 그대로 호출
        text = run_inference(prompt)

        # LangChain stop 토큰을 적용해야 할 때 여기서 자른다
        if stop:
            for s in stop:
                if s in text:
                    text = text.split(s)[0]
        return text

    @property
    def _llm_type(self) -> str:
        # 임의 식별자
        return "local-inference-llm"
