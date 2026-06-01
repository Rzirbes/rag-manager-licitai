# modules/documents/domain/entities/document.py

from dataclasses import dataclass


@dataclass
class Document:
    id: str
    file_name: str
    file_path: str