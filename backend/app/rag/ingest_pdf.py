"""Run from backend: python -m app.rag.ingest_pdf."""

from pathlib import Path

from app.config import get_settings
from app.rag.store import get_collection, sync_source
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader


def ingest_pdf(path: Path) -> int:
    splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=120)
    texts, metadata = [], []
    for page_number, page in enumerate(PdfReader(path).pages, start=1):
        for chunk in splitter.split_text(page.extract_text() or ""):
            if chunk.strip():
                texts.append(chunk)
                metadata.append(
                    {
                        "source": path.name,
                        "source_type": "pdf",
                        "page": page_number,
                        "chunk": len(texts) - 1,
                    }
                )
    if not texts:
        raise ValueError(f"No extractable text in {path.name}; OCR may be required")
    return sync_source(get_collection(create=True), path.name, texts, metadata)


def ingest_pdfs(directory: Path | None = None) -> int:
    directory = directory or get_settings().data_path
    paths = sorted(directory.glob("*.pdf"))
    if not paths:
        raise FileNotFoundError(f"No PDF files in {directory}")
    return sum(ingest_pdf(path) for path in paths)


if __name__ == "__main__":
    print(f"Indexed {ingest_pdfs()} PDF chunks.")
