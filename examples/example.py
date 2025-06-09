import pymssql
import pandas as pd
from datetime import datetime, timedelta
import sys
from io import StringIO

def get_connection():
    server = 'mmconsultoria.database.windows.net'
    database = 'MMC_Clientes_1'
    username = 'mmcadmin'
    password = 'Elpadrino12$'
    port = 1433
    return pymssql.connect(server=server, user=username, password=password, database=database, port=port)

def get_week_dates(year, week_number):
    first_day = datetime(year, 1, 1)
    days_to_monday = (first_day.weekday()) % 7
    first_monday = first_day - timedelta(days=days_to_monday)
    start_date = first_monday + timedelta(weeks=week_number)
    end_date = start_date + timedelta(days=6)
    return start_date, end_date

def main():
    try:
        # Definir año y semana
        year = 2025
        week_number = 16

        # Obtener fechas de inicio y fin de la semana
        start_date, end_date = get_week_dates(year, week_number)
        print(f"Fechas de la semana {week_number} del {year}: Inicio = {start_date}, Fin = {end_date}")

        # Conectar a la base de datos
        conn = get_connection()
        cursor = conn.cursor()

        # Consulta SQL
        query = f"""
        SELECT PROYECTO, TAREA, SUM(DATEDIFF(MINUTE, TIEMPO_INICIAL, TIEMPO_FINAL)) AS TOTAL_MINUTOS
        FROM Registro_Tiempo
        WHERE TIEMPO_INICIAL >= '{start_date}' AND TIEMPO_INICIAL < '{end_date + timedelta(days=1)}'
        GROUP BY PROYECTO, TAREA
        """
        print(f"Consulta SQL: {query}")

        # Ejecutar consulta
        cursor.execute(query)
        rows = cursor.fetchall()

        # Procesar resultados
        df = pd.DataFrame(rows, columns=['PROYECTO', 'TAREA', 'TOTAL_MINUTOS'])
        print(df)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    main()