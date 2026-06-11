# pyrefly: ignore [missing-import]
from docx import Document

from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)


class DocxDocumentExtractor(DocumentExtractorRepository):

    def extract_text(self, file_path: str) -> tuple[str, dict]:
        # evitar que esse extrator tente abrir um PDF e perca tempo gerando erro
        if not file_path.lower().endswith(".docx"):
            raise ValueError("O arquivo não é um documento Word (.docx).")

        docx = Document(file_path)
        text = ""
        
        # extrai os paragrafos do documento
        for paragraph in docx.paragraphs:
            if paragraph.text.strip():
                text += paragraph.text.strip() + "\n"
        
        # extrai textos de possíveis tabelas dentro do Word
        for table in docx.tables:
            for row in table.rows:
                row_data = []
                for cell in row.cells:
                    cell_content = cell.text.strip().replace("\n", " ").replace("\xa0", " ")
                    if cell_content:
                        row_data.append(cell_content)
                if row_data:
                    text += " | ".join(row_data) + "\n"

        # formato DOCX não armazena a quantidade de páginas.
        # estimar 1 página a cada ~1500 caracteres, ou setar como 1 se não souber.
        estimated_pages = max(1, len(text) // 1500)

        return text, {"page_count": estimated_pages}