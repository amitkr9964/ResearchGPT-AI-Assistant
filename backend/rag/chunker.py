"""Semantic text chunking with metadata preservation."""

from dataclasses import dataclass
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter

from backend.config import get_settings
from backend.utils.document_parser import ParsedDocument, ParsedPage
from backend.utils.text_cleaner import clean_text


@dataclass
class TextChunk:
    content: str
    page_number: int
    chunk_index: int
    metadata: dict


class SemanticChunker:
    def __init__(self) -> None:
        settings = get_settings()
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=settings.CHUNK_SIZE,
            chunk_overlap=settings.CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def chunk_document(self, parsed: ParsedDocument, document_id: int, filename: str) -> List[TextChunk]:
        chunks: List[TextChunk] = []
        global_index = 0

        for page in parsed.pages:
            page_text = clean_text(page.content)
            if not page_text:
                continue

            splits = self.splitter.split_text(page_text)
            for split in splits:
                if len(split.strip()) < 50:
                    continue
                chunks.append(
                    TextChunk(
                        content=split,
                        page_number=page.page_number,
                        chunk_index=global_index,
                        metadata={
                            "document_id": document_id,
                            "filename": filename,
                            "page_number": page.page_number,
                            "chunk_index": global_index,
                        },
                    )
                )
                global_index += 1

        return chunks
