# modules/documents/application/use_cases/extract_document_text.py

from uuid import uuid4
from pathlib import Path
from datetime import datetime

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
        import os

        text, extracted_metadata = self.extractor.extract_text(file_path)

        metadata = {
            "processed_at": datetime.now().isoformat(),
            "document_size": len(text),
            "file_size_bytes": os.path.getsize(file_path),
            **extracted_metadata,
        }

        return Document(
            document_id=str(uuid4()),
            file_name=Path(file_path).name,
            document_type=None,  # temporário, pois estamos testando com a lei
            source_path=file_path,
            text=text,
            metadata=metadata,
        )