

from datetime import datetime
import pyodbc
import psycopg2
import psycopg2.extras

from db_connections import get_sqlserver_connection, get_postgres_connection



EXTRACTIONS = [
    {
        "source_table": "Sales.SalesOrderHeader",
        "staging_table": "staging.stg_sales_order_header",
        "pk_columns": ["sales_order_id"],
        "query": """
            SELECT SalesOrderID, OrderDate, CustomerID, SalesPersonID,
                   TerritoryID, OnlineOrderFlag, ModifiedDate
            FROM Sales.SalesOrderHeader
            WHERE ModifiedDate > ?
        """,
        "columns": ["sales_order_id", "order_date", "customer_id",
                    "sales_person_id", "territory_id", "online_order_flag",
                    "modified_date"],
    },
    {
        "source_table": "Sales.SalesOrderDetail",
        "staging_table": "staging.stg_sales_order_detail",
        "pk_columns": ["sales_order_id", "sales_order_detail_id"],
        "query": """
            SELECT SalesOrderID, SalesOrderDetailID, ProductID, SpecialOfferID,
                   OrderQty, UnitPrice, UnitPriceDiscount, LineTotal, ModifiedDate
            FROM Sales.SalesOrderDetail
            WHERE ModifiedDate > ?
        """,
        "columns": ["sales_order_id", "sales_order_detail_id", "product_id",
                    "special_offer_id", "order_qty", "unit_price",
                    "unit_price_discount", "line_total", "modified_date"],
    },
    {
        "source_table": "Production.Product",
        "staging_table": "staging.stg_product",
        "pk_columns": ["product_id"],
        "query": """
            SELECT ProductID, Name, ProductNumber, Color, Size,
                   StandardCost, ListPrice, ProductSubcategoryID, ModifiedDate
            FROM Production.Product
            WHERE ModifiedDate > ?
        """,
        "columns": ["product_id", "product_name", "product_number", "color",
                    "size", "standard_cost", "list_price",
                    "product_subcategory_id", "modified_date"],
    },
    {
        "source_table": "Production.ProductSubcategory",
        "staging_table": "staging.stg_product_subcategory",
        "pk_columns": ["product_subcategory_id"],
        "query": """
            SELECT ProductSubcategoryID, ProductCategoryID, Name, ModifiedDate
            FROM Production.ProductSubcategory
            WHERE ModifiedDate > ?
        """,
        "columns": ["product_subcategory_id", "product_category_id", "name",
                    "modified_date"],
    },
    {
        "source_table": "Production.ProductCategory",
        "staging_table": "staging.stg_product_category",
        "pk_columns": ["product_category_id"],
        "query": """
            SELECT ProductCategoryID, Name, ModifiedDate
            FROM Production.ProductCategory
            WHERE ModifiedDate > ?
        """,
        "columns": ["product_category_id", "name", "modified_date"],
    },
    {
        "source_table": "Sales.Customer",
        "staging_table": "staging.stg_customer",
        "pk_columns": ["customer_id"],
        "query": """
            SELECT CustomerID, PersonID, StoreID, AccountNumber, ModifiedDate
            FROM Sales.Customer
            WHERE ModifiedDate > ?
        """,
        "columns": ["customer_id", "person_id", "store_id", "account_number",
                    "modified_date"],
    },
    {
        "source_table": "Person.Person",
        "staging_table": "staging.stg_person",
        "pk_columns": ["business_entity_id"],
        "query": """
            SELECT BusinessEntityID, FirstName, LastName, ModifiedDate
            FROM Person.Person
            WHERE ModifiedDate > ?
        """,
        "columns": ["business_entity_id", "first_name", "last_name",
                    "modified_date"],
    },
    {
        "source_table": "Sales.Store",
        "staging_table": "staging.stg_store",
        "pk_columns": ["business_entity_id"],
        "query": """
            SELECT BusinessEntityID, Name, ModifiedDate
            FROM Sales.Store
            WHERE ModifiedDate > ?
        """,
        "columns": ["business_entity_id", "name", "modified_date"],
    },
    {
        "source_table": "Person.Address",
        "staging_table": "staging.stg_address",
        "pk_columns": ["address_id"],
        "query": """
            SELECT AddressID, City, StateProvinceID, ModifiedDate
            FROM Person.Address
            WHERE ModifiedDate > ?
        """,
        "columns": ["address_id", "city", "state_province_id", "modified_date"],
    },
    {
        "source_table": "Person.BusinessEntityAddress",
        "staging_table": "staging.stg_business_entity_address",
        "pk_columns": ["business_entity_id", "address_id"],
        "query": """
            SELECT BusinessEntityID, AddressID, ModifiedDate
            FROM Person.BusinessEntityAddress
            WHERE ModifiedDate > ?
        """,
        "columns": ["business_entity_id", "address_id", "modified_date"],
    },
    {
        "source_table": "Person.StateProvince",
        "staging_table": "staging.stg_state_province",
        "pk_columns": ["state_province_id"],
        "query": """
            SELECT StateProvinceID, Name, CountryRegionCode, ModifiedDate
            FROM Person.StateProvince
            WHERE ModifiedDate > ?
        """,
        "columns": ["state_province_id", "name", "country_region_code",
                    "modified_date"],
    },
    {
        "source_table": "Person.CountryRegion",
        "staging_table": "staging.stg_country_region",
        "pk_columns": ["country_region_code"],
        "query": """
            SELECT CountryRegionCode, Name, ModifiedDate
            FROM Person.CountryRegion
            WHERE ModifiedDate > ?
        """,
        "columns": ["country_region_code", "name", "modified_date"],
    },
    {
        "source_table": "Sales.SalesTerritory",
        "staging_table": "staging.stg_sales_territory",
        "pk_columns": ["territory_id"],
        "query": """
            SELECT TerritoryID, Name, CountryRegionCode, [Group], ModifiedDate
            FROM Sales.SalesTerritory
            WHERE ModifiedDate > ?
        """,
        "columns": ["territory_id", "name", "country_region_code",
                    "territory_group", "modified_date"],
    },
    {
        "source_table": "Sales.SalesPerson",
        "staging_table": "staging.stg_sales_person",
        "pk_columns": ["business_entity_id"],
        "query": """
            SELECT BusinessEntityID, SalesQuota, ModifiedDate
            FROM Sales.SalesPerson
            WHERE ModifiedDate > ?
        """,
        "columns": ["business_entity_id", "sales_quota", "modified_date"],
    },
    {
        "source_table": "Sales.SpecialOffer",
        "staging_table": "staging.stg_special_offer",
        "pk_columns": ["special_offer_id"],
        "query": """
            SELECT SpecialOfferID, Description, DiscountPct, [Type], Category,
                   ModifiedDate
            FROM Sales.SpecialOffer
            WHERE ModifiedDate > ?
        """,
        "columns": ["special_offer_id", "description", "discount_pct",
                    "type", "category", "modified_date"],
    },
]


def get_watermark(pg_conn, source_table: str) -> datetime:
    """Lê o último ModifiedDate processado com sucesso para a tabela dada."""
    with pg_conn.cursor() as cur:
        cur.execute(
            "SELECT last_extracted_timestamp FROM staging.etl_control "
            "WHERE source_table = %s",
            (source_table,),
        )
        row = cur.fetchone()
        return row[0] if row else datetime(1900, 1, 1)


def update_watermark(pg_conn, source_table: str, new_watermark: datetime, rows_processed: int):
    """Atualiza o watermark após uma extração bem-sucedida."""
    with pg_conn.cursor() as cur:
        cur.execute(
            """
            UPDATE staging.etl_control
            SET last_extracted_timestamp = %s,
                last_run_datetime = now(),
                rows_processed = %s
            WHERE source_table = %s
            """,
            (new_watermark, rows_processed, source_table),
        )
    pg_conn.commit()


def upsert_staging_rows(pg_conn, staging_table: str, columns: list, pk_columns: list, rows: list):
    """
    Insere as linhas extraídas na tabela de staging do PostgreSQL, usando
    upsert (INSERT ... ON CONFLICT DO UPDATE) para lidar tanto com registros
    novos quanto com registros modificados.
    """
    if not rows:
        return

    cols_sql = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))
    conflict_cols = ", ".join(pk_columns)
    update_cols = [c for c in columns if c not in pk_columns]
    update_sql = ", ".join([f"{c} = EXCLUDED.{c}" for c in update_cols])

    sql = f"""
        INSERT INTO {staging_table} ({cols_sql})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_cols})
        DO UPDATE SET {update_sql}
    """

    with pg_conn.cursor() as cur:
        psycopg2.extras.execute_batch(cur, sql, rows, page_size=500)
    pg_conn.commit()


def run_extraction():
    """Executa a extração incremental de todas as tabelas configuradas."""
    sql_conn = get_sqlserver_connection()
    pg_conn = get_postgres_connection()

    print("=" * 70)
    print("INICIANDO EXTRAÇÃO INCREMENTAL (SQL Server -> Staging PostgreSQL)")
    print("=" * 70)

    try:
        for extraction in EXTRACTIONS:
            source_table = extraction["source_table"]
            staging_table = extraction["staging_table"]
            pk_columns = extraction["pk_columns"]
            columns = extraction["columns"]

            watermark = get_watermark(pg_conn, source_table)
            print(f"\n[{source_table}] watermark atual: {watermark}")

            cursor = sql_conn.cursor()
            cursor.execute(extraction["query"], watermark)
            rows = cursor.fetchall()
            rows = [tuple(row) for row in rows]

            if not rows:
                print(f"[{source_table}] nenhuma linha nova/modificada. Nada a fazer.")
                continue

            # Última coluna de cada linha é sempre modified_date, conforme
            # definido nas queries de extração acima.
            modified_date_idx = columns.index("modified_date")
            new_watermark = max(row[modified_date_idx] for row in rows)

            upsert_staging_rows(pg_conn, staging_table, columns, pk_columns, rows)
            update_watermark(pg_conn, source_table, new_watermark, len(rows))

            print(f"[{source_table}] {len(rows)} linha(s) processada(s). "
                  f"Novo watermark: {new_watermark}")

    finally:
        sql_conn.close()
        pg_conn.close()

    print("\n" + "=" * 70)
    print("EXTRAÇÃO CONCLUÍDA")
    print("=" * 70)


if __name__ == "__main__":
    run_extraction()
