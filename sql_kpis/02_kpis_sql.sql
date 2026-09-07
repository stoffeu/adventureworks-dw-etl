-- ============================================================================
-- CONSULTAS SQL — COMPROVAÇÃO DOS 10 INDICADORES (KPIs)
-- Data Warehouse AdventureWorks (Star Schema) — PostgreSQL
-- ============================================================================


-- ============================================================================
-- KPI 1 — Receita total de vendas por período (mês/ano)
-- Métrica aditiva simples: soma de line_total agrupada pela hierarquia de
-- tempo da dim_date.
-- ============================================================================
SELECT
    dd.year,
    dd.month,
    dd.month_name,
    ROUND(SUM(fs.line_total), 2) AS receita_total
FROM dw.fact_sales fs
JOIN dw.dim_date dd ON fs.date_key = dd.date_key
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;


-- ============================================================================
-- KPI 2 — Ticket médio por pedido
-- Primeiro agregamos por pedido (sales_order_id), depois tiramos a média
-- sobre os totais de pedido -- não confundir com média por linha de item.
-- ============================================================================
SELECT
    ROUND(AVG(total_pedido), 2) AS ticket_medio
FROM (
    SELECT
        sales_order_id,
        SUM(line_total) AS total_pedido
    FROM dw.fact_sales
    GROUP BY sales_order_id
) pedidos;


-- ============================================================================
-- KPI 3 — Quantidade vendida por categoria de produto
-- Usa a hierarquia categoria > subcategoria já resolvida na dim_product.
-- ============================================================================
SELECT
    dp.category_name,
    SUM(fs.order_qty) AS quantidade_total_vendida,
    ROUND(SUM(fs.line_total), 2) AS receita_total
FROM dw.fact_sales fs
JOIN dw.dim_product dp ON fs.product_key = dp.product_key
GROUP BY dp.category_name
ORDER BY quantidade_total_vendida DESC;


-- ============================================================================
-- KPI 4 — Top N produtos por receita (exemplo com N = 10)
-- ============================================================================
SELECT
    dp.product_name,
    dp.category_name,
    SUM(fs.order_qty) AS quantidade_vendida,
    ROUND(SUM(fs.line_total), 2) AS receita_total
FROM dw.fact_sales fs
JOIN dw.dim_product dp ON fs.product_key = dp.product_key
GROUP BY dp.product_name, dp.category_name
ORDER BY receita_total DESC
LIMIT 10;


-- ============================================================================
-- KPI 5 — Receita por território de vendas
-- ============================================================================
SELECT
    dt.territory_name,
    dt.territory_group,
    ROUND(SUM(fs.line_total), 2) AS receita_total,
    COUNT(DISTINCT fs.sales_order_id) AS qtd_pedidos
FROM dw.fact_sales fs
JOIN dw.dim_sales_territory dt ON fs.territory_key = dt.territory_key
GROUP BY dt.territory_name, dt.territory_group
ORDER BY receita_total DESC;


-- ============================================================================
-- KPI 6 — Desempenho de vendas por vendedor
-- Inclui o "unknown member" (sales_person_key = -1), que agrega todas as
-- vendas do canal online sem vendedor associado -- técnica de modelagem
-- dimensional (Kimball) aplicada para não perder linhas em INNER JOIN.
-- ============================================================================
SELECT
    dsp.full_name,
    dsp.is_unknown_member,
    COUNT(DISTINCT fs.sales_order_id) AS qtd_pedidos,
    ROUND(SUM(fs.line_total), 2) AS receita_total
FROM dw.fact_sales fs
JOIN dw.dim_sales_person dsp ON fs.sales_person_key = dsp.sales_person_key
GROUP BY dsp.full_name, dsp.is_unknown_member
ORDER BY receita_total DESC;


-- ============================================================================
-- KPI 7 — Receita por canal de venda (Online vs Revenda)
-- Usa a flag online_order_flag armazenada diretamente na fato.
-- ============================================================================
SELECT
    CASE WHEN fs.online_order_flag THEN 'Online' ELSE 'Revenda' END AS canal_venda,
    COUNT(DISTINCT fs.sales_order_id) AS qtd_pedidos,
    ROUND(SUM(fs.line_total), 2) AS receita_total,
    ROUND(100.0 * SUM(fs.line_total) / SUM(SUM(fs.line_total)) OVER (), 2) AS pct_receita
FROM dw.fact_sales fs
GROUP BY fs.online_order_flag
ORDER BY receita_total DESC;


-- ============================================================================
-- KPI 8 — Impacto de descontos/promoções na receita
-- Compara receita bruta (sem desconto) vs receita líquida (com desconto
-- aplicado), por tipo de promoção.
-- ============================================================================
SELECT
    dpr.promotion_type,
    dpr.description,
    COUNT(*) AS qtd_itens_vendidos,
    ROUND(SUM(fs.order_qty * fs.unit_price), 2) AS receita_bruta_sem_desconto,
    ROUND(SUM(fs.line_total), 2) AS receita_liquida_com_desconto,
    ROUND(SUM(fs.order_qty * fs.unit_price) - SUM(fs.line_total), 2) AS valor_total_descontado
FROM dw.fact_sales fs
JOIN dw.dim_promotion dpr ON fs.promotion_key = dpr.promotion_key
GROUP BY dpr.promotion_type, dpr.description
ORDER BY valor_total_descontado DESC;


-- ============================================================================
-- KPI 9 — Margem bruta estimada (receita - custo do produto)
-- standard_cost é o custo unitário; multiplicamos pela quantidade vendida
-- para obter o custo total da linha, e comparamos com line_total (receita).
-- ============================================================================
SELECT
    dp.category_name,
    ROUND(SUM(fs.line_total), 2) AS receita_total,
    ROUND(SUM(fs.standard_cost * fs.order_qty), 2) AS custo_total,
    ROUND(SUM(fs.line_total) - SUM(fs.standard_cost * fs.order_qty), 2) AS margem_bruta,
    ROUND(
        100.0 * (SUM(fs.line_total) - SUM(fs.standard_cost * fs.order_qty))
        / NULLIF(SUM(fs.line_total), 0), 2
    ) AS margem_bruta_pct
FROM dw.fact_sales fs
JOIN dw.dim_product dp ON fs.product_key = dp.product_key
GROUP BY dp.category_name
ORDER BY margem_bruta DESC;


-- ============================================================================
-- KPI 10 — Novos clientes por período (primeira compra de cada cliente)
-- Identifica a data da primeira compra de cada cliente (MIN date_key) e
-- agrupa por ano/mês dessa primeira compra.
-- ============================================================================
WITH primeira_compra AS (
    SELECT
        customer_key,
        MIN(date_key) AS primeira_data_key
    FROM dw.fact_sales
    GROUP BY customer_key
)
SELECT
    dd.year,
    dd.month,
    dd.month_name,
    COUNT(*) AS qtd_novos_clientes
FROM primeira_compra pc
JOIN dw.dim_date dd ON pc.primeira_data_key = dd.date_key
GROUP BY dd.year, dd.month, dd.month_name
ORDER BY dd.year, dd.month;
