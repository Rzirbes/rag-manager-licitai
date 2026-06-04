import pdfplumber

from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)


class PdfPlumberDocumentExtractor(DocumentExtractorRepository):

    def extract_text(self, file_path: str) -> tuple[str, dict]:
        text = ""
        page_count = 0

        with pdfplumber.open(file_path) as pdf:
            page_count = len(pdf.pages)
            for page in pdf.pages:
                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

        return text, {"page_count": page_count}