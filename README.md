# Data Warehouse AdventureWorks — OLAP & ETL Incremental

Projeto acadêmico da disciplina de Engenharia de Dados (Unisales) — construção de um Data Warehouse dimensional (Star Schema) a partir do banco transacional AdventureWorks2016, com ETL incremental em Python.

## Objetivo

Modelar e implementar um Data Warehouse de vendas seguindo o padrão **Star Schema**, com uma ETL **incremental** (baseada em watermark) responsável por extrair dados do AdventureWorks2016 (SQL Server), transformá-los e carregá-los no PostgreSQL.

## Arquitetura

```
SQL Server (AdventureWorks2016 - OLTP)
        │
        │  extração incremental (watermark por ModifiedDate)
        ▼
PostgreSQL - schema "staging"
        │
        │  transformação (joins, hierarquias, resolução de chaves)
        ▼
PostgreSQL - schema "dw" (Star Schema)
        ├── dim_date
        ├── dim_product
        ├── dim_customer
        ├── dim_sales_territory
        ├── dim_sales_person
        ├── dim_promotion
        └── fact_sales
```

## Estrutura do repositório

| Pasta | Conteúdo |
|---|---|
| `ddl/` | Script de criação dos schemas `staging` e `dw` no PostgreSQL |
| `etl/` | ETL incremental em Python (extração, transformação, carga) |
| `sql_kpis/` | Consultas SQL que comprovam os 10 indicadores (KPIs) propostos |
| `diagrama/` | Diagrama do modelo Star Schema (Draw.io + imagem) |
| `docs/` | Dicionário de dados completo do Data Warehouse |

## Star Schema

Grão da fato: **um item de pedido de venda** (uma linha de `Sales.SalesOrderDetail`).

Ver diagrama completo em [`diagrama/star_schema_diagram.png`](diagrama/star_schema_diagram.png) e dicionário de dados em [`docs/dicionario_dados_dw.md`](docs/dicionario_dados_dw.md).

## Estratégia de ETL incremental

A ETL utiliza **watermark baseado em `ModifiedDate`** (coluna presente nas tabelas de origem do AdventureWorks). A cada execução:

1. Consulta o último `ModifiedDate` processado com sucesso (armazenado em `staging.etl_control`);
2. Extrai do SQL Server apenas os registros com `ModifiedDate` maior que o watermark;
3. Faz upsert no schema `staging` do PostgreSQL;
4. Transforma e carrega as dimensões (SCD Tipo 1) e a tabela fato, também de forma incremental (upsert por chave natural).

Instruções completas de instalação e execução em [`etl/README.md`](etl/README.md).

## 10 Indicadores (KPIs) implementados

1. Receita total de vendas por período
2. Ticket médio por pedido
3. Quantidade vendida por categoria de produto
4. Top 10 produtos por receita
5. Receita por território de vendas
6. Desempenho de vendas por vendedor
7. Receita por canal de venda (Online vs Revenda)
8. Impacto de descontos/promoções na receita
9. Margem bruta estimada por categoria
10. Novos clientes por período

Consultas completas em [`sql_kpis/02_kpis_sql.sql`](sql_kpis/02_kpis_sql.sql).

## Tecnologias utilizadas

- **SQL Server** — banco de origem (OLTP), AdventureWorks2016
- **PostgreSQL** — Data Warehouse (staging + dw)
- **Python** (`pyodbc`, `psycopg2`) — ETL incremental
- **Draw.io** — diagramação do modelo dimensional

## Autor(es)

- [Breno Souza Peixoto, Estevão Cunha de Sá Viana,Kaike Stofel de Oliveira Lima, Thiago Campos Xavier ] — [curso/instituição]

## Referências

- Microsoft. *AdventureWorks sample databases*. Disponível em: https://learn.microsoft.com/pt-br/sql/samples/adventureworks-install-configure
- KIMBALL, Ralph; ROSS, Margy. *The Data Warehouse Toolkit*.
