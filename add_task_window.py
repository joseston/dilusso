from PyQt5.QtWidgets import QDialog, QLabel, QPushButton, QHBoxLayout, QCalendarWidget, QLineEdit, QVBoxLayout, QWidget, QTableWidget, QComboBox, QTableWidgetItem, QSizePolicy, QTimeEdit
from PyQt5.QtCore import QDate, Qt, QTime
from PyQt5.QtGui import QIcon
from database_operations import load_projects
from utils import resource_path
from add_task.database_tasks import add_daily_task, get_daily_tasks, update_task_priority, get_tiempo_hecho_por_fecha

class AddTaskWindow(QDialog):
    def __init__(self, parent=None, time_tracker_instance=None):
        super().__init__(parent)
        self.setWindowTitle("Añadir Tarea")
        self.time_tracker_instance = time_tracker_instance
        # Establecer un tamaño mínimo para la ventana
        self.setMinimumSize(1500, 600)

        # Layout principal horizontal
        main_layout = QHBoxLayout()
        
        # Calendario (ocupará 1/5 del espacio)
        self.calendar = QCalendarWidget()
        self.calendar.selectionChanged.connect(self.date_selected)
        main_layout.addWidget(self.calendar, 1)  # stretch factor 1
        
        # Contenedor derecho (ocupará 4/5 del espacio)
        right_container = QWidget()
        self.right_layout = QVBoxLayout(right_container)
        
        # Permitir que el contenedor derecho se expanda
        right_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Contenedor superior para la entrada de la tarea
        self.top_right_container = QWidget()
        self.top_right_layout = QVBoxLayout(self.top_right_container)
        
        # Cargar proyectos antes de añadir la primera fila
        self.load_projects()
        
        # Añadir la primera fila de tarea y proyecto
        self.add_task_row()
        
        # Contenedor inferior para la información de la tarea
        bottom_right_container = QWidget()
        bottom_right_layout = QVBoxLayout(bottom_right_container)
        
        self.task_info_label = QLabel("Información de tareas para este día:")
        self.task_info_label.setEnabled(False)
        
        # Tabla para mostrar las tareas
        self.table_widget = QTableWidget()
        self.table_widget.setColumnCount(7)
        self.table_widget.setHorizontalHeaderLabels(["Tarea", "Proyecto", "Prioridad", "Terminado", "Fecha", "Tiempo Máximo", ""])
        self.table_widget.setEditTriggers(QTableWidget.NoEditTriggers)  # Hacer la tabla no editable

        bottom_right_layout.addWidget(self.task_info_label)
        bottom_right_layout.addWidget(self.table_widget)  # Añadir la tabla al layout
        
        # Botón Guardar para la información de la tarea
        self.save_info_button = QPushButton("Guardar Info")
        self.save_info_button.clicked.connect(self.save_info)
        self.save_info_button.setEnabled(False)
        bottom_right_layout.addWidget(self.save_info_button)
        
        # Añadir contenedores superior e inferior al contenedor derecho
        self.right_layout.addWidget(self.top_right_container, 1)  # stretch factor 1
        self.right_layout.addWidget(bottom_right_container, 1)  # stretch factor 1
        
        main_layout.addWidget(right_container, 4)  # stretch factor 4
        
        # Layout final
        final_layout = QVBoxLayout()
        final_layout.addLayout(main_layout)
        self.setLayout(final_layout)

    def add_task_row(self):
        # Contenedor para la fila de tarea y proyecto
        task_row_container = QWidget()
        task_row_layout = QHBoxLayout(task_row_container)

        # Widgets para la tarea
        task_label = QLabel("Tarea:")
        task_entry = QLineEdit()
        task_entry.setEnabled(False)

        project_label = QLabel("Proyecto:")
        project_combo = QComboBox()
        project_combo.setEnabled(False)
        project_combo.addItems(sorted(self.projects.keys()))

        # Botón para añadir nueva fila
        add_button = QPushButton()
        add_button.setIcon(QIcon(resource_path("add_icon.png")))
        add_button.clicked.connect(self.add_task_row)
        add_button.setEnabled(False)

        # Botón para guardar la tarea de la fila
        save_button = QPushButton("Guardar Tarea")
        save_button.clicked.connect(lambda _, te=task_entry, pc=project_combo: self.save_task(te, pc))
        save_button.setEnabled(False)

        # Añadir widgets al layout de la fila
        task_row_layout.addWidget(task_label)
        task_row_layout.addWidget(task_entry)
        task_row_layout.addWidget(project_label)
        task_row_layout.addWidget(project_combo)
        task_row_layout.addWidget(add_button)
        task_row_layout.addWidget(save_button)  # Añadir el botón de guardar

        # Añadir la fila al layout superior
        self.top_right_layout.addWidget(task_row_container)

        # Guardar referencias a los widgets para su posterior uso
        self.task_entries.append(task_entry)
        self.project_combos.append(project_combo)
        self.add_buttons.append(add_button)
        self.save_buttons.append(save_button)

        # Permitir que los widgets se expandan
        task_entry.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        project_combo.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def date_selected(self):
        selected_date = self.calendar.selectedDate()
        for task_entry in self.task_entries:
            task_entry.setEnabled(True)
        for project_combo in self.project_combos:
            project_combo.setEnabled(True)
        for add_button in self.add_buttons:
            add_button.setEnabled(True)
        for save_button in self.save_buttons:
            save_button.setEnabled(True)
        self.task_info_label.setEnabled(True)
        self.save_info_button.setEnabled(True)
        # Cargar las tareas del día seleccionado en la tabla
        self.load_tasks_to_table(selected_date)
        print(f"Fecha seleccionada: {selected_date.toString('yyyy-MM-dd')}")

    def save_task(self, task_entry, project_combo):
        selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        task_text = task_entry.text()
        project_text = project_combo.currentText()
        if task_text and project_text:
            add_daily_task(task_text, project_text, selected_date)
            task_entry.clear()  # Limpiar el campo de tarea después de guardar
        else:
            print("Por favor, ingrese una tarea y seleccione un proyecto.")

    def save_info(self):
        for row_index in range(self.table_widget.rowCount()):
            task_item = self.table_widget.item(row_index, 0)
            project_item = self.table_widget.item(row_index, 1)
            priority_widget = self.table_widget.cellWidget(row_index, 2)
            terminado_item = self.table_widget.item(row_index, 3)  # Obtener el valor de "Terminado"
            time_widget = self.table_widget.cellWidget(row_index, 6)  # Obtener el QTimeEdit de la columna 6

            if task_item and project_item and priority_widget and time_widget and terminado_item:
                task_name = task_item.text()
                project_name = project_item.text()
                priority = priority_widget.currentText()
                terminado = 1 if terminado_item.text().lower() == "sí" else 0  # Convertir "Sí" a 1 y "No" a 0
                time = time_widget.time()
                time_in_seconds = time.hour() * 3600 + time.minute() * 60 + time.second()
                selected_date = self.calendar.selectedDate().toString("yyyy-MM-dd")

                # Actualizar la prioridad, el tiempo máximo y el estado de terminado
                update_task_priority(task_name, project_name, selected_date, priority, time_in_seconds, terminado)

        print("Información de la tabla guardada")

    def load_projects(self):
        self.projects = load_projects()
        self.task_entries = []
        self.project_combos = []
        self.add_buttons = []
        self.save_buttons = []  # Lista para almacenar los botones de guardar

    def load_tasks_to_table(self, date):
        tasks = get_daily_tasks(date.toString("yyyy-MM-dd"))
        tiempos_hechos = get_tiempo_hecho_por_fecha(date.toString("yyyy-MM-dd"))
        self.table_widget.setRowCount(len(tasks))
        self.table_widget.setColumnCount(9)  # Aumentar el número de columnas a 9
        self.table_widget.setHorizontalHeaderLabels(["Tarea", "Proyecto", "Prioridad", "Terminado", "Fecha", "Tiempo Real", "Tiempo Máximo", "","Seleccionar"]) # Añadir encabezados
        for row_index, task in enumerate(tasks):
            self.table_widget.setItem(row_index, 0, QTableWidgetItem(task["Tarea"]))
            self.table_widget.setItem(row_index, 1, QTableWidgetItem(task["Proyecto"]))

            # Crear un QComboBox para la prioridad
            priority_combo = QComboBox()
            priority_combo.addItems(["", "ALTA", "MEDIA", "BAJA"])
            priority_combo.setCurrentText(task["Prioridad"])
            self.table_widget.setCellWidget(row_index, 2, priority_combo)

            self.table_widget.setItem(row_index, 3, QTableWidgetItem("Sí" if task["Terminado"] else "No"))
            self.table_widget.setItem(row_index, 4, QTableWidgetItem(str(task["Fecha"])))

            # Obtener el tiempo hecho del diccionario
            tiempo_hecho = self.get_tiempo_hecho_formateado(tiempos_hechos, task["Proyecto"], task["Tarea"])
            self.table_widget.setItem(row_index, 5, QTableWidgetItem(tiempo_hecho))  # Columna 5: Tiempo Real

            # Usar QTimeEdit para el tiempo máximo
            time_edit = QTimeEdit()
            time_edit.setDisplayFormat("HH:mm:ss")
            if task["Tiempo_Maximo"]:
                # Convertir segundos a QTime
                hours = task["Tiempo_Maximo"] // 3600
                minutes = (task["Tiempo_Maximo"] % 3600) // 60
                seconds = task["Tiempo_Maximo"] % 60
                time_edit.setTime(QTime(hours, minutes, seconds))
            else:
                time_edit.setTime(QTime(0, 0, 0))  # Valor predeterminado
            self.table_widget.setCellWidget(row_index, 6, time_edit)  # Columna 6: Tiempo Máximo

            # Crear un botón para seleccionar la tarea
            select_button = QPushButton("Seleccionar")
            select_button.clicked.connect(lambda _, task=task: self.select_task(task))
            self.table_widget.setCellWidget(row_index, 8, select_button)  # Columna 8: Seleccionar

    def get_tiempo_hecho_formateado(self, tiempos_hechos, proyecto, tarea):
        if proyecto in tiempos_hechos and tarea in tiempos_hechos[proyecto]:
            tiempo = tiempos_hechos[proyecto][tarea]
            hours = tiempo // 3600
            minutes = (tiempo % 3600) // 60
            seconds = tiempo % 60
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return "00:00:00"

    def select_task(self, task):
        if self.time_tracker_instance:
            self.time_tracker_instance.project_combo.setCurrentText(task["Proyecto"])
            self.time_tracker_instance.update_tasks()
            self.time_tracker_instance.task_combo.setCurrentText(task["Tarea"])
            self.close()