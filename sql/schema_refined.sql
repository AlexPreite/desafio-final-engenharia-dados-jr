-- DDL da Camada Refined (Dados higienizados, tipados e com integridade relacional)

DROP TABLE IF EXISTS refined_itens_pedido;
DROP TABLE IF EXISTS refined_pedidos;
DROP TABLE IF EXISTS refined_produtos;
DROP TABLE IF EXISTS refined_clientes;

CREATE TABLE refined_clientes (
    id_cliente INTEGER PRIMARY KEY,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    cidade TEXT NOT NULL,
    estado TEXT NOT NULL,
    data_cadastro DATE NOT NULL
);

CREATE TABLE refined_produtos (
    id_produto INTEGER PRIMARY KEY,
    nome_produto TEXT NOT NULL,
    categoria TEXT NOT NULL,
    preco_unitario REAL NOT NULL CHECK(preco_unitario > 0),
    custo_unitario REAL NOT NULL CHECK(custo_unitario >= 0)
);

CREATE TABLE refined_pedidos (
    id_pedido INTEGER PRIMARY KEY,
    id_cliente INTEGER NOT NULL,
    data_pedido TIMESTAMP NOT NULL,
    status TEXT NOT NULL,
    metodo_pagamento TEXT NOT NULL,
    FOREIGN KEY (id_cliente) REFERENCES refined_clientes(id_cliente)
);

CREATE TABLE refined_itens_pedido (
    id_item INTEGER PRIMARY KEY,
    id_pedido INTEGER NOT NULL,
    id_produto INTEGER NOT NULL,
    quantidade INTEGER NOT NULL CHECK(quantidade > 0),
    preco_unitario REAL NOT NULL CHECK(preco_unitario > 0),
    subtotal REAL NOT NULL CHECK(subtotal > 0),
    FOREIGN KEY (id_pedido) REFERENCES refined_pedidos(id_pedido),
    FOREIGN KEY (id_produto) REFERENCES refined_produtos(id_produto)
);
