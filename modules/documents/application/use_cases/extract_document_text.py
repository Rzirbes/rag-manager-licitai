# modules/documents/application/use_cases/extract_document_text.py

from uuid import uuid4
from pathlib import Path

from modules.documents.domain.entities.document import Document
from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)


class ExtractDocumentTextUseCase:

    def __init__(
        self,
        extractor: DocumentExtractorRepository,
    ):
        self.extractor = extractor

    def execute(self, file_path: str) -> Document:

        text = self.extractor.extract_text(file_path)

        return Document(
            id=str(uuid4()),
            file_name=Path(file_path).name,
            file_path=file_path,
            content=text,
        )