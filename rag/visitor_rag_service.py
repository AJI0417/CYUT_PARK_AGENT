from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import MarkdownHeaderTextSplitter


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VISITOR_MANUAL_PATH = PROJECT_ROOT / "朝陽樂園遊客知識庫手冊.md"
VISITOR_VECTOR_DIR = PROJECT_ROOT / "faiss_visitor_index"
EMBEDDING_MODEL = "BAAI/bge-base-zh-v1.5"


def _split_visitor_manual(markdown_text: str) -> list[Document]:
    """Keep each nonempty Markdown FAQ as one self-contained document."""
    sections = MarkdownHeaderTextSplitter(
        headers_to_split_on=[
            ("#", "document"),
            ("##", "chapter"),
            ("###", "section"),
        ],
        strip_headers=True,
    ).split_text(markdown_text)

    chunks: list[Document] = []
    for faq in sections:
        # The document preamble and category introductions are not FAQ answers.
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
        chunks.append(
            Document(
                page_content=f"{headings}\n\n{faq.page_content.strip()}",
                metadata={
                    "source": str(VISITOR_MANUAL_PATH),
                    "knowledge_base": "visitor",
                    "category": faq.metadata.get("chapter", ""),
                    "question": faq.metadata["section"],
                },
            )
        )
        
    return chunks


def load_visitor_vector_store(*, force_rebuild: bool = False) -> FAISS:
    """Load or build only the visitor FAQ index using BGE embeddings."""
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={"device": "cpu"},
    )

    if (
        not force_rebuild
        and (VISITOR_VECTOR_DIR / "index.faiss").is_file()
        and (VISITOR_VECTOR_DIR / "index.pkl").is_file()
    ):
        # This pickle-backed index must come only from our trusted local build.
        return FAISS.load_local(
            str(VISITOR_VECTOR_DIR),
            embeddings,
            allow_dangerous_deserialization=True,
        )

    chunks = _split_visitor_manual(VISITOR_MANUAL_PATH.read_text(encoding="utf-8"))
    vector_store = FAISS.from_documents(chunks, embeddings)
    vector_store.save_local(str(VISITOR_VECTOR_DIR))
    return vector_store
