# modules/chunks/application/use_cases/chunk_document.py

from modules.documents.domain.entities.document import Document
from modules.chunks.domain.entities.document_chunk import DocumentChunk
from modules.chunks.infra.chunkers.generic_chunker import GenericChunker


class ChunkDocumentUseCase:

    def __init__(self):
        self.generic_chunker = GenericChunker()

    def execute(self, document: Document) -> list[DocumentChunk]:
        return self.generic_chunker.chunk(document)