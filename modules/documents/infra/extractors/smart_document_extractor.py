from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)
from modules.documents.infra.extractors.pypdf_document_extractor import (
    PyPdfDocumentExtractor,
)
from modules.documents.infra.extractors.pdf_plumber_document_extractor import (
    PdfPlumberDocumentExtractor,
)
from modules.documents.infra.extractors.ocr_document_extractor import (
    OcrDocumentExtractor,
)
from modules.documents.infra.extractors.docx_document_extractor import (
    DocxDocumentExtractor,
)

from modules.documents.infra.extractors.csv_document_extractor import (
    CsvDocumentExtractor,
)

from modules.documents.infra.extractors.xlsx_document_extractor import (
    XlsxDocumentExtractor,
)
from modules.documents.infra.extractors.odt_document_extractor import (
    OdtDocumentExtractor,
)
from modules.documents.infra.extractors.ods_document_extractor import (
    OdsDocumentExtractor,
)

class SmartDocumentExtractor(DocumentExtractorRepository):

    def __init__(self):
        self.extractors = [
            PdfPlumberDocumentExtractor(),
            PyPdfDocumentExtractor(),
            OcrDocumentExtractor(),
            XlsxDocumentExtractor(),
            CsvDocumentExtractor(),
            DocxDocumentExtractor(),
            OdtDocumentExtractor(),
            OdsDocumentExtractor(),
        ]

    def extract_text(self, file_path: str) -> tuple[str, dict]:

        for extractor in self.extractors:
            try:
                text, metadata = extractor.extract_text(file_path)

                if len(text.strip()) > 0:
                    return text, metadata
                
            except Exception as e:
                print(f"[Aviso] Falha ao extrair com {extractor.__class__.__name__}: {e}")
                continue


        # Se passou por todos os extratores, dispara a exceção
        raise ValueError("Nenhum extrator conseguiu extrair o texto do documento. O arquivo pode estar vazio ou corrompido.")
        