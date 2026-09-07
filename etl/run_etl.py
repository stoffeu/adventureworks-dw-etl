

import sys
import time

from extract import run_extraction
from load_dimensions import run_dimension_loads
from load_fact import run_fact_load


def main():
    start = time.time()
    print("\n" + "#" * 70)
    print("#  ETL INCREMENTAL - DATA WAREHOUSE ADVENTUREWORKS")
    print("#" * 70 + "\n")

    try:
        run_extraction()
        run_dimension_loads()
        run_fact_load()
    except Exception as exc:
        print(f"\n[ERRO] A ETL foi interrompida: {exc}", file=sys.stderr)
        raise

    elapsed = time.time() - start
    print(f"\nETL concluída com sucesso em {elapsed:.2f} segundos.")


if __name__ == "__main__":
    main()
