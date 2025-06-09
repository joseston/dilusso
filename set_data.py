# app/set_data.py
from PyQt5.QtWidgets import (QDialog, QLabel, QPushButton, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QLineEdit, QMessageBox, QComboBox)
from database_operations import add_project_task, load_projects

class SetData(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Setear Datos")

        self.projects = set()
        self.current_tasks = set()

        self.init_ui()
        self.load_projects()

    def init_ui(self):
        self.project_combo = QComboBox()
        self.project_combo.setEditable(True)
        self.project_combo.currentTextChanged.connect(self.update_tasks)
        self.task_list = QListWidget()
        self.new_task_input = QLineEdit()
        self.add_task_button = QPushButton("Agregar Tarea")
        self.add_task_button.clicked.connect(self.add_task)
        self.remove_task_button = QPushButton("Quitar Tarea")
        self.remove_task_button.clicked.connect(self.remove_task)

        self.save_button = QPushButton("Guardar")
        self.save_button.clicked.connect(self.save_data)

        layout = QVBoxLayout()

        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel("Proyecto:"))
        project_layout.addWidget(self.project_combo)
        layout.addLayout(project_layout)

        layout.addWidget(QLabel("Tareas:"))
        layout.addWidget(self.task_list)

        task_input_layout = QHBoxLayout()
        task_input_layout.addWidget(self.new_task_input)
        task_input_layout.addWidget(self.add_task_button)
        task_input_layout.addWidget(self.remove_task_button)
        layout.addLayout(task_input_layout)

        layout.addWidget(self.save_button)

        self.setLayout(layout)

    def load_projects(self):
        self.projects = load_projects()
        self.project_combo.clear()
        self.project_combo.addItems(sorted(self.projects))

    def update_tasks(self):
        self.task_list.clear()
        self.current_tasks.clear()

    def add_task(self):
        current_project = self.project_combo.currentText()
        new_task = self.new_task_input.text().strip()

        if not new_task:
            QMessageBox.warning(self, "Error", "Por favor, ingrese una tarea.")
            return

        if new_task not in self.current_tasks:
            self.current_tasks.add(new_task)
            self.task_list.addItem(new_task)
            self.new_task_input.clear()
        else:
            QMessageBox.warning(self, "Error", "Esta tarea ya existe para este proyecto.")

    def remove_task(self):
        current_item = self.task_list.currentItem()
        if current_item is None:
            QMessageBox.warning(self, "Error", "Por favor, seleccione una tarea para quitar.")
            return

        task_to_remove = current_item.text()
        self.current_tasks.remove(task_to_remove)
        self.task_list.takeItem(self.task_list.row(current_item))

    def save_data(self):
        current_project = self.project_combo.currentText()
        for task in self.current_tasks:
            add_project_task(current_project, task, 1)
        
        if current_project not in self.projects:
            self.projects.add(current_project)
            self.project_combo.addItem(current_project)

        QMessageBox.information(self, "Guardado", "Los cambios han sido guardados en la base de datos.")
        self.current_tasks.clear()
        self.task_list.clear()