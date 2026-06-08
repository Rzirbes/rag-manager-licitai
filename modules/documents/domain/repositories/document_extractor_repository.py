# modules/documents/domain/repositories/document_extractor_repository.py

from abc import ABC, abstractmethod
from typing import Any


class DocumentExtractorRepository(ABC):

    @abstractmethod
    def extract_text(self, file_path: str) -> tuple[str, dict[str, Any]]:
        pass