"""
Gerenciamento de conexão e utilitários de banco de dados SQLite.
"""
import sqlite3
from pathlib import Path
from typing import Optional
from src.config import DB_PATH


def get_connection(db_path: Optional[Path] = None) -> sqlite3.Connection:
    """
    Retorna uma conexão com o SQLite configurada com suporte a row_factory e chaves estrangeiras.
    """
    caminho = db_path or DB_PATH
    conn = sqlite3.connect(caminho)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(db_path: Optional[Path] = None) -> None:
    """
    Garante que o diretório de dados exista e inicializa o arquivo do banco.
    """
    caminho = db_path or DB_PATH
    caminho.parent.mkdir(parents=True, exist_ok=True)
    with get_connection(caminho) as conn:
        conn.execute("SELECT 1;")


def reset_db(db_path: Optional[Path] = None) -> None:
    """
    Remove o arquivo de banco de dados se existir, para recriação do zero.
    """
    caminho = db_path or DB_PATH
    if caminho.exists():
        caminho.unlink()
