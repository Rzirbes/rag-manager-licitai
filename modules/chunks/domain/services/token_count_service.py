from transformers import AutoTokenizer

class TokenCountService:
    """
    Serviço Singleton para gerenciar a tokenização e garantir que nenhum 
    pedaço do documento ultrapasse o limite do modelo de Embedding.
    """
    _instance = None
    _tokenizer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TokenCountService, cls).__new__(cls)
            # Inicializa o tokenizer do mesmo modelo usado no SentenceTransformer
            cls._instance._tokenizer = AutoTokenizer.from_pretrained("sentence-transformers/all-MiniLM-L6-v2")
        return cls._instance

    def count_tokens(self, text: str) -> int:
        """Retorna a quantidade de tokens de um texto."""
        if not text:
            return 0
        return len(self._tokenizer.encode(text, add_special_tokens=False))

    def split_text_by_tokens(self, text: str, max_tokens: int = 250, overlap: int = 50) -> list[str]:
        """
        Divide um texto grande em pedaços menores baseados em tokens reais.
        Tenta quebrar em espaços ou novas linhas para não cortar palavras no meio.
        """
        tokens = self._tokenizer.encode(text, add_special_tokens=False)
        
        if len(tokens) <= max_tokens:
            return [text.strip()]

        chunks = []
        start = 0

        while start < len(tokens):
            end = min(start + max_tokens, len(tokens))
            
            # Se for o fim do texto, apenas adiciona o que restou
            if end == len(tokens):
                chunk_tokens = tokens[start:end]
                decoded_text = self._tokenizer.decode(chunk_tokens).strip()
                if decoded_text:
                    chunks.append(decoded_text)
                break
                
            # Descodifica o pedaço até o limite máximo
            chunk_tokens = tokens[start:end]
            chunk_text = self._tokenizer.decode(chunk_tokens)
            
            # Recua para o último espaço ou quebra de linha para não cortar palavra no meio
            last_space = chunk_text.rfind(' ')
            last_newline = chunk_text.rfind('\n')
            cut_point = max(last_space, last_newline)
            
            if cut_point != -1 and cut_point > len(chunk_text) // 2:
                # Encontrou um ponto de corte razoável
                chunk_text = chunk_text[:cut_point]
                
                # Conta quantos tokens de fato usamos no corte limpo
                actual_tokens = self._tokenizer.encode(chunk_text, add_special_tokens=False)
                start += len(actual_tokens) - overlap
            else:
                # Corte forçado
                start += max_tokens - overlap
                
            clean_chunk = chunk_text.strip()
            if clean_chunk:
                chunks.append(clean_chunk)

        return chunks
