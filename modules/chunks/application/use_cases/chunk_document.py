# modules/chunks/application/use_cases/chunk_document.py

from modules.documents.domain.entities.document import Document
from modules.chunks.domain.entities.document_chunk import DocumentChunk

from modules.chunks.infra.chunkers.generic_chunker import GenericChunker
from modules.chunks.infra.chunkers.law_chunker import LawChunker
from modules.chunks.infra.chunkers.section_chunker import SectionChunker


class ChunkDocumentUseCase:

    def __init__(self):
        self.generic_chunker = GenericChunker()
        self.law_chunker = LawChunker()
        self.section_chunker = SectionChunker()

    def detect_document_type(self, text: str, file_name: str = "") -> str:
        upper_text = text.upper()
        upper_file = file_name.upper()

        if "MINUTA-DE-CONTRATO" in upper_file or "MINUTA DE CONTRATO" in upper_file:
            return "contract"

        if "ATA-DE-REGISTRO" in upper_file or "ATA DE REGISTRO" in upper_file:
            return "price_registry_minutes"

        if "DECLARA" in upper_file:
            return "declaration_model"

        if "REEQUIL" in upper_file or "RENOVA" in upper_file:
            return "addendum"

        if "ART. 1º" in upper_text or "LEI Nº" in upper_text:
            return "law"

        if "CONTRATO N.º" in upper_text or "CONTRATO Nº" in upper_text:
            return "contract"

        if "ATA DE REGISTRO DE PREÇOS" in upper_text:
            return "price_registry_minutes"

        if "MODELO DE DECLARAÇÃO" in upper_text:
            return "declaration_model"

        if "ADITIVO" in upper_text:
            return "addendum"

        if (
            "EDITAL DE PREGÃO" in upper_text
            or "EDITAL DE CONCORRÊNCIA" in upper_text
            or "CHAMAMENTO PÚBLICO" in upper_text
        ):
            return "bid_notice"

        return "generic"

    def execute(self, document: Document) -> list[DocumentChunk]:

        document_type = (
            document.document_type
            if document.document_type
            else self.detect_document_type(document.text, document.file_name)
        )

        document.document_type = document_type

        if document_type == "law":
            return self.law_chunker.chunk(document)

        if document_type in [
            "bid_notice",
            "contract",
            "price_registry_minutes",
            "declaration_model",
            "addendum",
        ]:
            return self.section_chunker.chunk(document)

        return self.generic_chunker.chunk(document)