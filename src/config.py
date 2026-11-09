"""
Configurações de diretórios e caminhos do projeto.
"""
from pathlib import Path

# Diretório raiz do projeto
BASE_DIR = Path(__file__).resolve().parent.parent

# Pastas de dados
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"

# Banco de dados SQLite do projeto
DB_PATH = DATA_DIR / "ecommerce.db"

# Pastas de SQL
SQL_DIR = BASE_DIR / "sql"
MARTS_SQL_DIR = SQL_DIR / "marts"
