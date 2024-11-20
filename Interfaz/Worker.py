from PyQt6.QtCore import QRunnable, pyqtSignal as Signal, QObject
import time

class WorkerSignals(QObject):
    """
    Define las señales que se emitirán desde el hilo de trabajo hacia la GUI.
    - update_labels: Emite tres cadenas que representan la temperatura, el estado del sensor y el estado del motor.
    """
    update_labels = Signal(str, str, str)

class Worker(QRunnable):
    """
    Worker que se ejecuta en un hilo secundario para leer datos del puerto serie y emitir señales para actualizar la GUI.
    """
    def __init__(self, puerto_serie):
        super().__init__()
        self.signals = WorkerSignals()
        self.puerto_serie = puerto_serie
        self.running = True

    def run(self):
        """
        Método que se ejecuta en bucle mientras `running` sea True. Lee datos del puerto serie y emite señales
        con los datos para la actualización de la interfaz gráfica.
        """
        self.puerto_serie.abrir()
        while self.running:
            datos = self.puerto_serie.leer_mensaje()
            if datos:
                sensor_data = datos.split(',')
                if len(sensor_data) == 3:
                    # Asume que los datos vienen en el formato adecuado y los emite
                    self.signals.update_labels.emit(sensor_data[0], sensor_data[1], sensor_data[2])
            time.sleep(1)  # Reduce la carga de lectura para no saturar el puerto

    def stop(self):
        """
        Detiene el bucle del hilo y cierra el puerto serie.
        """
        self.running = False
        self.puerto_serie.cerrar()
