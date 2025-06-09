# app/database_tasks.py
import pymssql
from database_operations import get_connection

def add_daily_task(task, project, date):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO Tareas_diarias (Tarea, Proyecto, Fecha)
            VALUES (%s, %s, %s)
        """, (task, project, date))
        conn.commit()
        print(f"Tarea '{task}' añadida al proyecto '{project}' para la fecha '{date}'")
    except Exception as e:
        print(f"Error al añadir tarea: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_daily_tasks(date):
    conn = get_connection()
    cursor = conn.cursor()
    tasks = []
    try:
        cursor.execute("""
            SELECT Tarea, Proyecto, Prioridad, Terminado, Tiempo_Maximo
            FROM Tareas_diarias
            WHERE Fecha = %s
        """, (date,))
        for row in cursor.fetchall():
            task, project, priority, completed, max_time = row
            tasks.append({
                "Tarea": task,
                "Proyecto": project,
                "Prioridad": priority,
                "Terminado": completed,
                "Fecha": date,
                "Tiempo_Maximo": max_time
            })
    except Exception as e:
        print(f"Error al obtener tareas: {e}")
    finally:
        conn.close()
    return tasks

def update_task_priority(task, project, date, priority, time_maximo, terminado):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            UPDATE Tareas_diarias
            SET Prioridad = %s, Tiempo_Maximo = %s, Terminado = %d
            WHERE Tarea = %s AND Proyecto = %s AND Fecha = %s
        """, (priority, time_maximo, terminado, task, project, date))
        conn.commit()
        print(f"Prioridad de la tarea '{task}' actualizada a '{priority}', tiempo máximo a '{time_maximo}', y terminado a '{terminado}'")
    except Exception as e:
        print(f"Error al actualizar la prioridad, tiempo máximo y terminado: {e}")
        conn.rollback()
    finally:
        conn.close()

def get_tiempo_hecho_por_fecha(fecha):
    conn = get_connection()
    cursor = conn.cursor()
    tiempos_hechos = {}
    try:
        cursor.execute("""
            SELECT TAREA, PROYECTO, SUM(DATEDIFF(second, TIEMPO_INICIAL, TIEMPO_FINAL))
            FROM Registro_Tiempo
            WHERE CONVERT(DATE, TIEMPO_INICIAL) = %s
            GROUP BY TAREA, PROYECTO
        """, (fecha,))
        for row in cursor.fetchall():
            tarea, proyecto, tiempo = row
            if proyecto not in tiempos_hechos:
                tiempos_hechos[proyecto] = {}
            tiempos_hechos[proyecto][tarea] = tiempo
    except Exception as e:
        print(f"Error al obtener tiempos hechos: {e}")
    finally:
        conn.close()
    return tiempos_hechos