# app/database_operations.py

import pymssql
from utils import resource_path

# Azure SQL Database connection parameters
server = 'mmconsultoria.database.windows.net'
database = 'MMC_Clientes_1'
username = 'mmcadmin'
password = 'Elpadrino12$'
port = 1433

def get_connection():
    return pymssql.connect(server=server, user=username, password=password, database=database, port=port)

def add_project_task(project, task, showed):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        # Primero, verificamos si la combinación de proyecto y tarea ya existe
        cursor.execute("SELECT COUNT(*) FROM Proyectos_Tareas WHERE PROYECTO = %s AND TAREA = %s", (project, task))
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO Proyectos_Tareas (PROYECTO, TAREA, SHOWED) VALUES (%s, %s, %d)", (project, task, showed))
            conn.commit()
            print(f"Project '{project}' with task '{task}' added successfully.")
        else:
            print(f"Project '{project}' with task '{task}' already exists. Skipping.")
    except Exception as e:
        print(f"Error adding project and task: {e}")
        conn.rollback()
    finally:
        conn.close()

def add_time_record(project, task, start_time, end_time):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Registro_Tiempo (PROYECTO, TAREA, TIEMPO_INICIAL, TIEMPO_FINAL)
            VALUES (%s, %s, %s, %s)
        """, (project, task, start_time, end_time))
        conn.commit()
        print("Time record added successfully.")
    except Exception as e:
        print(f"Error adding time record: {e}")
        conn.rollback()
    finally:
        conn.close()

def load_projects():
    conn = get_connection()
    cursor = conn.cursor()
    projects = {}
    try:
        cursor.execute("SELECT PROYECTO, TAREA FROM Proyectos_Tareas WHERE SHOWED = 1")
        for row in cursor.fetchall():
            project, task = row
            if project not in projects:
                projects[project] = set()
            projects[project].add(task)
    except Exception as e:
        print(f"Error loading projects and tasks: {e}")
    finally:
        conn.close()
    return projects