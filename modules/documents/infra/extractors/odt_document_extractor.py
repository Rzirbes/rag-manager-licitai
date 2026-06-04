import zipfile
import xml.etree.ElementTree as ET

from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)


class OdtDocumentExtractor(DocumentExtractorRepository):

    def extract_text(self, file_path: str) -> tuple[str, dict]:
        if not file_path.lower().endswith(".odt"):
            raise ValueError("O arquivo não é um documento ODT (.odt).")

        text = ""
        
        try:
            with zipfile.ZipFile(file_path, 'r') as zf:
                # O conteúdo textual fica no arquivo content.xml
                content = zf.read("content.xml")
                
                # parse do XML
                root = ET.fromstring(content)
                
                # namespace padrão usado pelos documentos OpenDocument
                ns = {"text": "urn:oasis:names:tc:opendocument:xmlns:text:1.0"}
                
                # pega todos os parágrafos (<text:p>)
                for para in root.findall(".//text:p", ns):
                    # junta todos os pedaços de texto dentro do parágrafo
                    para_text = "".join(para.itertext())
                    if para_text.strip():
                        text += para_text.strip() + "\n"
        except zipfile.BadZipFile:
            raise ValueError("O arquivo ODT está corrompido ou não é um ZIP válido.")

        # O formato ODT não armazena a contagem de páginas de forma simples no XML.
        # Estimamos 1 página a cada ~1500 caracteres, semelhante ao DOCX.
        estimated_pages = max(1, len(text) // 1500)

        return text.strip(), {"page_count": estimated_pages}
