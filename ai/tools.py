from langchain.tools import tool
from rag.rag_service import load_vector_store

vector_store = load_vector_store()

@tool
def search_knowledge_base(query: str) -> str:
    """搜索樂園營運手冊知識庫，查詢不同天氣條件下的設施營運規則和決策建議。"""
    docs = vector_store.similarity_search(query, k=5)

    return "\n\n".join(
        f"【來源 {i+1}】\n{doc.page_content}"
        for i, doc in enumerate(docs)
    )

