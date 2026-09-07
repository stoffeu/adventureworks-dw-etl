

from db_connections import get_postgres_connection


def load_fact_sales(pg_conn):
    sql = """
        INSERT INTO dw.fact_sales (
            date_key, product_key, customer_key, territory_key,
            sales_person_key, promotion_key,
            sales_order_id, sales_order_detail_id,
            order_qty, unit_price, unit_price_discount, line_total,
            standard_cost, online_order_flag,
            source_modified_date, dw_load_date
        )
        SELECT
            CAST(TO_CHAR(h.order_date, 'YYYYMMDD') AS INT) AS date_key,
            dp.product_key,
            dc.customer_key,
            dt.territory_key,
            COALESCE(dsp.sales_person_key, -1) AS sales_person_key,
            dpr.promotion_key,
            d.sales_order_id,
            d.sales_order_detail_id,
            d.order_qty,
            d.unit_price,
            d.unit_price_discount,
            d.line_total,
            sp_prod.standard_cost,
            h.online_order_flag,
            d.modified_date,
            now()
        FROM staging.stg_sales_order_detail d
        JOIN staging.stg_sales_order_header h
             ON d.sales_order_id = h.sales_order_id
        JOIN staging.stg_product sp_prod ON d.product_id = sp_prod.product_id
        JOIN dw.dim_product dp ON d.product_id = dp.product_id
        JOIN dw.dim_customer dc ON h.customer_id = dc.customer_id
        JOIN dw.dim_sales_territory dt ON h.territory_id = dt.territory_id
        JOIN dw.dim_promotion dpr ON d.special_offer_id = dpr.special_offer_id
        LEFT JOIN dw.dim_sales_person dsp ON h.sales_person_id = dsp.sales_person_id
        LEFT JOIN dw.fact_sales existing
               ON existing.sales_order_id = d.sales_order_id
              AND existing.sales_order_detail_id = d.sales_order_detail_id
        WHERE existing.sales_key IS NULL
           OR d.modified_date > existing.source_modified_date
        ON CONFLICT (sales_order_id, sales_order_detail_id) DO UPDATE SET
            date_key = EXCLUDED.date_key,
            product_key = EXCLUDED.product_key,
            customer_key = EXCLUDED.customer_key,
            territory_key = EXCLUDED.territory_key,
            sales_person_key = EXCLUDED.sales_person_key,
            promotion_key = EXCLUDED.promotion_key,
            order_qty = EXCLUDED.order_qty,
            unit_price = EXCLUDED.unit_price,
            unit_price_discount = EXCLUDED.unit_price_discount,
            line_total = EXCLUDED.line_total,
            standard_cost = EXCLUDED.standard_cost,
            online_order_flag = EXCLUDED.online_order_flag,
            source_modified_date = EXCLUDED.source_modified_date,
            dw_load_date = now();
    """
    with pg_conn.cursor() as cur:
        cur.execute(sql)
        affected = cur.rowcount
    pg_conn.commit()
    print(f"[fact_sales] {affected} linha(s) inserida(s)/atualizada(s).")


def run_fact_load():
    pg_conn = get_postgres_connection()
    print("=" * 70)
    print("CARGA DA TABELA FATO (incremental)")
    print("=" * 70)
    try:
        load_fact_sales(pg_conn)
    finally:
        pg_conn.close()
    print("=" * 70)
    print("CARGA DA FATO CONCLUÍDA")
    print("=" * 70)


if __name__ == "__main__":
    run_fact_load()
