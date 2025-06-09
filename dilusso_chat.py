# app/dilusso_chat.py

from PyQt5.QtWidgets import QDialog, QTextEdit, QLineEdit, QPushButton, QVBoxLayout
from PyQt5.QtCore import Qt
from openai import OpenAI
import pandas as pd
from io import StringIO
import sys
from datetime import datetime
from database_operations import get_connection
import pymssql

class DilussoChat(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Chat con Dilusso")
        self.setGeometry(100, 100, 600, 800)

        layout = QVBoxLayout()

        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        layout.addWidget(self.chat_display)

        self.input_field = QLineEdit()
        layout.addWidget(self.input_field)

        self.send_button = QPushButton("Enviar")
        self.send_button.clicked.connect(self.send_message)
        layout.addWidget(self.send_button)

        self.setLayout(layout)
        #l6KsPnUXDFyC6aJ6hD17BgUTIoltvdeI
        self.client = OpenAI(
            api_key='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'
        )
        self.client1 = OpenAI(
            api_key='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'
        )

        self.MODEL = "gpt-4o-mini"
        self.MODEL1 = "gpt-4o-mini"

        self.messages = [
            {"role": "system", "content": self.get_system_message()}
        ]

        self.chat_display.append("Dilusso: Hola, soy Dilusso. ¿En qué puedo ayudarte?")

    def get_current_date(self):
        return datetime.now().strftime("%d/%m/%Y")

    def get_system_message(self):
        return f"""
        Eres un asistente llamado Dilusso.
        
        La fecha actual SIEMPRE debe ser {self.get_current_date()}.
        
        Tu propósito es asistir a José Huaylinos Guerrero, el cual es el Jefe de la Compañia Scieluxe
        
        Eres experto en análisis de datos usando la libreria Pandas de Python
        
        Eres un experto estadístico
        
        Siempre estudia el contexto en el que estamos, memorizate las fechas y horas en que trabajamos. Nunca te olvides de
        las fechas en que estamos trabajando a menos que se te diga que se cambie la fecha.
        """

    def send_message(self):
        user_input = self.input_field.text()
        self.chat_display.append(f"Tú: {user_input}")
        self.input_field.clear()

        response = self.generate_response(user_input)
        self.chat_display.append(f"Dilusso: {response}")

    def generate_response(self, user_input):
        analysis_prompt = f"""
        Determina si la siguiente consulta requiere un análisis de datos o no.
        Responde solo con 'SI' o 'NO'.
        Consulta: {user_input}
        """
        
        analysis_needed_response = self.client1.chat.completions.create(
            model=self.MODEL1,
            messages=[{"role": "system", "content": "Eres un asistente que determina si una consulta requiere análisis de datos."},
                    {"role": "user", "content": analysis_prompt}],
            temperature=0,
        )
        
        print('Imprimiendo la respuesta de si se necesita análisis o no')
        print("Respuesta de análisis:", analysis_needed_response.choices[0].message.content.strip())
        """ print(analysis_needed_response)"""
        analysis_needed = analysis_needed_response.choices[0].message.content.strip().upper() == 'SI'
        
        if analysis_needed:
            # Add current date information to the prompt
            current_date = datetime.now()
            code_prompt = f"""
                Genera código Python completo para analizar los datos según la siguiente consulta.
                Incluye TODAS las importaciones necesarias al inicio del código.
                
                La fecha actual es {current_date.strftime("%Y-%m-%d")} y estamos en la semana {current_date.strftime("%U")} del año {current_date.year}.
                
                IMPORTANTE: Para análisis por fechas o semanas:
                
                1. Para cálculos de semanas específicas (como "semana X del año Y"), usa esta función:
                ```
                    # Crea una fecha para el primer día del año
                    first_day = datetime(year, 1, 1)
                    # Ajusta al primer día de la semana (lunes)
                    days_to_monday = (first_day.weekday()) % 7
                    first_monday = first_day - timedelta(days=days_to_monday)
                    # Avanza hasta la semana deseada
                    start_date = first_monday + timedelta(weeks=week_number)
                    end_date = start_date + timedelta(days=6)
                    return start_date, end_date
                ```
                
                2. Al filtrar datos en SQL, usa preferentemente rangos inclusivos/exclusivos:
                WHERE TIEMPO_INICIAL >= 'fecha_inicio' AND TIEMPO_INICIAL < 'fecha_fin+1_dia'
                
                3. Siempre imprime las fechas de inicio y fin para fines de depuración.

                4. NUNCA USES CON CODIGO SIMILAR A "if __name__ == '__main__':" en el código generado.".
                
                
                El código debe incluir estas importaciones y usar la conexión existente:
                
                import pymssql
                import pandas as pd
                from datetime import datetime, timedelta
                import sys
                from io import StringIO
                
                La conexión a la base de datos ya está configurada con estos parámetros:
                server = 'mmconsultoria.database.windows.net'
                database = 'MMC_Clientes_1'
                username = 'mmcadmin'
                password = 'Elpadrino12$'
                port = 1433
                
                Usa estos parámetros directamente con pymssql.connect().
                
                La estructura de datos es:
                Tabla: Registro_Tiempo
                Columnas:
                - PROYECTO: Nombre del proyecto
                - TAREA: Nombre de la tarea que pertenece al proyecto
                - TIEMPO_INICIAL: Formato "AÑO-MES-DIA HORA"
                - TIEMPO_FINAL: Formato "AÑO-MES-DIA HORA"
                
                El código debe usar get_connection() para obtener la conexión a la base de datos.
                
                Consulta: {user_input}
                
                Responde SOLO con el código Python, sin explicaciones adicionales.

                Todo código debe incluir manejo de excepciones y print statements con los detalles suficientes para depurar tanto la lógica del cálculo de fechas como la consulta SQL generada.
                """
            
            code_response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=[{"role": "system", "content": "Eres un asistente que genera código Python para análisis de datos."},
                        {"role": "user", "content": code_prompt}],
                temperature=0,
            )
            print('Imprimiendo la respuesta del código')
            print("Respuesta de código:", code_response.choices[0].message.content.strip())
            
            generated_code = code_response.choices[0].message.content.strip()
            if generated_code.startswith('```python'):
                generated_code = generated_code[9:]
            if generated_code.endswith('```'):
                generated_code = generated_code[:-3]
            generated_code = generated_code.strip()

            try:
                output = StringIO()
                sys.stdout = output
                exec(generated_code, globals())
                sys.stdout = sys.__stdout__
                code_output = output.getvalue()
                print("Resultado de la ejecución del código:")
                print(code_output)  # Imprime el resultado de la ejecución
            except Exception as e:
                code_output = f"Error en la ejecución del código: {str(e)}"
                print(code_output)  # Imprime el error si ocurre uno
            
            # Interpreta los resultados
            interpretation_prompt = f"""
            Interpreta los siguientes resultados de análisis de datos y proporciona una respuesta clara para el usuario:
            
            Consulta original: {user_input}
            
            Resultados del análisis:
            {code_output}
            
            Proporciona una respuesta clara y concisa basada en estos resultados.
            """
            
            interpretation_response = self.client1.chat.completions.create(
                model=self.MODEL1,
                messages=[{"role": "system", "content": "Eres un asistente que interpreta resultados de análisis de datos."},
                        {"role": "user", "content": interpretation_prompt}],
                temperature=0,
            )
            print(interpretation_response)
            assistant_response = interpretation_response.choices[0].message.content
        else:
            # Si no se necesita análisis, genera una respuesta normal
            self.messages.append({"role": "user", "content": user_input})
            response = self.client.chat.completions.create(
                model=self.MODEL,
                messages=self.messages,
                temperature=0,
            )
            assistant_response = response.choices[0].message.content

        self.messages.append({"role": "assistant", "content": assistant_response})
        return assistant_response