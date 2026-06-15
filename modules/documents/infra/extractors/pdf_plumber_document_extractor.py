import pdfplumber

from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)


class PdfPlumberDocumentExtractor(DocumentExtractorRepository):

    def extract_text(self, file_path: str) -> tuple[str, dict]:

        if not file_path.lower().endswith(".pdf"):
            raise ValueError("O arquivo não é um documento PDF (.pdf).")

        text = ""
        tables = []

        with pdfplumber.open(file_path) as pdf:

            for page_number, page in enumerate(pdf.pages, start=1):

                page_text = page.extract_text()

                if page_text:
                    text += page_text + "\n"

                page_tables = page.extract_tables()

                valid_tables = [
                    table
                    for table in page_tables
                    if self._is_valid_table(table)
                ]

                if valid_tables:
                    tables.append(
                        {
                            "page": page_number,
                            "tables": valid_tables,
                        }
                    )

            page_count = len(pdf.pages)

        return text, {
            "page_count": page_count,
            "tables": tables,
            "has_tables": len(tables) > 0,
        }

    def _is_valid_table(self, table: list[list[str | None]]) -> bool:

        if not table:
            return False

        rows = len(table)

        cols = max(
            (len(row) for row in table if row),
            default=0,
        )

        if rows < 2:
            return False

        if cols < 2:
            return False

        cell_count = sum(
            len(row)
            for row in table
            if row
        )

        if cell_count < 6:
            return False

        return True