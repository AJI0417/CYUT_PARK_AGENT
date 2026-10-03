import os
import re
from pathlib import Path

from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import (
    MarkdownHeaderTextSplitter,
    RecursiveCharacterTextSplitter,
)
from transformers import AutoTokenizer


VECTOR_DIR = "./faiss_index"
MARKDOWN_FILE_PATH = Path("./樂園營運手冊.md")
EMBEDDING_MODEL = "BAAI/bge-base-zh-v1.5"
MAX_CHUNK_TOKENS = 480
CHUNK_OVERLAP_TOKENS = 40


def _header_prefix(metadata: dict) -> str:
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


def _split_markdown(markdown_text: str, tokenizer) -> list[Document]:
    header_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "document"),
            ("##", "chapter"),
            ("###", "section"),
        ],
        strip_headers=True,
    )
    sections = header_splitter.split_text(markdown_text)
    chunks = []

    for section in sections:
        prefix = _header_prefix(section.metadata)
        prefix_tokens = len(tokenizer.encode(prefix, add_special_tokens=False))
        body_chunk_size = MAX_CHUNK_TOKENS - prefix_tokens - 2

        body_splitter = RecursiveCharacterTextSplitter.from_huggingface_tokenizer(
            tokenizer,
            chunk_size=body_chunk_size,
            chunk_overlap=CHUNK_OVERLAP_TOKENS,
            separators=["\n\n", "\n", "。", "；", "，", ""],
        )

        for body in body_splitter.split_text(section.page_content):
            page_content = f"{prefix}\n\n{body}" if prefix else body
            metadata = {
                **section.metadata,
                "source": str(MARKDOWN_FILE_PATH),
            }
            wx_match = re.search(r"WX-\d{3}[A-Z]?", metadata.get("section", ""))
            if wx_match:
                metadata["wx_id"] = wx_match.group(0)

            chunks.append(Document(page_content=page_content, metadata=metadata))

    return chunks


def load_vector_store():
    
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )

    if os.path.exists(VECTOR_DIR):
        return FAISS.load_local(
            VECTOR_DIR,
            embeddings,
            allow_dangerous_deserialization=True,
        )

    markdown_text = MARKDOWN_FILE_PATH.read_text(encoding="utf-8")
    tokenizer = AutoTokenizer.from_pretrained(EMBEDDING_MODEL)
    texts = _split_markdown(markdown_text, tokenizer)

    db = FAISS.from_documents(texts, embeddings)
    db.save_local(VECTOR_DIR)
    
    return db
