import pdfplumber

from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)


class PdfPlumberDocumentExtractor(DocumentExtractorRepository):

    def extract_text(self, file_path: str) -> str:
        text = ""

        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        return text