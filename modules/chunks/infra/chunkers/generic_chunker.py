# modules/chunks/infra/chunkers/generic_chunker.py

from uuid import uuid4

from modules.documents.domain.entities.document import Document
from modules.chunks.domain.entities.document_chunk import DocumentChunk
from modules.chunks.domain.chunkers.base_chunker import BaseChunker


class GenericChunker(BaseChunker):

    def chunk(
        self,
        document: Document,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []

        start = 0
        chunk_index = 0

        while start < len(document.text):
            end = start + chunk_size
            content = document.text[start:end].strip()

            if content:
                chunks.append(
                    DocumentChunk(
                        document_id=document.document_id,
                        chunk_id=str(uuid4()),
                        content=content,
                        chunk_index=chunk_index,
                        metadata={
                            "file_name": document.file_name,
                            "document_type": document.document_type,
                            "source_path": document.source_path,
                            "section_type": "generic",
                            **document.metadata,
                        },
                    )
                )

            start += chunk_size - overlap
            chunk_index += 1

        return chunks