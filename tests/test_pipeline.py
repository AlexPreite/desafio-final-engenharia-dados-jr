"""
Testes Unitários Automatizados com Pytest.
Requisito obrigatório do professor:
- Rodar com dados inventados (mockados).
- Não abrir nem depender do arquivo de banco de dados do projeto (usar sqlite3 :memory:).
"""
import sqlite3
import pandas as pd
import pytest
from src.transform import (
    limpar_clientes,
    limpar_produtos,
    limpar_itens_pedido,
)
from src.marts import carregar_sql


def test_limpeza_clientes():
    """Valida se espaços em branco são removidos e e-mails convertidos para minúsculas."""
    dados_mock = pd.DataFrame([
        {
            "id_cliente": "1",
            "nome": "  Mariana Souza  ",
            "email": " Mariana.Souza@Email.Com ",
            "cidade": " São Paulo ",
            "estado": " sp ",
            "data_cadastro": "2023-05-10",
        }
    ])
    df_resultado = limpar_clientes(dados_mock)

    assert df_resultado.loc[0, "nome"] == "Mariana Souza"
    assert df_resultado.loc[0, "email"] == "mariana.souza@email.com"
    assert df_resultado.loc[0, "estado"] == "SP"
    assert df_resultado.loc[0, "id_cliente"] == 1


def test_calculo_subtotal_itens():
    """Valida se o cálculo derivado de subtotal (quantidade * preco) está correto."""
    dados_mock = pd.DataFrame([
        {"id_item": "1", "id_pedido": "10", "id_produto": "5", "quantidade": "3", "preco_unitario": "150.50"},
        {"id_item": "2", "id_pedido": "10", "id_produto": "8", "quantidade": "2", "preco_unitario": "70.00"},
    ])
    df_resultado = limpar_itens_pedido(dados_mock)

    assert df_resultado.loc[0, "subtotal"] == 451.50
    assert df_resultado.loc[1, "subtotal"] == 140.00
    assert df_resultado["subtotal"].sum() == 591.50


@pytest.fixture
def conexao_memoria():
    """Cria um banco SQLite isolado em memória com dados mockados para teste de SQL."""
    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")

    # Cria tabelas refinadas em memória
    conn.executescript("""
        CREATE TABLE refined_clientes (
            id_cliente INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            email TEXT NOT NULL,
            cidade TEXT NOT NULL,
            estado TEXT NOT NULL,
            data_cadastro DATE NOT NULL
        );
        CREATE TABLE refined_produtos (
            id_produto INTEGER PRIMARY KEY,
            nome_produto TEXT NOT NULL,
            categoria TEXT NOT NULL,
            preco_unitario REAL NOT NULL,
            custo_unitario REAL NOT NULL
        );
        CREATE TABLE refined_pedidos (
            id_pedido INTEGER PRIMARY KEY,
            id_cliente INTEGER NOT NULL,
            data_pedido TIMESTAMP NOT NULL,
            status TEXT NOT NULL,
            metodo_pagamento TEXT NOT NULL
        );
        CREATE TABLE refined_itens_pedido (
            id_item INTEGER PRIMARY KEY,
            id_pedido INTEGER NOT NULL,
            id_produto INTEGER NOT NULL,
            quantidade INTEGER NOT NULL,
            preco_unitario REAL NOT NULL,
            subtotal REAL NOT NULL
        );
    """)

    # Popula com dados mockados contendo 1 pedido entregue e 1 pedido cancelado
    conn.executescript("""
        INSERT INTO refined_clientes VALUES (1, 'Cliente Teste', 'teste@email.com', 'SP', 'SP', '2023-01-01');
        INSERT INTO refined_produtos VALUES (10, 'Teclado', 'Periféricos', 100.0, 60.0);
        INSERT INTO refined_produtos VALUES (20, 'Mouse', 'Periféricos', 50.0, 25.0);

        -- Pedido 101 ENTREGUE (1 Teclado + 2 Mouses = 100 + 100 = 200)
        INSERT INTO refined_pedidos VALUES (101, 1, '2023-07-01 10:00:00', 'entregue', 'PIX');
        INSERT INTO refined_itens_pedido VALUES (1, 101, 10, 1, 100.0, 100.0);
        INSERT INTO refined_itens_pedido VALUES (2, 101, 20, 2, 50.0, 100.0);

        -- Pedido 102 CANCELADO (deve ser ignorado pelos marts)
        INSERT INTO refined_pedidos VALUES (102, 1, '2023-07-02 11:00:00', 'cancelado', 'Boleto');
        INSERT INTO refined_itens_pedido VALUES (3, 102, 10, 5, 100.0, 500.0);
    """)

    yield conn
    conn.close()


def test_sql_marts_ignora_pedidos_cancelados(conexao_memoria):
    """
    Testa se a regra de negócio implementada no arquivo SQL faturamento_por_categoria.sql
    ignora pedidos cancelados e calcula a receita e lucro corretamente.
    """
    sql = carregar_sql("faturamento_por_categoria.sql")
    resultado = conexao_memoria.execute(sql).fetchall()

    # Como todos os produtos são 'Periféricos', deve vir apenas 1 categoria
    assert len(resultado) == 1
    linha = resultado[0]

    assert linha["categoria"] == "Periféricos"
    assert linha["total_itens_vendidos"] == 3  # 1 teclado + 2 mouses (o pedido cancelado tinha 5 teclados e NÃO entra)
    assert linha["receita_bruta"] == 200.0
    # Custo: 1*60 + 2*25 = 110.0
    assert linha["custo_total"] == 110.0
    # Lucro: 200.0 - 110.0 = 90.0
    assert linha["lucro_bruto"] == 90.0
    # Margem: 90 / 200 = 45.0%
    assert linha["margem_bruta_percentual"] == 45.0
