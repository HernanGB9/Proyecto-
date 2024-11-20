from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget, QPushButton
from PyQt6.QtCore import Qt, QThreadPool
import sys
from Worker import Worker  # Asegúrate de que Worker.py está correctamente definido y en el mismo directorio
from PuertoSerie import PuertoSerie  # Asegúrate de que PuertoSerie.py está correctamente definido

class Ventana(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor de Sensores y Motor")
        self.setGeometry(100, 100, 400, 300)  # Tamaño y posición de la ventana principal

        # Configuración de la interfaz de usuario
        self.setup_ui()

        # Inicialización del pool de threads
        self.threadpool = QThreadPool()

        # Creación y configuración del worker
        puerto_serie = PuertoSerie()  # Instancia de PuertoSerie
        self.worker = Worker(puerto_serie)
        self.worker.signals.update_labels.connect(self.update_labels)  # Conexión de la señal del worker a un slot local
        self.threadpool.start(self.worker)  # Inicia el worker en un nuevo thread

    def setup_ui(self):
        layout = QVBoxLayout()

        self.valor_temperatura = QLabel("Temperatura: Esperando datos...")
        self.estado_sensor = QLabel("Estado del sensor: Esperando datos...")
        self.estado_motor = QLabel("Estado del motor: Esperando datos...")
        boton_salir = QPushButton("Salir")
        boton_salir.clicked.connect(self.close)

        layout.addWidget(self.valor_temperatura)
        layout.addWidget(self.estado_sensor)
        layout.addWidget(self.estado_motor)
        layout.addWidget(boton_salir)

        central_widget = QWidget()
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

    def obtener_worker(self):
        return self.worker

    def update_labels(self, temperatura, estado_sensor, estado_motor):
        self.valor_temperatura.setText(f"Temperatura: {temperatura} °C")
        self.estado_sensor.setText(f"Estado del sensor: {'Detectado' if estado_sensor == '1' else 'No detectado'}")
        self.estado_motor.setText(f"Estado del motor: {'Activado' if estado_motor == '1' else 'Apagado'}")

    def closeEvent(self, event):
        self.worker.stop()  # Detiene el worker antes de cerrar la aplicación
        super().closeEvent(event)

def main():
    app = QApplication(sys.argv)
    ventana = Ventana()
    ventana.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
