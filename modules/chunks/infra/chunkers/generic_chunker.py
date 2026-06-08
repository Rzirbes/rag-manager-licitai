# modules/chunks/infra/chunkers/generic_chunker.py

from uuid import uuid4

from modules.documents.domain.entities.document import Document
from modules.chunks.domain.entities.document_chunk import DocumentChunk
from modules.chunks.domain.chunkers.base_chunker import BaseChunker


class GenericChunker(BaseChunker):

    def chunk(
        self,
        document: Document,
        chunk_size: int = 1000,
        overlap: int = 200,
    ) -> list[DocumentChunk]:
        chunks: list[DocumentChunk] = []

        start = 0
        chunk_index = 0

        while start < len(document.text):
            end = start + chunk_size
           
            # se não for o último chunk, recua o 'end' até o último espaço ou quebra de linha
            if end < len(document.text):
                last_space = document.text.rfind(' ', start, end)
                last_newline = document.text.rfind('\n', start, end)
                cut_point = max(last_space, last_newline)
                
                # se viu um separador válido, corta ali
                if cut_point != -1 and cut_point > start:
                    end = cut_point
            

            content = document.text[start:end].strip()

            if content:
                chunks.append(
                    DocumentChunk(
                        document_id=document.document_id,
                        chunk_id=str(uuid4()),
                        content=content,
                        chunk_index=chunk_index,
                        metadata={
                            "file_name": document.file_name,
                            "document_type": document.document_type,
                            "source_path": document.source_path,
                            "section_type": "generic",
                            **document.metadata,
                        },
                    )
                )
            
            start += chunk_size - overlap

            # adicionei este bloco para faciltar, o fatiament de documentos genericos, já que antes cortavam no meio perdendo o sentido 
            next_start = end - overlap
            
            # arruma o próximo início para não começar no meio de uma palavra
            if next_start > start and next_start < len(document.text):
                next_space = document.text.find(' ', next_start, end)
                next_newline = document.text.find('\n', next_start, end)
                
                # pega o primeiro separador depois do next_start calculado
                separators = [s for s in (next_space, next_newline) if s != -1]
                if separators:
                    start = min(separators) + 1
                else:
                    start = next_start
            else:
                start = end

            chunk_index += 1
    
        return chunks