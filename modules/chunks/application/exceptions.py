# modules/chunks/application/exceptions.py

class DocumentChunkingError(Exception):
    """Exceção levantada quando ocorre uma falha no fatiamento (chunking) de um documento."""
    pass
