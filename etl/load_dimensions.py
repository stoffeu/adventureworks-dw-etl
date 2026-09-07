

from db_connections import get_postgres_connection


def load_dim_product(pg_conn):
    sql = """
        INSERT INTO dw.dim_product (
            product_id, product_name, product_number, color, size,
            category_name, subcategory_name, list_price,
            source_modified_date, dw_load_date
        )
        SELECT
            p.product_id,
            p.product_name,
            p.product_number,
            p.color,
            p.size,
            pc.name AS category_name,
            psc.name AS subcategory_name,
            p.list_price,
            p.modified_date,
            now()
        FROM staging.stg_product p
        LEFT JOIN staging.stg_product_subcategory psc
               ON p.product_subcategory_id = psc.product_subcategory_id
        LEFT JOIN staging.stg_product_category pc
               ON psc.product_category_id = pc.product_category_id
        ON CONFLICT (product_id) DO UPDATE SET
            product_name = EXCLUDED.product_name,
            product_number = EXCLUDED.product_number,
            color = EXCLUDED.color,
            size = EXCLUDED.size,
            category_name = EXCLUDED.category_name,
            subcategory_name = EXCLUDED.subcategory_name,
            list_price = EXCLUDED.list_price,
            source_modified_date = EXCLUDED.source_modified_date,
            dw_load_date = now();
    """
    with pg_conn.cursor() as cur:
        cur.execute(sql)
        affected = cur.rowcount
    pg_conn.commit()
    print(f"[dim_product] {affected} linha(s) inserida(s)/atualizada(s).")


def load_dim_customer(pg_conn):
  
    sql = """
        WITH primary_address AS (
            SELECT DISTINCT ON (business_entity_id)
                   business_entity_id, address_id
            FROM staging.stg_business_entity_address
            ORDER BY business_entity_id, address_id
        )
        INSERT INTO dw.dim_customer (
            customer_id, person_name, store_name, account_number,
            city, state_province, country_region,
            source_modified_date, dw_load_date
        )
        SELECT
            c.customer_id,
            TRIM(CONCAT(per.first_name, ' ', per.last_name)) AS person_name,
            st.name AS store_name,
            c.account_number,
            addr.city,
            sp.name AS state_province,
            cr.name AS country_region,
            c.modified_date,
            now()
        FROM staging.stg_customer c
        LEFT JOIN staging.stg_person per ON c.person_id = per.business_entity_id
        LEFT JOIN staging.stg_store st ON c.store_id = st.business_entity_id
        LEFT JOIN primary_address pa
               ON pa.business_entity_id = COALESCE(c.person_id, c.store_id)
        LEFT JOIN staging.stg_address addr ON pa.address_id = addr.address_id
        LEFT JOIN staging.stg_state_province sp ON addr.state_province_id = sp.state_province_id
        LEFT JOIN staging.stg_country_region cr ON sp.country_region_code = cr.country_region_code
        ON CONFLICT (customer_id) DO UPDATE SET
            person_name = EXCLUDED.person_name,
            store_name = EXCLUDED.store_name,
            account_number = EXCLUDED.account_number,
            city = EXCLUDED.city,
            state_province = EXCLUDED.state_province,
            country_region = EXCLUDED.country_region,
            source_modified_date = EXCLUDED.source_modified_date,
            dw_load_date = now();
    """
    with pg_conn.cursor() as cur:
        cur.execute(sql)
        affected = cur.rowcount
    pg_conn.commit()
    print(f"[dim_customer] {affected} linha(s) inserida(s)/atualizada(s).")


def load_dim_sales_territory(pg_conn):
    sql = """
        INSERT INTO dw.dim_sales_territory (
            territory_id, territory_name, country_region_code, territory_group
        )
        SELECT territory_id, name, country_region_code, territory_group
        FROM staging.stg_sales_territory
        ON CONFLICT (territory_id) DO UPDATE SET
            territory_name = EXCLUDED.territory_name,
            country_region_code = EXCLUDED.country_region_code,
            territory_group = EXCLUDED.territory_group;
    """
    with pg_conn.cursor() as cur:
        cur.execute(sql)
        affected = cur.rowcount
    pg_conn.commit()
    print(f"[dim_sales_territory] {affected} linha(s) inserida(s)/atualizada(s).")


def load_dim_sales_person(pg_conn):
    
    sql = """
        INSERT INTO dw.dim_sales_person (
            sales_person_id, full_name, sales_quota, is_unknown_member
        )
        SELECT
            sp.business_entity_id,
            TRIM(CONCAT(per.first_name, ' ', per.last_name)),
            sp.sales_quota,
            FALSE
        FROM staging.stg_sales_person sp
        LEFT JOIN staging.stg_person per ON sp.business_entity_id = per.business_entity_id
        ON CONFLICT (sales_person_id) DO UPDATE SET
            full_name = EXCLUDED.full_name,
            sales_quota = EXCLUDED.sales_quota;
    """
    with pg_conn.cursor() as cur:
        cur.execute(sql)
        affected = cur.rowcount
    pg_conn.commit()
    print(f"[dim_sales_person] {affected} linha(s) inserida(s)/atualizada(s).")


def load_dim_promotion(pg_conn):
    sql = """
        INSERT INTO dw.dim_promotion (
            special_offer_id, description, discount_pct,
            promotion_type, promotion_category
        )
        SELECT special_offer_id, description, discount_pct, type, category
        FROM staging.stg_special_offer
        ON CONFLICT (special_offer_id) DO UPDATE SET
            description = EXCLUDED.description,
            discount_pct = EXCLUDED.discount_pct,
            promotion_type = EXCLUDED.promotion_type,
            promotion_category = EXCLUDED.promotion_category;
    """
    with pg_conn.cursor() as cur:
        cur.execute(sql)
        affected = cur.rowcount
    pg_conn.commit()
    print(f"[dim_promotion] {affected} linha(s) inserida(s)/atualizada(s).")


def run_dimension_loads():
    pg_conn = get_postgres_connection()
    print("=" * 70)
    print("CARGA DAS DIMENSÕES (Transform + Load, SCD Tipo 1)")
    print("=" * 70)
    try:
        load_dim_product(pg_conn)
        load_dim_customer(pg_conn)
        load_dim_sales_territory(pg_conn)
        load_dim_sales_person(pg_conn)
        load_dim_promotion(pg_conn)
    finally:
        pg_conn.close()
    print("=" * 70)
    print("CARGA DAS DIMENSÕES CONCLUÍDA")
    print("=" * 70)


if __name__ == "__main__":
    run_dimension_loads()
