

SQLSERVER_CONFIG = {
    "driver": "{ODBC Driver 17 for SQL Server}",
    "server": "localhost",
    "database": "AdventureWorks2016",
    "trusted_connection": "yes",  # Windows Authentication
}

def get_sqlserver_connection_string() -> str:
    cfg = SQLSERVER_CONFIG
    return (
        f"DRIVER={cfg['driver']};"
        f"SERVER={cfg['server']};"
        f"DATABASE={cfg['database']};"
        f"Trusted_Connection={cfg['trusted_connection']};"
        f"TrustServerCertificate=yes;"
    )



POSTGRES_CONFIG = {
    "host": "localhost",
    "port": 5439,
    "dbname": "adworks_db",
    "user": "postgres",
    "password": "123",
}
