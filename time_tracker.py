# app/time_tracker.py
from PyQt5.QtWidgets import QWidget, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QComboBox, QFormLayout, QSystemTrayIcon
from PyQt5.QtCore import QTimer, QDateTime, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtMultimedia import QSound
from set_data import SetData
from datetime import datetime
from dilusso_chat import DilussoChat
from utils import resource_path
from database_operations import add_time_record, load_projects
from add_task_window import AddTaskWindow

class TimeTracker(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Time Tracker")
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        
        # Remove this early call to set_inactive_style()
        # self.set_inactive_style()

        self.projects_and_tasks = {}

        self.project_label = QLabel("Proyecto:")
        self.project_combo = QComboBox()
        self.project_combo.currentIndexChanged.connect(self.update_tasks)
        self.task_label = QLabel("Tarea:")
        self.task_combo = QComboBox()
        self.duration_label = QLabel("Duración (minutos):")
        self.duration_entry = QLineEdit()
        self.timer_label = QLabel("00:00:00")
        self.timer_label.setStyleSheet("font-size: 36px; font-family: Helvetica;")
        self.start_button = QPushButton("Iniciar")
        self.start_button.clicked.connect(self.start_timer)
        self.stop_button = QPushButton("Detener")
        self.stop_button.clicked.connect(self.stop_timer)
        self.stop_button.setEnabled(False)
        self.set_data_button = QPushButton("Setear Datos")
        self.set_data_button.clicked.connect(self.open_set_data_window)
        self.done_button = QPushButton("LISTO")
        self.done_button.clicked.connect(self.stop_alarm)
        self.done_button.hide()
        self.dilusso_button = QPushButton("Dilusso")
        self.dilusso_button.clicked.connect(self.open_dilusso_chat)
        self.view_data_button = QPushButton("Ver Datos")
        self.view_data_button.clicked.connect(self.open_data_window)
        self.add_task_button = QPushButton("Añadir Tarea")
        self.add_task_button.clicked.connect(self.open_add_task_window)

        self.reduced_layout = QVBoxLayout()
        self.reduced_layout.addWidget(self.timer_label)
        self.reduced_layout.addWidget(self.stop_button)

        self.full_layout = QVBoxLayout()
        
        form_layout = QFormLayout()
        form_layout.addRow("Proyecto:", self.project_combo)
        form_layout.addRow("Tarea:", self.task_combo)
        form_layout.addRow("Duración (minutos):", self.duration_entry)
        self.full_layout.addLayout(form_layout)
        self.full_layout.addWidget(self.timer_label)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.set_data_button)
        button_layout.addWidget(self.view_data_button)
        button_layout.addWidget(self.done_button)
        button_layout.addWidget(self.dilusso_button)
        button_layout.addWidget(self.add_task_button)
        self.full_layout.addLayout(button_layout)

        self.setLayout(self.full_layout)

        self.alarm_sound = QSound(resource_path("sound.wav"))
        self.start_time = 0
        self.remaining_time = 0
        self.timer_running = False
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)

        self.load_projects()

        self.reminder_timer = QTimer(self)
        self.reminder_timer.timeout.connect(self.blink_icon)
        self.reminder_interval = 1000
        self.blink_state = False

        self.tray_icon = QSystemTrayIcon(self)
        self.tray_icon.setIcon(QIcon(resource_path("icon.png")))
        self.tray_icon.setVisible(True)

        # Add this line at the end of __init__
        self.set_inactive_style()
        self.start_soft_reminder()

    def load_projects(self):
        self.projects_and_tasks = load_projects()
        self.project_combo.clear()
        self.project_combo.addItems(sorted(self.projects_and_tasks.keys()))
        self.update_tasks()

    def update_tasks(self):
        self.task_combo.clear()
        current_project = self.project_combo.currentText()
        if current_project in self.projects_and_tasks:
            self.task_combo.addItems(sorted(self.projects_and_tasks[current_project]))


    def open_set_data_window(self):
        set_data_window = SetData(self)
        set_data_window.exec_()
        self.load_projects()

    def start_timer(self):
        if not self.timer_running:
            duration = self.duration_entry.text()
            if duration.isdigit():
                self.remaining_time = int(duration) * 60
                self.start_time = QDateTime.currentDateTime() 
                self.timer_running = True
                self.start_button.setEnabled(False)
                self.stop_button.setEnabled(True)
                self.timer.start(1000)
                self.stop_soft_reminder()
                self.current_project = self.project_combo.currentText()
                self.current_task = self.task_combo.currentText()
                self.switch_to_reduced_layout()
                self.set_active_style()  # Apply active style
            else:
                print("Ingrese una duración válida en minutos.")

    def stop_timer(self):
        if self.timer_running:
            self.timer_running = False
            self.start_button.setEnabled(True)
            self.stop_button.setEnabled(False)
            self.timer.stop()
            self.save_data()
            self.start_soft_reminder()  
            self.switch_to_full_layout()
            self.project_combo.setCurrentText(self.current_project)
            self.task_combo.setCurrentText(self.current_task)
            self.set_inactive_style()  # Apply inactive style

    def switch_to_reduced_layout(self):
        for widget in [self.project_combo, self.task_combo, 
                       self.duration_entry, self.start_button, 
                       self.set_data_button, self.view_data_button, self.dilusso_button,
                       self.add_task_button]:
            widget.hide()
        
        self.timer_label.show()
        self.stop_button.show()
        
        self.adjustSize()

    def switch_to_full_layout(self):
        for widget in [self.project_combo, self.task_combo, 
                       self.duration_entry, self.start_button, 
                       self.set_data_button, self.view_data_button, self.dilusso_button,
                       self.timer_label, self.stop_button, self.add_task_button]:
            widget.show()
        
        self.adjustSize()

    def save_data(self):
        project = self.project_combo.currentText()
        task = self.task_combo.currentText()
        start_time = self.start_time.toString("yyyy-MM-dd HH:mm:ss")
        end_time = QDateTime.currentDateTime().toString("yyyy-MM-dd HH:mm:ss")

        add_time_record(project, task, start_time, end_time)
        print("Data saved successfully.")

    def open_data_window(self):
        from data_window import DataWindow
        data_window = DataWindow(self)
        data_window.exec_()

    def update_timer(self):
        if self.timer_running:
            elapsed_time = self.start_time.secsTo(QDateTime.currentDateTime())
            remaining_time = self.remaining_time - elapsed_time
            if remaining_time <= 0:
                self.timer_running = False
                self.timer_label.setText("00:00:00")
                self.start_button.setEnabled(True)
                self.stop_button.setEnabled(False)
                self.timer.stop()
                self.save_data()
                self.start_alarm()
            elif remaining_time == 10:
                self.speak_warning()
            hours = remaining_time // 3600
            minutes = (remaining_time % 3600) // 60
            seconds = remaining_time % 60
            self.timer_label.setText(f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
    def speak_warning(self):
        self.speaker.Speak("Te quedan 10 segundos de esta actividad")
        
    def start_alarm(self):
        self.alarm_sound.setLoops(QSound.Infinite)
        self.alarm_sound.play()
        self.done_button.show()
        self.set_alarm_style()  # Apply alarm style

    def stop_alarm(self):
        self.alarm_sound.stop()
        self.done_button.hide()
        
        self.timer_running = False
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)
        self.timer.stop()
        self.start_soft_reminder()  
        self.switch_to_full_layout()
        self.project_combo.setCurrentText(self.current_project)
        self.task_combo.setCurrentText(self.current_task)
        self.timer_label.setText("00:00:00")
        self.set_inactive_style()  # Apply inactive style

    def open_dilusso_chat(self):
        chat_window = DilussoChat(self)
        chat_window.exec_()

    def start_soft_reminder(self):
        self.reminder_timer.start(self.reminder_interval)

    def stop_soft_reminder(self):
        self.reminder_timer.stop()
        self.tray_icon.setIcon(QIcon(resource_path("icon.png")))

    def blink_icon(self):
        if not self.timer_running:
            self.blink_state = not self.blink_state
            if self.blink_state:
                self.tray_icon.setIcon(QIcon(resource_path("icon_blink.png")))
            else:
                self.tray_icon.setIcon(QIcon(resource_path("icon.png")))

    def open_add_task_window(self):
        add_task_window = AddTaskWindow(self, time_tracker_instance=self)
        add_task_window.exec_()

    def set_active_style(self):
        """Apply styling when timer is running"""
        self.setStyleSheet("""
            QWidget {
                background-color: #e6ffe6; /* Light green background */
            }
            QLabel#timer_label {
                font-size: 36px;
                font-family: Helvetica;
                font-weight: bold;
                color: #006400; /* Dark green text */
            }
        """)
        self.timer_label.setObjectName("timer_label")

    def set_inactive_style(self):
        """Apply styling when timer is not running"""
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f0f0; /* Light gray background */
            }
            QLabel#timer_label {
                font-size: 36px;
                font-family: Helvetica;
                font-weight: bold;
                color: #444444;
            }
        """)
        self.timer_label.setObjectName("timer_label")

    def set_alarm_style(self):
        """Apply styling when alarm is active"""
        self.setStyleSheet("""
            QWidget {
                background-color: #ffe6e6; /* Light red background */
            }
            QLabel#timer_label {
                font-size: 36px;
                font-family: Helvetica;
                font-weight: bold;
                color: #8b0000; /* Dark red text */
            }
            QPushButton#done_button {
                background-color: #ff6666;
                color: white;
                font-weight: bold;
                padding: 8px;
                border-radius: 4px;
            }
        """)
        self.timer_label.setObjectName("timer_label")
        self.done_button.setObjectName("done_button")