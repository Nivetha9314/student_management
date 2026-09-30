import os
import pyodbc
from dotenv import load_dotenv

load_dotenv()


def get_connection():
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_DATABASE")
    configured_driver = os.getenv("DB_DRIVER")
    installed_drivers = pyodbc.drivers()

    candidate_drivers = []
    if configured_driver:
        candidate_drivers.append(configured_driver)

    candidate_drivers.extend([
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server",
        "ODBC Driver 11 for SQL Server",
        "SQL Server Native Client 11.0",
        "SQL Server",
    ])

    driver = next((d for d in candidate_drivers if d in installed_drivers), None)

    if not driver:
        raise RuntimeError(
            "No SQL Server ODBC driver is installed on this machine. "
            f"Installed drivers: {installed_drivers}"
        )

    connection_string = (
        f"DRIVER={{{driver}}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"Trusted_Connection=yes;"
        f"TrustServerCertificate=yes;"
    )

    return pyodbc.connect(connection_string)
