import re
from pathlib import Path

from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MARKDOWN_FILE_PATH = PROJECT_ROOT / "樂園營運手冊.md"
VECTOR_FILE = PROJECT_ROOT / "vector_indexes" / "operations.json"

EMBEDDING_MODEL = "BAAI/bge-base-zh-v1.5"

# 單位是「字元」，不是 token。
CHUNK_SIZE = 350
CHUNK_OVERLAP = 60


def _header_prefix(metadata: dict) -> str:
    """把 Markdown 標題放回每個 chunk，保留內容脈絡。"""
    headers = (
        ("document", "#"),
        ("chapter", "##"),
        ("section", "###"),
    )
    return "\n".join(
        f"{marker} {metadata[key]}"
        for key, marker in headers
        if metadata.get(key)
    )


def _split_markdown(markdown_text: str) -> list[Document]:
    """先依標題分段，再將較長段落切成有 overlap 的 chunk。"""
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

    for section in sections:
        prefix = _header_prefix(section.metadata)

        # Overlap 只發生在同一個標題段落內，不混入別的章節。
        for body in text_splitter.split_text(section.page_content):
            page_content = f"{prefix}\n\n{body}" if prefix else body

            metadata = {
                **section.metadata,
                "source": str(MARKDOWN_FILE_PATH),
            }

            wx_match = re.search(r"WX-\d{3}[A-Z]?", metadata.get("section", ""))
            if wx_match:
                metadata["wx_id"] = wx_match.group(0)

            chunks.append(
                Document(page_content=page_content, metadata=metadata)
            )

    return chunks


def load_vector_store():
    """有快取就載入；沒有快取才切分、產生向量並存檔。"""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )

    if VECTOR_FILE.is_file():
        return InMemoryVectorStore.load(str(VECTOR_FILE), embeddings)

    markdown_text = MARKDOWN_FILE_PATH.read_text(encoding="utf-8")
    chunks = _split_markdown(markdown_text)

    if not chunks:
        raise ValueError("營運手冊沒有可建立索引的內容")

    vector_store = InMemoryVectorStore.from_documents(chunks, embeddings)
    vector_store.dump(str(VECTOR_FILE))

    return vector_store