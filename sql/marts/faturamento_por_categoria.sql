-- Indicador: Faturamento e Lucro por Categoria de Produto
-- Decisão de Negócio:
-- 1. Excluímos pedidos com status 'cancelado', pois não representam receita efetiva da loja.
-- 2. Calculamos receita, custo total e margem de lucro percentual para orientar decisões de estoque.

SELECT
    prod.categoria,
    SUM(item.quantidade) AS total_itens_vendidos,
    ROUND(SUM(item.subtotal), 2) AS receita_bruta,
    ROUND(SUM(item.quantidade * prod.custo_unitario), 2) AS custo_total,
    ROUND(SUM(item.subtotal) - SUM(item.quantidade * prod.custo_unitario), 2) AS lucro_bruto,
    ROUND(
        ((SUM(item.subtotal) - SUM(item.quantidade * prod.custo_unitario)) * 100.0) / SUM(item.subtotal),
        2
    ) AS margem_bruta_percentual
FROM refined_itens_pedido item
JOIN refined_pedidos ped ON ped.id_pedido = item.id_pedido
JOIN refined_produtos prod ON prod.id_produto = item.id_produto
WHERE ped.status != 'cancelado'
GROUP BY prod.categoria
ORDER BY receita_bruta DESC;
