# modules/chunks/domain/chunkers/base_chunker.py

from abc import ABC, abstractmethod

from modules.documents.domain.entities.document import Document
from modules.chunks.domain.entities.document_chunk import DocumentChunk


class BaseChunker(ABC):

    @abstractmethod
    def chunk(self, document: Document) -> list[DocumentChunk]:
        pass