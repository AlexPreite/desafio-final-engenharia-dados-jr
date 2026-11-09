-- Indicador: Faturamento Acumulado e Ticket Médio por Cliente (LTV Inicial)
-- Decisão de Negócio:
-- 1. Excluímos pedidos com status 'cancelado'.
-- 2. Agrupamos por cliente e cidade/UF para identificar praças de maior valor.
-- 3. Calculamos total gasto e ticket médio por pedido do cliente.

SELECT
    cli.id_cliente,
    cli.nome AS nome_cliente,
    cli.cidade,
    cli.estado,
    COUNT(DISTINCT ped.id_pedido) AS total_pedidos,
    ROUND(SUM(item.subtotal), 2) AS total_gasto,
    ROUND(SUM(item.subtotal) * 1.0 / COUNT(DISTINCT ped.id_pedido), 2) AS ticket_medio_cliente
FROM refined_clientes cli
JOIN refined_pedidos ped ON ped.id_cliente = cli.id_cliente
JOIN refined_itens_pedido item ON item.id_pedido = ped.id_pedido
WHERE ped.status != 'cancelado'
GROUP BY cli.id_cliente, cli.nome, cli.cidade, cli.estado
ORDER BY total_gasto DESC;
