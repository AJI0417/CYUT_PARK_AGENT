from pathlib import Path

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VISITOR_MANUAL_PATH = PROJECT_ROOT / "朝陽樂園遊客知識庫手冊.md"
VISITOR_VECTOR_FILE = PROJECT_ROOT / "vector_indexes" / "visitor.json"

EMBEDDING_MODEL = "BAAI/bge-base-zh-v1.5"

# 單位是「字元」，不是 token。
CHUNK_SIZE = 350
CHUNK_OVERLAP = 60


def _split_visitor_manual(markdown_text: str) -> list[Document]:
    """先按 FAQ 標題分開；較長的單題 FAQ 才繼續切分。"""
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "document"),
            ("##", "chapter"),
            ("###", "section"),
        ],
        strip_headers=True,
    )

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
        separators=["\n\n", "\n", "。", "；", "，", ""],
    )

    sections = header_splitter.split_text(markdown_text)
    chunks: list[Document] = []

    for faq in sections:
        # 沒有 ### 問題標題的前言，不作為 FAQ 答案。
        if not faq.metadata.get("section") or not faq.page_content.strip():
            continue

        headings = "\n".join(
            f"{marker} {faq.metadata[key]}"
            for key, marker in (
                ("document", "#"),
                ("chapter", "##"),
                ("section", "###"),
            )
            if faq.metadata.get(key)
        )

        # 不跨 FAQ 做 overlap，避免把兩個不同問題的答案混在一起。
        for body in text_splitter.split_text(faq.page_content):
            chunks.append(
                Document(
                    page_content=f"{headings}\n\n{body}",
                    metadata={
                        "source": str(VISITOR_MANUAL_PATH),
                        "knowledge_base": "visitor",
                        "category": faq.metadata.get("chapter", ""),
                        "question": faq.metadata["section"],
                    },
                )
            )

    return chunks


def load_visitor_vector_store():
    """有遊客索引就載入；沒有才建立，不碰營運索引。"""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )

    if VISITOR_VECTOR_FILE.is_file():
        return InMemoryVectorStore.load(str(VISITOR_VECTOR_FILE), embeddings)

    markdown_text = VISITOR_MANUAL_PATH.read_text(encoding="utf-8")
    chunks = _split_visitor_manual(markdown_text)

    if not chunks:
        raise ValueError("遊客手冊沒有可建立索引的 FAQ")

    vector_store = InMemoryVectorStore.from_documents(chunks, embeddings)
    vector_store.dump(str(VISITOR_VECTOR_FILE))

    return vector_store