
-- DDL — Data Warehouse AdventureWorks (Star Schema)
-- Banco de destino: PostgreSQL


DROP SCHEMA IF EXISTS dw CASCADE;
DROP SCHEMA IF EXISTS staging CASCADE;

CREATE SCHEMA dw;
CREATE SCHEMA staging;

COMMENT ON SCHEMA dw IS 'Data Warehouse dimensional - Star Schema de vendas AdventureWorks';
COMMENT ON SCHEMA staging IS 'Área intermediária de extração (dados brutos do OLTP) e controle de ETL';



CREATE TABLE staging.stg_sales_order_header (
    sales_order_id       INT PRIMARY KEY,
    order_date           TIMESTAMP NOT NULL,
    customer_id          INT NOT NULL,
    sales_person_id      INT NULL,
    territory_id         INT NULL,
    online_order_flag    BOOLEAN NOT NULL,
    modified_date         TIMESTAMP NOT NULL
);

CREATE TABLE staging.stg_sales_order_detail (
    sales_order_id        INT NOT NULL,
    sales_order_detail_id INT NOT NULL,
    product_id            INT NOT NULL,
    special_offer_id      INT NOT NULL,
    order_qty             SMALLINT NOT NULL,
    unit_price             NUMERIC(19,4) NOT NULL,
    unit_price_discount   NUMERIC(10,4) NOT NULL DEFAULT 0,
    line_total             NUMERIC(19,4) NOT NULL,
    modified_date          TIMESTAMP NOT NULL,
    PRIMARY KEY (sales_order_id, sales_order_detail_id)
);

CREATE TABLE staging.stg_product (
    product_id           INT PRIMARY KEY,
    product_name          VARCHAR(100) NOT NULL,
    product_number        VARCHAR(25) NOT NULL,
    color                 VARCHAR(15),
    size                  VARCHAR(10),
    standard_cost         NUMERIC(19,4) NOT NULL,
    list_price            NUMERIC(19,4) NOT NULL,
    product_subcategory_id INT NULL,
    modified_date          TIMESTAMP NOT NULL
);

CREATE TABLE staging.stg_product_subcategory (
    product_subcategory_id INT PRIMARY KEY,
    product_category_id    INT NOT NULL,
    name                    VARCHAR(50) NOT NULL,
    modified_date            TIMESTAMP NOT NULL
);

CREATE TABLE staging.stg_product_category (
    product_category_id INT PRIMARY KEY,
    name                 VARCHAR(50) NOT NULL,
    modified_date         TIMESTAMP NOT NULL
);

CREATE TABLE staging.stg_customer (
    customer_id     INT PRIMARY KEY,
    person_id       INT NULL,
    store_id        INT NULL,
    account_number  VARCHAR(15) NOT NULL,
    modified_date    TIMESTAMP NOT NULL
);

CREATE TABLE staging.stg_person (
    business_entity_id INT PRIMARY KEY,
    first_name          VARCHAR(50) NOT NULL,
    last_name           VARCHAR(50) NOT NULL,
    modified_date        TIMESTAMP NOT NULL
);

CREATE TABLE staging.stg_store (
    business_entity_id INT PRIMARY KEY,
    name                VARCHAR(150) NOT NULL,
    modified_date        TIMESTAMP NOT NULL
);

CREATE TABLE staging.stg_address (
    address_id       INT PRIMARY KEY,
    city             VARCHAR(30) NOT NULL,
    state_province_id INT NOT NULL,
    modified_date     TIMESTAMP NOT NULL
);

CREATE TABLE staging.stg_business_entity_address (
    business_entity_id INT NOT NULL,
    address_id          INT NOT NULL,
    modified_date         TIMESTAMP NOT NULL,
    PRIMARY KEY (business_entity_id, address_id)
);

CREATE TABLE staging.stg_state_province (
    state_province_id INT PRIMARY KEY,
    name               VARCHAR(50) NOT NULL,
    country_region_code VARCHAR(3) NOT NULL,
    modified_date        TIMESTAMP NOT NULL
);

CREATE TABLE staging.stg_country_region (
    country_region_code VARCHAR(3) PRIMARY KEY,
    name                  VARCHAR(50) NOT NULL,
    modified_date          TIMESTAMP NOT NULL
);

CREATE TABLE staging.stg_sales_territory (
    territory_id         INT PRIMARY KEY,
    name                  VARCHAR(50) NOT NULL,
    country_region_code  VARCHAR(3) NOT NULL,
    territory_group       VARCHAR(50) NOT NULL,
    modified_date          TIMESTAMP NOT NULL
);

CREATE TABLE staging.stg_sales_person (
    business_entity_id INT PRIMARY KEY,
    sales_quota         NUMERIC(19,4),
    modified_date         TIMESTAMP NOT NULL
);

CREATE TABLE staging.stg_special_offer (
    special_offer_id INT PRIMARY KEY,
    description       VARCHAR(255) NOT NULL,
    discount_pct      NUMERIC(10,4) NOT NULL,
    type              VARCHAR(50),
    category          VARCHAR(50),
    modified_date       TIMESTAMP NOT NULL
);



CREATE TABLE staging.etl_control (
    source_table              VARCHAR(100) PRIMARY KEY,
    last_extracted_timestamp  TIMESTAMP NOT NULL DEFAULT '1900-01-01',
    last_run_datetime         TIMESTAMP,
    rows_processed             INT DEFAULT 0
);




INSERT INTO staging.etl_control (source_table, last_extracted_timestamp) VALUES
    ('Sales.SalesOrderHeader', '1900-01-01'),
    ('Sales.SalesOrderDetail', '1900-01-01'),
    ('Production.Product', '1900-01-01'),
    ('Production.ProductSubcategory', '1900-01-01'),
    ('Production.ProductCategory', '1900-01-01'),
    ('Sales.Customer', '1900-01-01'),
    ('Person.Person', '1900-01-01'),
    ('Sales.Store', '1900-01-01'),
    ('Person.Address', '1900-01-01'),
    ('Person.BusinessEntityAddress', '1900-01-01'),
    ('Person.StateProvince', '1900-01-01'),
    ('Person.CountryRegion', '1900-01-01'),
    ('Sales.SalesTerritory', '1900-01-01'),
    ('Sales.SalesPerson', '1900-01-01'),
    ('Sales.SpecialOffer', '1900-01-01');







CREATE TABLE dw.dim_date (
    date_key      INT PRIMARY KEY,          
    full_date     DATE NOT NULL UNIQUE,
    day           SMALLINT NOT NULL,
    day_name      VARCHAR(15) NOT NULL,
    day_of_week   SMALLINT NOT NULL,
    month         SMALLINT NOT NULL,
    month_name    VARCHAR(15) NOT NULL,
    quarter       SMALLINT NOT NULL,
    year          SMALLINT NOT NULL,
    is_weekend    BOOLEAN NOT NULL
);





CREATE TABLE dw.dim_product (
    product_key           SERIAL PRIMARY KEY,
    product_id            INT NOT NULL UNIQUE,   
    product_name          VARCHAR(100) NOT NULL,
    product_number        VARCHAR(25) NOT NULL,
    color                 VARCHAR(15),
    size                  VARCHAR(10),
    category_name          VARCHAR(50),
    subcategory_name       VARCHAR(50),
    list_price             NUMERIC(19,4),
    source_modified_date   TIMESTAMP NOT NULL,
    dw_load_date            TIMESTAMP NOT NULL DEFAULT now()
);




CREATE TABLE dw.dim_customer (
    customer_key          SERIAL PRIMARY KEY,
    customer_id           INT NOT NULL UNIQUE,   
    person_name            VARCHAR(150),
    store_name             VARCHAR(150),
    account_number         VARCHAR(15),
    city                   VARCHAR(30),
    state_province         VARCHAR(50),
    country_region         VARCHAR(50),
    source_modified_date   TIMESTAMP NOT NULL,
    dw_load_date            TIMESTAMP NOT NULL DEFAULT now()
);




CREATE TABLE dw.dim_sales_territory (
    territory_key         SERIAL PRIMARY KEY,
    territory_id          INT NOT NULL UNIQUE,   
    territory_name         VARCHAR(50) NOT NULL,
    country_region_code   VARCHAR(3),
    territory_group        VARCHAR(50)
);




CREATE TABLE dw.dim_sales_person (
    sales_person_key      SERIAL PRIMARY KEY,
    sales_person_id       INT UNIQUE,            
    full_name              VARCHAR(150),
    sales_quota            NUMERIC(19,4),
    is_unknown_member      BOOLEAN NOT NULL DEFAULT FALSE
);

-- Registro fixo "unknown member"
INSERT INTO dw.dim_sales_person (sales_person_key, sales_person_id, full_name, sales_quota, is_unknown_member)
OVERRIDING SYSTEM VALUE
VALUES (-1, NULL, 'N/A - Venda Online', NULL, TRUE);

-- Garante que o próximo valor gerado pelo SERIAL não colida com o -1
SELECT setval(pg_get_serial_sequence('dw.dim_sales_person', 'sales_person_key'), 1, false);




CREATE TABLE dw.dim_promotion (
    promotion_key         SERIAL PRIMARY KEY,
    special_offer_id      INT NOT NULL UNIQUE,   -- Natural key (BK)
    description            VARCHAR(255),
    discount_pct           NUMERIC(10,4),
    promotion_type         VARCHAR(50),
    promotion_category     VARCHAR(50)
);




CREATE TABLE dw.fact_sales (
    sales_key              BIGSERIAL PRIMARY KEY,

    date_key               INT NOT NULL REFERENCES dw.dim_date(date_key),
    product_key            INT NOT NULL REFERENCES dw.dim_product(product_key),
    customer_key           INT NOT NULL REFERENCES dw.dim_customer(customer_key),
    territory_key          INT NOT NULL REFERENCES dw.dim_sales_territory(territory_key),
    sales_person_key       INT NOT NULL REFERENCES dw.dim_sales_person(sales_person_key),
    promotion_key          INT NOT NULL REFERENCES dw.dim_promotion(promotion_key),

    sales_order_id         INT NOT NULL,          
    sales_order_detail_id  INT NOT NULL,          

    order_qty              SMALLINT NOT NULL,
    unit_price              NUMERIC(19,4) NOT NULL,
    unit_price_discount     NUMERIC(10,4) NOT NULL DEFAULT 0,
    line_total               NUMERIC(19,4) NOT NULL,
    standard_cost            NUMERIC(19,4) NOT NULL,
    online_order_flag        BOOLEAN NOT NULL,

    source_modified_date     TIMESTAMP NOT NULL,   
    dw_load_date              TIMESTAMP NOT NULL DEFAULT now(),

    
    CONSTRAINT uq_fact_sales_natural_key UNIQUE (sales_order_id, sales_order_detail_id)
);



CREATE INDEX idx_fact_sales_date ON dw.fact_sales(date_key);
CREATE INDEX idx_fact_sales_product ON dw.fact_sales(product_key);
CREATE INDEX idx_fact_sales_customer ON dw.fact_sales(customer_key);
CREATE INDEX idx_fact_sales_territory ON dw.fact_sales(territory_key);
CREATE INDEX idx_fact_sales_salesperson ON dw.fact_sales(sales_person_key);
CREATE INDEX idx_fact_sales_promotion ON dw.fact_sales(promotion_key);






