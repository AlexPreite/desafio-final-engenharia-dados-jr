"""
Módulo de Transformação: Camada Raw -> Camada Refined.
Responsabilidades:
- Higienização de strings (remoção de espaços extras, padronização de maiúsculas/minúsculas).
- Conversão e validação estrita de tipos (inteiros, floats, datas ISO).
- Cálculo de colunas derivadas (ex: subtotal de itens).
- Carga na estrutura relacional refinada com integridade de PK e FK.
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from typing import Optional, Dict
import pandas as pd
from src.config import DB_PATH, SQL_DIR
from src.database import get_connection


def aplicar_schema_refined(conn) -> None:
    """Executa o script DDL que cria as tabelas da camada refined."""
    caminho_schema = SQL_DIR / "schema_refined.sql"
    with open(caminho_schema, "r", encoding="utf-8") as f:
        conn.executescript(f.read())


def limpar_clientes(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Limpa e formata dados brutos de clientes."""
    df = df_raw.copy()
    df["id_cliente"] = df["id_cliente"].astype(int)
    df["nome"] = df["nome"].astype(str).str.strip()
    df["email"] = df["email"].astype(str).str.strip().str.lower()
    df["cidade"] = df["cidade"].astype(str).str.strip()
    df["estado"] = df["estado"].astype(str).str.strip().str.upper()
    df["data_cadastro"] = pd.to_datetime(df["data_cadastro"].str.strip()).dt.strftime("%Y-%m-%d")
    return df[["id_cliente", "nome", "email", "cidade", "estado", "data_cadastro"]]


def limpar_produtos(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Limpa e formata dados brutos de produtos."""
    df = df_raw.copy()
    df["id_produto"] = df["id_produto"].astype(int)
    df["nome_produto"] = df["nome_produto"].astype(str).str.strip()
    df["categoria"] = df["categoria"].astype(str).str.strip()
    df["preco_unitario"] = df["preco_unitario"].astype(float)
    df["custo_unitario"] = df["custo_unitario"].astype(float)
    return df[["id_produto", "nome_produto", "categoria", "preco_unitario", "custo_unitario"]]


def limpar_pedidos(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Limpa e formata dados brutos de pedidos."""
    df = df_raw.copy()
    df["id_pedido"] = df["id_pedido"].astype(int)
    df["id_cliente"] = df["id_cliente"].astype(int)
    df["data_pedido"] = pd.to_datetime(df["data_pedido"].str.strip()).dt.strftime("%Y-%m-%d %H:%M:%S")
    df["status"] = df["status"].astype(str).str.strip().str.lower()
    df["metodo_pagamento"] = df["metodo_pagamento"].astype(str).str.strip()
    return df[["id_pedido", "id_cliente", "data_pedido", "status", "metodo_pagamento"]]


def limpar_itens_pedido(df_raw: pd.DataFrame) -> pd.DataFrame:
    """Limpa, formata e calcula subtotais dos itens de pedido."""
    df = df_raw.copy()
    df["id_item"] = df["id_item"].astype(int)
    df["id_pedido"] = df["id_pedido"].astype(int)
    df["id_produto"] = df["id_produto"].astype(int)
    df["quantidade"] = df["quantidade"].astype(int)
    df["preco_unitario"] = df["preco_unitario"].astype(float)
    df["subtotal"] = (df["quantidade"] * df["preco_unitario"]).round(2)
    return df[["id_item", "id_pedido", "id_produto", "quantidade", "preco_unitario", "subtotal"]]


def transformar_camada_refined(db_path: Optional[Path] = None) -> Dict[str, int]:
    """
    Executa a transformação da camada Raw para a camada Refined no SQLite.
    """
    conn = get_connection(db_path)
    totais = {}

    try:
        # 1. Cria tabelas da camada refinada
        aplicar_schema_refined(conn)

        # 2. Lê tabelas brutas
        raw_clientes = pd.read_sql("SELECT * FROM raw_clientes", conn)
        raw_produtos = pd.read_sql("SELECT * FROM raw_produtos", conn)
        raw_pedidos = pd.read_sql("SELECT * FROM raw_pedidos", conn)
        raw_itens = pd.read_sql("SELECT * FROM raw_itens_pedido", conn)

        # 3. Transforma
        refined_clientes = limpar_clientes(raw_clientes)
        refined_produtos = limpar_produtos(raw_produtos)
        refined_pedidos = limpar_pedidos(raw_pedidos)
        refined_itens = limpar_itens_pedido(raw_itens)

        # 4. Grava na camada refinada (respeitando ordem de integridade referencial)
        refined_clientes.to_sql("refined_clientes", conn, if_exists="append", index=False)
        refined_produtos.to_sql("refined_produtos", conn, if_exists="append", index=False)
        refined_pedidos.to_sql("refined_pedidos", conn, if_exists="append", index=False)
        refined_itens.to_sql("refined_itens_pedido", conn, if_exists="append", index=False)

        totais["refined_clientes"] = len(refined_clientes)
        totais["refined_produtos"] = len(refined_produtos)
        totais["refined_pedidos"] = len(refined_pedidos)
        totais["refined_itens_pedido"] = len(refined_itens)

        return totais
    finally:
        conn.close()


if __name__ == "__main__":
    print("Iniciando processamento da camada Refined...")
    resultado = transformar_camada_refined()
    for tabela, total in resultado.items():
        print(f" -> {tabela}: {total} registros processados e inseridos.")
