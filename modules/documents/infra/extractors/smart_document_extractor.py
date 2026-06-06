from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)
from modules.documents.infra.extractors.pypdf_document_extractor import (
    PyPdfDocumentExtractor,
)
from modules.documents.infra.extractors.pdf_plumber_document_extractor import (
    PdfPlumberDocumentExtractor,
)
from modules.documents.infra.extractors.ocr_document_extractor import (
    OcrDocumentExtractor,
)


class SmartDocumentExtractor(DocumentExtractorRepository):

    def __init__(self):
        self.extractors = [
            PyPdfDocumentExtractor(),
            PdfPlumberDocumentExtractor(),
            OcrDocumentExtractor(),
        ]

    def extract_text(self, file_path: str) -> tuple[str, dict]:
        import os
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"O arquivo {file_path} não foi encontrado.")

        for extractor in self.extractors:
            try:
                text, metadata = extractor.extract_text(file_path)
                if len(text.strip()) > 0:
                    return text, metadata
            except Exception as e:
                print(f"[Aviso] Falha ao extrair com {extractor.__class__.__name__}: {e}")
                continue

        raise ValueError("Nenhum extrator conseguiu extrair o texto do arquivo.")