import pandas as pd

from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)


class OdsDocumentExtractor(DocumentExtractorRepository):

    def extract_text(self, file_path: str) -> tuple[str, dict]:
        if not file_path.lower().endswith(".ods"):
            raise ValueError("O arquivo não é um documento ODS (.ods).")

        try:
            # O pandas suporta leitura de .ods usando a engine 'odf'
            dados = pd.read_excel(file_path, engine="odf", sheet_name=None)
        except ImportError:
            raise ImportError(
                "extrair planilhas .ods, requer a biblioteca odfpy. "
            )

        text = ""
        for sheet, df in dados.items():
            text += f"--- Planilha: {sheet} ---\n"
            text += df.fillna("").to_string(index=False) + "\n\n"
            
        return text.strip(), {"page_count": 1}
