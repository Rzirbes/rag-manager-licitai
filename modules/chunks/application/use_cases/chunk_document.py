# modules/chunks/application/use_cases/chunk_document.py

from modules.documents.domain.entities.document import Document
from modules.chunks.domain.entities.document_chunk import DocumentChunk
from modules.chunks.infra.chunkers.generic_chunker import GenericChunker
from modules.chunks.infra.chunkers.law_chunker import LawChunker


class ChunkDocumentUseCase:

    def __init__(self):
        self.generic_chunker = GenericChunker()
        self.law_chunker = LawChunker()

    def execute(self, document: Document) -> list[DocumentChunk]:
        if document.document_type == "law":
            return self.law_chunker.chunk(document)

        return self.generic_chunker.chunk(document)