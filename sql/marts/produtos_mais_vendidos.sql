-- Indicador: Ranking de Produtos Mais Vendidos e Receita
-- Decisão de Negócio:
-- 1. Excluímos pedidos com status 'cancelado'.
-- 2. Agrupamos por id, nome e categoria do produto.
-- 3. Ordenamos pelas unidades vendidas e em caso de empate pela receita total gerada.

SELECT
    prod.id_produto,
    prod.nome_produto,
    prod.categoria,
    SUM(item.quantidade) AS unidades_vendidas,
    COUNT(DISTINCT ped.id_pedido) AS total_pedidos,
    ROUND(SUM(item.subtotal), 2) AS receita_total
FROM refined_itens_pedido item
JOIN refined_pedidos ped ON ped.id_pedido = item.id_pedido
JOIN refined_produtos prod ON prod.id_produto = item.id_produto
WHERE ped.status != 'cancelado'
GROUP BY prod.id_produto, prod.nome_produto, prod.categoria
ORDER BY unidades_vendidas DESC, receita_total DESC;
