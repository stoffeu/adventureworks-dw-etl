

from datetime import date, timedelta
import psycopg2
import psycopg2.extras

from db_connections import get_postgres_connection

DIAS_SEMANA_PT = ["Segunda-feira", "Terça-feira", "Quarta-feira", "Quinta-feira",
                   "Sexta-feira", "Sábado", "Domingo"]
MESES_PT = ["Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho", "Julho",
            "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"]


def generate_dates(start_date: date, end_date: date):
    rows = []
    current = start_date
    while current <= end_date:
        date_key = int(current.strftime("%Y%m%d"))
        day = current.day
        day_of_week_iso = current.isoweekday()  # 1=segunda ... 7=domingo
        day_name = DIAS_SEMANA_PT[day_of_week_iso - 1]
        month = current.month
        month_name = MESES_PT[month - 1]
        quarter = (month - 1) // 3 + 1
        year = current.year
        is_weekend = day_of_week_iso in (6, 7)

        rows.append((
            date_key, current, day, day_name, day_of_week_iso,
            month, month_name, quarter, year, is_weekend
        ))
        current += timedelta(days=1)
    return rows


def run(start_date: date = date(2010, 1, 1), end_date: date = date(2016, 12, 31)):
    rows = generate_dates(start_date, end_date)

    pg_conn = get_postgres_connection()
    try:
        with pg_conn.cursor() as cur:
            sql = """
                INSERT INTO dw.dim_date (
                    date_key, full_date, day, day_name, day_of_week,
                    month, month_name, quarter, year, is_weekend
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date_key) DO NOTHING
            """
            psycopg2.extras.execute_batch(cur, sql, rows, page_size=500)
        pg_conn.commit()
        print(f"dim_date populada com {len(rows)} datas "
              f"({start_date} a {end_date}).")
    finally:
        pg_conn.close()


if __name__ == "__main__":
    run()
