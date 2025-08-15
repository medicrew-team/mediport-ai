# server/services/rag/lc_retriever.py
# 목적: 현재 search_similar_medicines()를 LangChain의 BaseRetriever로 감싸서
#       LangChain 체인 내부에서 호출 가능하게 만든다.

from typing import List
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

# 현재 벡터 검색 함수를 그대로 가져와 사용
from server.services.vector_store.vector_search import search_similar_medicines
# 프롬프트 생성을 위해 동일한 조립 로직이 필요하면 import
from server.services.vector_store.save_to_faiss import build_text_for_embedding


class CurrentPipelineRetriever(BaseRetriever):
    # top_k를 외부에서 주입 가능하게 기본값을 준다
    top_k: int = 1

    def _get_relevant_documents(self, query: str) -> List[Document]:
        # 현재 파이프라인 그대로 사용: 문자열 매칭 → FAISS 검색
        hits = search_similar_medicines(query, top_k=self.top_k)

        docs: List[Document] = []
        for item in hits:
            # page_content는 LLM에게 줄 본문. 기존 임베딩 조립 문장을 재사용하면 일관성이 높다.
            try:
                content = build_text_for_embedding(item)
            except Exception:
                # 필수 필드가 누락된 데이터가 있을 수 있으므로 방어적으로 제품명만이라도 넣는다
                content = item.get("제품명", "")

            # LangChain Document에 원본 메타데이터를 그대로 실어 보관
            docs.append(
                Document(page_content=content, metadata=item)
            )
        return docs

    async def _aget_relevant_documents(self, query: str) -> List[Document]:
        # 비동기 진입점도 동일 로직으로 처리
        return self._get_relevant_documents(query)
