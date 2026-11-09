-- Indicador: Métricas Mensais de Vendas e Ticket Médio por Pedido
-- Decisão de Negócio:
-- 1. Excluímos pedidos com status 'cancelado'.
-- 2. Agrupamos por ano-mês extraído da data do pedido (padrão ISO YYYY-MM).
-- 3. Acompanhamos volume de pedidos, compradores únicos, receita e ticket médio geral mensal.

SELECT
    strftime('%Y-%m', ped.data_pedido) AS ano_mes,
    COUNT(DISTINCT ped.id_pedido) AS total_pedidos,
    COUNT(DISTINCT ped.id_cliente) AS clientes_unicos,
    ROUND(SUM(item.subtotal), 2) AS faturamento_total,
    ROUND(SUM(item.subtotal) * 1.0 / COUNT(DISTINCT ped.id_pedido), 2) AS ticket_medio_pedido
FROM refined_pedidos ped
JOIN refined_itens_pedido item ON item.id_pedido = ped.id_pedido
WHERE ped.status != 'cancelado'
GROUP BY strftime('%Y-%m', ped.data_pedido)
ORDER BY ano_mes ASC;
