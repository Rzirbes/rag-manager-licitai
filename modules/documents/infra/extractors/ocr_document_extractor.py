from pdf2image import convert_from_path
import pytesseract

from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)


class OcrDocumentExtractor(DocumentExtractorRepository):

    def extract_text(self, file_path: str) -> str:
        pages = convert_from_path(file_path, dpi=300)

        text = ""

        for index, page in enumerate(pages):
            print(f"OCR: extraindo página {index + 1}...")

            page_text = pytesseract.image_to_string(
                page,
                lang="por",
            )

            if page_text:
                text += page_text + "\n"

        return text