# modules/documents/application/use_cases/extract_document_text.py

from uuid import uuid4
from pathlib import Path
from datetime import datetime
import os
import json

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

        # Tentativa de extração: vamos catar qualquer erro e lançar uma exceção de domínio com contexto
        try:
            text, extracted_metadata = self.extractor.extract_text(file_path)
        except Exception as e:
            from modules.documents.application.exceptions import DocumentExtractionError
            raise DocumentExtractionError(f"Erro ao extrair texto do arquivo {file_path}: {e}") from e
      

        metadata = {
            "processed_at": datetime.now().isoformat(),
            "document_size": len(text),
            "file_size_bytes": os.path.getsize(file_path),
            **extracted_metadata,
        }

        document = Document(
            document_id=str(uuid4()),
            file_name=Path(file_path).name,
            document_type=None,  # temporário, pois estamos testando com a lei
            source_path=file_path,
            text=text,
            metadata=metadata,
        )

        # Serializa e salva o documento em data/interim
        interim_dir = Path("data/interim")
        interim_dir.mkdir(parents=True, exist_ok=True)
        json_path = interim_dir / f"{document.file_name}.json"
        
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump({
                "document_id": document.document_id,
                "file_name": document.file_name,
                "document_type": document.document_type,
                "source_path": document.source_path,
                "text": document.text,
                "metadata": document.metadata
            }, f, ensure_ascii=False, indent=4)

        return document