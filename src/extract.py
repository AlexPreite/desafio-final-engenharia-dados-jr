"""
Módulo de Extração e Ingestão para a Camada Raw (Bruta).
Regra: Na camada bruta, nada é alterado. Os dados são gravados exatamente como vieram.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

import pandas as pd
from typing import Optional, Dict
from src.config import RAW_DIR, DB_PATH
from src.database import get_connection


def extrair_camada_raw(raw_dir: Optional[Path] = None, db_path: Optional[Path] = None) -> Dict[str, int]:
    """
    Lê os arquivos CSV da camada de dados brutos e os persiste no banco de dados
    com o prefixo 'raw_', sem realizar nenhuma transformação ou limpeza.
    Retorna a contagem de registros ingeridos por tabela.
    """
    diretorio_raw = raw_dir or RAW_DIR
    arquivos = {
        "raw_clientes": diretorio_raw / "clientes.csv",
        "raw_produtos": diretorio_raw / "produtos.csv",
        "raw_pedidos": diretorio_raw / "pedidos.csv",
        "raw_itens_pedido": diretorio_raw / "itens_pedido.csv",
    }

    conn = get_connection(db_path)
    totais = {}

    try:
        for nome_tabela, caminho_csv in arquivos.items():
            if not caminho_csv.exists():
                raise FileNotFoundError(f"Arquivo de origem não encontrado: {caminho_csv}")

            # Leitura do CSV bruto (mantendo todos os tipos e formatos originais como texto)
            df_bruto = pd.read_csv(caminho_csv, dtype=str)
            df_bruto.to_sql(nome_tabela, conn, if_exists="replace", index=False)
            totais[nome_tabela] = len(df_bruto)

        return totais
    finally:
        conn.close()


if __name__ == "__main__":
    print("Iniciando ingestão da camada Raw...")
    resultado = extrair_camada_raw()
    for tabela, total in resultado.items():
        print(f" -> {tabela}: {total} registros ingeridos com sucesso.")
