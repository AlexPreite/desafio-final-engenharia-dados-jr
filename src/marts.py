"""
Módulo da Camada Marts (Indicadores e Métricas de Negócio).
Responsabilidades:
- Carregar os arquivos SQL individuais da pasta sql/marts/.
- Materializar ou consultar os indicadores analíticos diretamente sobre a camada Refined.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from typing import Optional, Dict
import pandas as pd
from src.config import MARTS_SQL_DIR, DB_PATH
from src.database import get_connection


def carregar_sql(nome_arquivo: str, sql_dir: Optional[Path] = None) -> str:
    """Carrega o conteúdo de um arquivo SQL da pasta de marts."""
    diretorio = sql_dir or MARTS_SQL_DIR
    caminho = diretorio / nome_arquivo
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo SQL não encontrado: {caminho}")
    with open(caminho, "r", encoding="utf-8") as f:
        return f.read()


def gerar_indicador(nome_arquivo_sql: str, db_path: Optional[Path] = None) -> pd.DataFrame:
    """Executa a consulta SQL correspondente e retorna um DataFrame do pandas."""
    query = carregar_sql(nome_arquivo_sql)
    conn = get_connection(db_path)
    try:
        return pd.read_sql_query(query, conn)
    finally:
        conn.close()


def materializar_camada_marts(db_path: Optional[Path] = None) -> Dict[str, int]:
    """
    Cria tabelas na camada Marts (prefixo marts_) para cada arquivo SQL de indicador.
    Retorna o total de linhas geradas em cada mart.
    """
    conn = get_connection(db_path)
    totais = {}
    marts_arquivos = {
        "marts_faturamento_categoria": "faturamento_por_categoria.sql",
        "marts_produtos_mais_vendidos": "produtos_mais_vendidos.sql",
        "marts_faturamento_cliente": "faturamento_por_cliente.sql",
        "marts_metricas_mensais": "metricas_mensais_ticket_medio.sql",
    }

    try:
        for nome_tabela, arquivo_sql in marts_arquivos.items():
            query = carregar_sql(arquivo_sql)
            df_mart = pd.read_sql_query(query, conn)
            df_mart.to_sql(nome_tabela, conn, if_exists="replace", index=False)
            totais[nome_tabela] = len(df_mart)
        return totais
    finally:
        conn.close()


if __name__ == "__main__":
    print("Materializando camada Marts a partir dos arquivos SQL...")
    resultado = materializar_camada_marts()
    for tabela, total in resultado.items():
        print(f" -> {tabela}: {total} registros gerados.")
