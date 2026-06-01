# modules/documents/domain/repositories/document_extractor_repository.py

from abc import ABC, abstractmethod


class DocumentExtractorRepository(ABC):

    @abstractmethod
    def extract_text(self, file_path: str) -> str:
        pass