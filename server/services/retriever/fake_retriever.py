from typing import List, Optional
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import PrivateAttr

from server.services.vector_store.vector_search import search_similar_medicines
from server.services.vector_store.save_to_faiss import build_text_for_embedding


class FakeRetriever(BaseRetriever):
    """LLM 없이 파이프라인만 검증하기 위한 가짜 Retriever."""

    top_k: int = 1  # pydantic 필드 선언
    fixed_docs: Optional[List[Document]] = None  # pydantic 필드 선언

    def _get_relevant_documents(self, query: str) -> List[Document]:
        if self.fixed_docs is not None:
            return self.fixed_docs

        hits = search_similar_medicines(query, top_k=self.top_k)
        docs: List[Document] = []

        for item in hits:
            try:
                # content = build_text_for_embedding(item)
                content = ""
            except Exception:
                content = str(item)
            docs.append(Document(page_content=content, metadata=item))
        return docs
