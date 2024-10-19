import sys
import time
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QVBoxLayout, QProgressBar

# Importar los módulos de sensores y motores
from sensores import medir_distancia, detectar_coco
from motores import activar_motor, detener_motor, activar_piston

# Clase para la interfaz de control
class ControlInterface(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        # Configurar la ventana principal
        self.setWindowTitle("Control de Sistema")
        self.setGeometry(100, 100, 600, 400)

        # Estado del sensor de la tolva
        self.tolva_status_label = QLabel("Estado de la Tolva: Desconocido")
        
        # Estado del sensor del coco
        self.coco_status_label = QLabel("Coco Detectado: No")
        
        # Barra de progreso para el pistón
        self.piston_progress = QProgressBar()
        self.piston_progress.setValue(0)

        # Botón para encender y apagar el motor
        self.motor_on_button = QPushButton("Encender Banda")
        self.motor_on_button.clicked.connect(self.motor_on)

        self.motor_off_button = QPushButton("Apagar Banda")
        self.motor_off_button.clicked.connect(self.motor_off)

        # Botón para activar el pistón
        self.piston_button = QPushButton("Activar Pistón")
        self.piston_button.clicked.connect(self.activar_piston)

        # Layout
        layout = QVBoxLayout()
        layout.addWidget(self.tolva_status_label)
        layout.addWidget(self.coco_status_label)
        layout.addWidget(self.motor_on_button)
        layout.addWidget(self.motor_off_button)
        layout.addWidget(self.piston_button)
        layout.addWidget(self.piston_progress)
        self.setLayout(layout)

        # Actualizar el estado del sistema cada segundo
        self.update_state()

    # Función para encender el motor
    def motor_on(self):
        activar_motor()
        print("Banda activada")

    # Función para apagar el motor
    def motor_off(self):
        detener_motor()
        print("Banda apagada")

    # Función para activar el pistón
    def activar_piston(self):
        activar_piston()
        for i in range(101):
            self.piston_progress.setValue(i)
            QApplication.processEvents()
            time.sleep(0.02)

    # Función para actualizar el estado de los sensores
    def update_state(self):
        distancia_tolva = medir_distancia()

        if distancia_tolva is not None:
            if distancia_tolva < 20:
                self.tolva_status_label.setText("Estado de la Tolva: Llena")
            else:
                self.tolva_status_label.setText("Estado de la Tolva: Vacía")
        else:
            self.tolva_status_label.setText("Error leyendo el sensor de la tolva")
        
        if detectar_coco():
            self.coco_status_label.setText("Coco Detectado: Sí")
        else:
            self.coco_status_label.setText("Coco Detectado: No")

        QTimer.singleShot(1000, self.update_state)

# Ejecutar la aplicación PyQt6
if __name__ == '__main__':
    app = QApplication(sys.argv)
    ventana = ControlInterface()
    ventana.show()
    sys.exit(app.exec())
