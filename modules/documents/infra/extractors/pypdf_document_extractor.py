from pypdf import PdfReader

from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)


class PyPdfDocumentExtractor(DocumentExtractorRepository):

    def extract_text(self, file_path: str) -> tuple[str, dict]:
        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text, {"page_count": len(reader.pages)}