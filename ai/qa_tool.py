from langchain.tools import tool
from rag.visitor_rag_service import load_visitor_vector_store



visitor_vector_store = load_visitor_vector_store()

@tool
def search_visitor_knowledge_base(query: str) -> str:
    """搜尋朝陽樂園遊客知識庫，回答票務、交通、設施及入園常見問題。"""
    docs = visitor_vector_store.similarity_search(query, k=3)

    return "\n\n".join(
        f"【遊客手冊來源 {i+1}｜{doc.metadata['category']}｜{doc.metadata['question']}】\n"
        f"{doc.page_content}"
        for i, doc in enumerate(docs)
    )