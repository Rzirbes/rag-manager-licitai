from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)
import pandas as pd 

class XlsxDocumentExtractor(DocumentExtractorRepository):


    def extract_text(self, file_path: str) -> tuple[str, dict]:
        # evitar que esse extrator tente abrir um PDF e perca tempo gerando erro
        if not file_path.lower().endswith(".xlsx"):
            raise ValueError("O arquivo não é um documento xlsx (.xlsx).")

        dados = pd.read_excel(file_path, sheet_name=None)
        
        text = ""
        for sheet, df in dados.items():
            text += f"--- Planilha: {sheet} ---\n"
            # fillna("") substitui a células vazias por uma string vazia
            text += df.fillna("").to_string(index=False) + "\n\n"
            
        return text.strip(), {"page_count": 1}
