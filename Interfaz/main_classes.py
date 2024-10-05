from PyQt6.QtWidgets import QMainWindow, QLabel, QVBoxLayout, QWidget, QProgressBar, QDialog, QPushButton, QTextEdit, QHBoxLayout
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QRect
from PyQt6.QtGui import QFont, QAction
import asyncio
from bleak import BleakScanner
from pywifi import PyWiFi, const
import time

class SplashScreen(QWidget):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calibración de la máquina")
        self.setGeometry(100, 100, 600, 400)
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Calibrando la máquina...", self)
        self.label.setFont(QFont("Arial", 16))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)

        layout.addWidget(self.label)
        layout.addWidget(self.progress_bar)
        self.setLayout(layout)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateProgress)
        self.timer.start(500)

        self.step = 0
        self.steps = [
            "Calibrando la máquina...",
            "Conectando con microprocesadores...",
            "Conectando con microcontroladores...",
            "Activando Bluetooth...",
            "Activando WiFi...",
            "Calibración completada."
        ]

    def updateProgress(self):
        if self.step < len(self.steps):
            self.label.setText(self.steps[self.step])
            self.progress_bar.setValue((self.step + 1) * 20)
            self.step += 1
        else:
            self.timer.stop()
            self.finished.emit()

class ProcessScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Proceso en progreso")
        self.setGeometry(100, 100, 800, 600)
        self.initUI()

    def initUI(self):
        self.layout = QVBoxLayout()

        self.label = QLabel("Tolva vacía", self)
        self.label.setFont(QFont("Arial", 20))
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        # Las animaciones de motor y pistón se crean solo cuando son necesarias
        self.motor_label = None
        self.piston_label = None

    def show_message(self, message):
        self.label.setText(message)

    def animate_motor(self):
        if self.motor_label is None:
            self.motor_label = QLabel("🔄 Motor", self)
            self.motor_label.setFont(QFont("Arial", 24))
            self.layout.addWidget(self.motor_label)

        self.motor_animation = QPropertyAnimation(self.motor_label, b"geometry")
        self.motor_animation.setDuration(3000)
        self.motor_animation.setStartValue(QRect(50, 50, 100, 50))
        self.motor_animation.setEndValue(QRect(650, 50, 100, 50))
        self.motor_animation.start()

    def animate_piston(self):
        if self.piston_label is None:
            self.piston_label = QLabel("🛠️ Pistón", self)
            self.piston_label.setFont(QFont("Arial", 24))
            self.layout.addWidget(self.piston_label)

        self.piston_animation = QPropertyAnimation(self.piston_label, b"geometry")
        self.piston_animation.setDuration(3000)
        self.piston_animation.setStartValue(QRect(50, 150, 100, 50))
        self.piston_animation.setEndValue(QRect(650, 150, 100, 50))
        self.piston_animation.start()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Pantalla Principal")
        self.setGeometry(100, 100, 800, 600)
        self.process_screen = ProcessScreen()
        self.setCentralWidget(self.process_screen)
        self.initUI()

    def initUI(self):
        # Barra de herramientas
        self.menu_bar = self.menuBar()

        inicio_action = QAction("Inicio", self)
        inicio_action.triggered.connect(self.start_process)

        paro_action = QAction("Paro", self)
        paro_action.triggered.connect(self.stop_process)

        reanudar_action = QAction("Reanudar", self)
        reanudar_action.triggered.connect(self.resume_process)

        self.menu_bar.addAction(inicio_action)
        self.menu_bar.addAction(paro_action)
        self.menu_bar.addAction(reanudar_action)

        # Variables de control de proceso
        self.paused = False
        self.process_stopped = False
        self.current_step = None  # Guardar el paso en el que se detuvo

    def start_process(self):
        # Reiniciar el estado de las variables si el proceso está detenido
        self.paused = False
        self.process_stopped = False
        self.current_step = None  # Reinicia el paso actual

        # Mostrar el mensaje "Tolva vacía" durante 5 segundos
        self.process_screen.show_message("Tolva vacía")
        QTimer.singleShot(5000, self.tolva_cargada)

    def tolva_cargada(self):
        if not self.process_stopped:
            # Mostrar el mensaje "Tolva cargada" y esperar para el siguiente paso
            self.process_screen.show_message("Tolva cargada")
            self.current_step = self.activate_motor
            QTimer.singleShot(5000, self.activate_motor)

    def activate_motor(self):
        if not self.process_stopped:
            # Mostrar el mensaje "Activando motores" y empezar animación del motor
            self.process_screen.show_message("Activando motores")
            self.current_step = self.activate_piston
            self.process_screen.animate_motor()

            QTimer.singleShot(5000, self.activate_piston)

    def activate_piston(self):
        if not self.process_stopped:
            # Mostrar el mensaje "Activando pistón" y empezar animación del pistón
            self.process_screen.show_message("Activando pistón")
            self.current_step = None  # El proceso termina aquí
            self.process_screen.animate_piston()

    def stop_process(self):
        self.process_stopped = True
        self.paused = True
        self.process_screen.show_message("Paro activado")

    def resume_process(self):
        if self.paused and self.process_stopped:
            self.paused = False
            self.process_stopped = False
            self.process_screen.show_message("Reanudando proceso")
            if self.current_step:
                QTimer.singleShot(2000, self.current_step)  # Reanuda en el paso que quedó
