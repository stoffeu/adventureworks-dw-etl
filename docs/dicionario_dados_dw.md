# Dicionário de Dados — Data Warehouse AdventureWorks (Star Schema)

## Visão Geral

- **Grão da fato:** um item de pedido de venda (uma linha de `Sales.SalesOrderDetail` no OLTP)
- **Padrão de modelagem:** Star Schema puro (sem snowflake)
- **Estratégia de SCD:** Tipo 1 (sobrescrita) em todas as dimensões
- **Schema no PostgreSQL:** `dw`
- **Schema de staging (área intermediária da ETL):** `staging`

---

## 1. Tabela Fato: `dw.fact_sales`

| Coluna | Tipo | Chave | Origem (OLTP) | Descrição |
|---|---|---|---|---|
| `sales_key` | BIGSERIAL | PK | — | Chave substituta da fato |
| `date_key` | INT | FK → `dim_date` | `SalesOrderHeader.OrderDate` | Data do pedido |
| `product_key` | INT | FK → `dim_product` | `SalesOrderDetail.ProductID` | Produto vendido |
| `customer_key` | INT | FK → `dim_customer` | `SalesOrderHeader.CustomerID` | Cliente comprador |
| `territory_key` | INT | FK → `dim_sales_territory` | `SalesOrderHeader.TerritoryID` | Território da venda |
| `sales_person_key` | INT | FK → `dim_sales_person` | `SalesOrderHeader.SalesPersonID` | Vendedor (ou membro "unknown" se venda online) |
| `promotion_key` | INT | FK → `dim_promotion` | `SalesOrderDetail.SpecialOfferID` | Promoção/oferta aplicada |
| `sales_order_id` | INT | Degenerate Dimension | `SalesOrderDetail.SalesOrderID` | Nº do pedido (rastreabilidade) |
| `sales_order_detail_id` | INT | Degenerate Dimension | `SalesOrderDetail.SalesOrderDetailID` | Nº da linha do pedido |
| `order_qty` | SMALLINT | Métrica | `SalesOrderDetail.OrderQty` | Quantidade vendida |
| `unit_price` | NUMERIC(19,4) | Métrica | `SalesOrderDetail.UnitPrice` | Preço unitário praticado |
| `unit_price_discount` | NUMERIC(10,4) | Métrica | `SalesOrderDetail.UnitPriceDiscount` | % de desconto aplicado |
| `line_total` | NUMERIC(19,4) | Métrica | `SalesOrderDetail.LineTotal` | Valor total da linha (receita) |
| `standard_cost` | NUMERIC(19,4) | Métrica | `Production.Product.StandardCost` | Custo padrão do produto (para margem) |
| `online_order_flag` | BOOLEAN | Métrica/atributo | `SalesOrderHeader.OnlineOrderFlag` | Indica canal (venda online x revenda) |
| `source_modified_date` | TIMESTAMP | Controle ETL | `SalesOrderDetail.ModifiedDate` | Usado para watermark incremental |
| `dw_load_date` | TIMESTAMP | Controle ETL | — | Data/hora em que o registro foi carregado no DW |

**Chave primária alternativa (natural key da fato):** `(sales_order_id, sales_order_detail_id)` — usada pela ETL para identificar se uma linha já existe (upsert).

---

## 2. Dimensão: `dw.dim_date`


| Coluna | Tipo | Chave | Descrição |
|---|---|---|---|
| `date_key` | INT | PK | Formato `YYYYMMDD` (ex: 20130715) |
| `full_date` | DATE | — | Data completa |
| `day` | SMALLINT | — | Dia do mês |
| `day_name` | VARCHAR(15) | — | Nome do dia da semana |
| `day_of_week` | SMALLINT | — | 1=domingo ... 7=sábado |
| `month` | SMALLINT | — | Número do mês (1–12) |
| `month_name` | VARCHAR(15) | — | Nome do mês |
| `quarter` | SMALLINT | — | Trimestre (1–4) |
| `year` | SMALLINT | — | Ano |
| `is_weekend` | BOOLEAN | — | Indica fim de semana |

---

## 3. Dimensão: `dw.dim_product`

| Coluna | Tipo | Chave | Origem (OLTP) | Descrição |
|---|---|---|---|---|
| `product_key` | SERIAL | PK | — | Chave substituta |
| `product_id` | INT | Natural Key (BK) | `Production.Product.ProductID` | Chave natural do produto |
| `product_name` | VARCHAR(100) | — | `Product.Name` | Nome do produto |
| `product_number` | VARCHAR(25) | — | `Product.ProductNumber` | Código do produto |
| `color` | VARCHAR(15) | — | `Product.Color` | Cor |
| `size` | VARCHAR(10) | — | `Product.Size` | Tamanho |
| `category_name` | VARCHAR(50) | — | `ProductCategory.Name` | Categoria (hierarquia nível 1) |
| `subcategory_name` | VARCHAR(50) | — | `ProductSubcategory.Name` | Subcategoria (hierarquia nível 2) |
| `list_price` | NUMERIC(19,4) | — | `Product.ListPrice` | Preço de tabela |
| `source_modified_date` | TIMESTAMP | Controle ETL | `Product.ModifiedDate` | Watermark incremental |
| `dw_load_date` | TIMESTAMP | Controle ETL | — | Data de carga no DW |

---

## 4. Dimensão: `dw.dim_customer`

| Coluna | Tipo | Chave | Origem (OLTP) | Descrição |
|---|---|---|---|---|
| `customer_key` | SERIAL | PK | — | Chave substituta |
| `customer_id` | INT | Natural Key (BK) | `Sales.Customer.CustomerID` | Chave natural do cliente |
| `person_name` | VARCHAR(150) | — | `Person.Person` (FirstName+LastName) | Nome completo (se pessoa física) |
| `store_name` | VARCHAR(150) | — | `Sales.Store.Name` | Nome da loja (se cliente for revendedor) |
| `account_number` | VARCHAR(15) | — | `Customer.AccountNumber` | Número de conta |
| `city` | VARCHAR(30) | — | `Person.Address.City` | Cidade |
| `state_province` | VARCHAR(50) | — | `Person.StateProvince.Name` | Estado/província |
| `country_region` | VARCHAR(50) | — | `Person.CountryRegion.Name` | País |
| `source_modified_date` | TIMESTAMP | Controle ETL | `Customer.ModifiedDate` | Watermark incremental |
| `dw_load_date` | TIMESTAMP | Controle ETL | — | Data de carga no DW |

---

## 5. Dimensão: `dw.dim_sales_territory`

| Coluna | Tipo | Chave | Origem (OLTP) | Descrição |
|---|---|---|---|---|
| `territory_key` | SERIAL | PK | — | Chave substituta |
| `territory_id` | INT | Natural Key (BK) | `Sales.SalesTerritory.TerritoryID` | Chave natural |
| `territory_name` | VARCHAR(50) | — | `SalesTerritory.Name` | Nome do território |
| `country_region_code` | VARCHAR(3) | — | `SalesTerritory.CountryRegionCode` | Código do país |
| `territory_group` | VARCHAR(50) | — | `SalesTerritory.Group` | Grupo/continente |

---

## 6. Dimensão: `dw.dim_sales_person`

| Coluna | Tipo | Chave | Origem (OLTP) | Descrição |
|---|---|---|---|---|
| `sales_person_key` | SERIAL | PK | — | Chave substituta |
| `sales_person_id` | INT | Natural Key (BK), nullable | `Sales.SalesPerson.BusinessEntityID` | Chave natural do vendedor |
| `full_name` | VARCHAR(150) | — | `Person.Person` | Nome do vendedor |
| `sales_quota` | NUMERIC(19,4) | — | `SalesPerson.SalesQuota` | Meta de vendas |
| `is_unknown_member` | BOOLEAN | — | — | `TRUE` para o registro genérico "Venda Online / Sem Vendedor" |



---

## 7. Dimensão: `dw.dim_promotion`

| Coluna | Tipo | Chave | Origem (OLTP) | Descrição |
|---|---|---|---|---|
| `promotion_key` | SERIAL | PK | — | Chave substituta |
| `special_offer_id` | INT | Natural Key (BK) | `Sales.SpecialOffer.SpecialOfferID` | Chave natural |
| `description` | VARCHAR(255) | — | `SpecialOffer.Description` | Descrição da promoção |
| `discount_pct` | NUMERIC(10,4) | — | `SpecialOffer.DiscountPct` | Percentual de desconto |
| `promotion_type` | VARCHAR(50) | — | `SpecialOffer.Type` | Tipo da promoção |
| `promotion_category` | VARCHAR(50) | — | `SpecialOffer.Category` | Categoria da promoção |


---

## 8. Tabela de Controle da ETL: `staging.etl_control`



| Coluna | Tipo | Descrição |
|---|---|---|
| `source_table` | VARCHAR(100) | Nome da tabela de origem (ex: `Sales.SalesOrderDetail`) |
| `last_extracted_timestamp` | TIMESTAMP | Último `ModifiedDate` processado com sucesso |
| `last_run_datetime` | TIMESTAMP | Data/hora da última execução da ETL |
| `rows_processed` | INT | Quantidade de linhas processadas na última execução |

---

## Relacionamentos (Star Schema)

```
dim_date ───────────────┐
dim_product ────────────┤
dim_customer ───────────┼──▶ fact_sales
dim_sales_territory ────┤
dim_sales_person ───────┤
dim_promotion ──────────┘
```


