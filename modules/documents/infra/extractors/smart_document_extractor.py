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

    def extract_text(self, file_path: str) -> str:
        for extractor in self.extractors:
            text = extractor.extract_text(file_path)

            if len(text.strip()) > 0:
                return text

        return ""