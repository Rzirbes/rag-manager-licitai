# modules/chunks/infra/chunkers/generic_chunker.py

from uuid import uuid4

from modules.documents.domain.entities.document import Document
from modules.chunks.domain.entities.document_chunk import DocumentChunk
from modules.chunks.domain.chunkers.base_chunker import BaseChunker
from modules.chunks.domain.services.token_count_service import TokenCountService


class GenericChunker(BaseChunker):

    def chunk(
        self,
        document: Document,
        max_tokens: int = 250,
        overlap_tokens: int = 50,
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []

        token_service = TokenCountService()
        
        # O serviço já resolve o particionamento respeitando a semântica de palavras e o limite matemático de IA
        pieces = token_service.split_text_by_tokens(document.text, max_tokens=max_tokens, overlap=overlap_tokens)

        for chunk_index, content in enumerate(pieces):
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

        return chunks