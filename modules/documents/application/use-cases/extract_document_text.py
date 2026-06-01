# modules/documents/application/use_cases/extract_document_text.py

from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)


class ExtractDocumentTextUseCase:

    def __init__(
        self,
        extractor: DocumentExtractorRepository,
    ):
        self.extractor = extractor

    def execute(self, file_path: str):
        return self.extractor.extract_text(file_path)