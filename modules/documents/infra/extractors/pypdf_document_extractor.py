from pypdf import PdfReader

from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)


class PyPdfDocumentExtractor(DocumentExtractorRepository):

<<<<<<< Updated upstream
    def extract_text(self, file_path: str) -> str:
=======
    def extract_text(self, file_path: str) -> tuple[str, dict]:
        if not file_path.lower().endswith(".pdf"):
            raise ValueError("O arquivo não é um documento PDF (.pdf).")

>>>>>>> Stashed changes
        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:
            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

        return text