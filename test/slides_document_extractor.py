from modules.documents.domain.repositories.document_extractor_repository import (
    DocumentExtractorRepository,
)

import json
import pytesseract
from pdf2image import convert_from_path

# pega a jogada                                             
"""
Existem slides que foram convertidos em pdf, mas depende de como foi salvo.
digamos que um pdf foi feito qno power point, o texto, graficos e etc
ja estão imbutidos no documentos, a extração é facil.
Agora, digamos que usei o Canva e salvei como pdf, ex: "data/raw/Nova_Engenharia_das_Contratações.pdf"
o texto vira uma "imagem", então temos que usar o OCR para extrair o texto, mas antes disso
temos que usar o pdf2image para converter o pdf em imagem.
"""
class SlidesDocumentExtractor(DocumentExtractorRepository):
    def extract_text(self, file_path: str) -> tuple[str, dict]:
        if not file_path.lower().endswith(".pdf"):
            raise ValueError("O arquivo não é um documento PDF (.pdf).")
        file_exit= file_path.split(".pdf")[0] + "_result_pdf.txt"
        pages = convert_from_path(file_path, dpi=300)
        final_data_json = {
            "slides": [],
            'total_slides': len(pages),
            'processed_slides': 0,
            'origem_slide':file_path
        }
        text = ""
        
        # Iteramos sobre as imagens geradas, cada página do PDF virou uma imagem
        for index, page in enumerate(pages):
            page_text = pytesseract.image_to_string(page, lang="por")
            
            # Adicionamos uma marcação para separar os slides no texto final
            slide_text = f"--- Slide {index + 1} ---\n{page_text.strip()}\n\n"
            text += slide_text
            
            # Populamos o dicionário que vai servir como metadados
            final_data_json["slides"].append({
                "slide_number": index + 1,
                "content": page_text.strip()
            })
            final_data_json["processed_slides"] += 1
            
        # O padrão do repositório é retornar texto_em_string, metadados_em_dicionario
        return text.strip(), final_data_json

'''
DISCLAMER IMPORTANTE
Problema de Infraestrutura, a logica funciona supimpa
mas tem um porém, pra rodar isso na maquina local é tranquilo
mas pra rodar em deploy, vai ser osso, ou vai precisar de uma maquina virtual potente
ou vai ter q usar uma api de OCR, ele vai dar erro tipo:

Unable to get page count. Is poppler installed and in PATH?

Isso porque a linha convert_from_path(file_path, dpi=300) precisa de um software externo chamado Poppler
Então teremos que testar de outras maneiras, não deixe de ler 👌
'''
