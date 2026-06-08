from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)

import csv

class CsvDocumentExtractor(DocumentExtractorRepository):
    # ta usando o module csv mas testar com pandas depois
    def extract_text(self, file_path: str) -> tuple[str, dict]:
        # evitar que esse extrator tente abrir um PDF e perca tempo gerando erro
        if not file_path.lower().endswith(".csv"):
            raise ValueError("O arquivo não é um documento CSV (.csv).")

        text = ""
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            for row in reader:
                text += " | ".join(row) + "\n"

        return text, {"page_count": 1}