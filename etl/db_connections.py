

import pyodbc
import psycopg2
from config import get_sqlserver_connection_string, POSTGRES_CONFIG


def get_sqlserver_connection():
    conn_str = get_sqlserver_connection_string()
    return pyodbc.connect(conn_str)


def get_postgres_connection():
    return psycopg2.connect(**POSTGRES_CONFIG)
