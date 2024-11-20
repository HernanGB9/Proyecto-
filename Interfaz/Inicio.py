import sys
import serial
import socket
from serial.tools import list_ports
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QLabel, QWidget,
    QPushButton, QMenu, QDialog, QLineEdit, QFormLayout, QMessageBox, QComboBox
)
from PyQt6.QtCore import QThread, pyqtSignal, pyqtSlot, QTimer


# Hilo de comunicación
class CommunicationThread(QThread):
    data_received = pyqtSignal(str)  # Señal para pasar datos recibidos a la interfaz

    def __init__(self, connection_method, client_socket=None, serial_connection=None):
        super().__init__()
        self.connection_method = connection_method
        self.client_socket = client_socket
        self.serial_connection = serial_connection
        self.running = True

    def run(self):
        while self.running:
            try:
                if self.connection_method == "WiFi" and self.client_socket:
                    self.client_socket.sendall(b'\x05')  # Solicitar estados
                    data = self.client_socket.recv(1024).decode()
                    self.data_received.emit(data)
                elif self.connection_method == "Serial" and self.serial_connection:
                    self.serial_connection.write(b'\x05')  # Solicitar estados
                    data = self.serial_connection.readline().decode()
                    self.data_received.emit(data)
            except Exception as e:
                print(f"Error en la comunicación: {e}")
                self.running = False

    def stop(self):
        self.running = False
        self.quit()
        self.wait()


# Cuadro de diálogo para seleccionar WiFi o Serial
class ConnectionModeDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Seleccionar Modo de Conexión")
        self.setGeometry(100, 100, 300, 200)
        self.mode = None
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.wifi_button = QPushButton("WiFi")
        self.serial_button = QPushButton("Serial")
        self.wifi_button.clicked.connect(self.select_wifi)
        self.serial_button.clicked.connect(self.select_serial)

        layout.addWidget(self.wifi_button)
        layout.addWidget(self.serial_button)
        self.setLayout(layout)

    def select_wifi(self):
        self.mode = "WiFi"
        self.accept()

    def select_serial(self):
        self.mode = "Serial"
        self.accept()

    def get_mode(self):
        return self.mode


# Cuadro de diálogo para configuración WiFi o Serial
class ConnectionDialog(QDialog):
    def __init__(self, method):
        super().__init__()
        self.method = method
        self.setWindowTitle("Configuración de Conexión")
        self.setGeometry(100, 100, 300, 200)
        self.init_ui()

    def init_ui(self):
        layout = QFormLayout()

        if self.method == "WiFi":
            self.ip_input = QLineEdit(self)
            self.port_input = QLineEdit(self)
            layout.addRow("IP del Servidor:", self.ip_input)
            layout.addRow("Puerto:", self.port_input)
        elif self.method == "Serial":
            self.port_combobox = QComboBox(self)
            self.baud_rate_input = QLineEdit(self)

            # Detectar puertos disponibles
            ports = list_ports.comports()
            for port in ports:
                self.port_combobox.addItem(port.device)

            layout.addRow("Puerto Serial:", self.port_combobox)
            layout.addRow("Baud Rate:", self.baud_rate_input)

        self.ok_button = QPushButton("Conectar")
        self.cancel_button = QPushButton("Cancelar")
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)

        button_layout = QHBoxLayout()
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addRow(button_layout)
        self.setLayout(layout)

    def get_data(self):
        if self.method == "WiFi":
            return self.ip_input.text(), self.port_input.text()
        elif self.method == "Serial":
            return self.port_combobox.currentText(), self.baud_rate_input.text()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Control ESP32")
        self.setGeometry(100, 100, 800, 600)

        # Conexión
        self.connection_method = None
        self.client_socket = None
        self.serial_connection = None
        self.communication_thread = None

        # Estados
        self.motor_state = "Apagado"
        self.piston_state = "Desactivado"
        self.sensor_barrier_state = "No activado"

        self.init_ui()

    def init_ui(self):
        # Layout principal
        central_widget = QWidget()
        main_layout = QVBoxLayout()

        # Lecturas
        self.motor_state_label = QLabel(f"Estado del Motor: {self.motor_state}")
        self.piston_state_label = QLabel(f"Estado del Pistón: {self.piston_state}")
        self.sensor_barrier_label = QLabel(f"Sensor de Barrera: {self.sensor_barrier_state}")

        main_layout.addWidget(self.motor_state_label)
        main_layout.addWidget(self.piston_state_label)
        main_layout.addWidget(self.sensor_barrier_label)

        # Botones de control
        button_layout = QHBoxLayout()
        self.start_button = QPushButton("Encender Motor")
        self.stop_button = QPushButton("Apagar Motor")
        self.piston_button = QPushButton("Activar Pistón")
        self.stop_system_button = QPushButton("Paro")
        self.start_system_button = QPushButton("Arranque")

        self.start_button.clicked.connect(lambda: self.send_command(0x01))
        self.stop_button.clicked.connect(lambda: self.send_command(0x02))
        self.piston_button.clicked.connect(lambda: self.send_command(0x03))
        self.stop_system_button.clicked.connect(lambda: self.send_command(0x06))  # Paro
        self.start_system_button.clicked.connect(lambda: self.send_command(0x07))  # Arranque

        button_layout.addWidget(self.start_button)
        button_layout.addWidget(self.stop_button)
        button_layout.addWidget(self.piston_button)
        button_layout.addWidget(self.stop_system_button)
        button_layout.addWidget(self.start_system_button)

        main_layout.addLayout(button_layout)

        # Configurar el widget principal
        central_widget.setLayout(main_layout)
        self.setCentralWidget(central_widget)

        # Selección del modo de conexión
        self.select_connection_mode()

    def select_connection_mode(self):
        mode_dialog = ConnectionModeDialog()
        if mode_dialog.exec():
            self.connection_method = mode_dialog.get_mode()
            self.configure_connection()

    def configure_connection(self):
        if self.connection_method:
            config_dialog = ConnectionDialog(self.connection_method)
            if config_dialog.exec():
                if self.connection_method == "WiFi":
                    ip, port = config_dialog.get_data()
                    if not ip or not port.isdigit():  # Validar entrada
                        QMessageBox.critical(self, "Error", "IP o puerto no válidos.")
                        self.configure_connection()  # Reintentar
                    else:
                        self.connect_wifi(ip, int(port))
                elif self.connection_method == "Serial":
                    port, baud_rate = config_dialog.get_data()
                    if not port or not baud_rate.isdigit():  # Validar entrada
                        QMessageBox.critical(self, "Error", "Puerto o baud rate no válidos.")
                        self.configure_connection()  # Reintentar
                    else:
                        self.connect_serial(port, int(baud_rate))

    def connect_wifi(self, ip, port):
        try:
            self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.client_socket.connect((ip, port))
            QMessageBox.information(self, "Conexión", "Conexión WiFi exitosa")
            self.start_communication()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar por WiFi: {e}")

    def connect_serial(self, port, baud_rate):
        try:
            self.serial_connection = serial.Serial(port, baud_rate, timeout=1)
            QMessageBox.information(self, "Conexión", "Conexión Serial exitosa")
            self.start_communication()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo conectar por Serial: {e}")

    def start_communication(self):
        self.communication_thread = CommunicationThread(
            self.connection_method, self.client_socket, self.serial_connection
        )
        self.communication_thread.data_received.connect(self.process_data)
        self.communication_thread.start()

    def send_command(self, command):
        if self.connection_method == "WiFi" and self.client_socket:
            try:
                self.client_socket.sendall(bytes([command]))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo enviar el comando: {e}")
        elif self.connection_method == "Serial" and self.serial_connection:
            try:
                self.serial_connection.write(bytes([command]))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"No se pudo enviar el comando: {e}")

    @pyqtSlot(str)
    def process_data(self, data):
        try:
            parts = data.strip().split(", ")
            for part in parts:
                if "Motor" in part:
                    self.motor_state = "Encendido" if "Encendido" in part else "Apagado"
                elif "Pistón" in part:
                    self.piston_state = "Activado" if "Activado" in part else "Desactivado"
                elif "Barrera" in part:
                    self.sensor_barrier_state = "Activado" if "Activado" in part else "No activado"

            self.motor_state_label.setText(f"Estado del Motor: {self.motor_state}")
            self.piston_state_label.setText(f"Estado del Pistón: {self.piston_state}")
            self.sensor_barrier_label.setText(f"Sensor de Barrera: {self.sensor_barrier_state}")
        except Exception as e:
            print(f"Error al procesar datos: {e}")

    def closeEvent(self, event):
        if self.communication_thread:
            self.communication_thread.stop()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
