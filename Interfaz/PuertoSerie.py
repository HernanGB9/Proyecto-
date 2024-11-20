import serial
import time

class PuertoSerie:
    def __init__(self):
        self.puerto = serial.Serial()
        self.puerto.port = "/dev/ttyUSB0"  # Ajusta esto a tu puerto serial correcto
        self.puerto.baudrate = 115200
        self.puerto.parity = serial.PARITY_NONE
        self.puerto.timeout = 1
        self.puerto.stopbits = serial.STOPBITS_ONE
        self.puerto.bytesize = serial.EIGHTBITS

    def abrir(self):
        if not self.puerto.is_open:
            self.puerto.open()

    def leer_mensaje(self):
        if self.puerto.is_open:
            datos = self.puerto.readline().decode('utf-8').strip()
            return datos

    def enviar_mensaje(self, mensaje):
        if self.puerto.is_open:
            self.puerto.write(mensaje)
            time.sleep(0.01)  # Da tiempo para que el mensaje sea procesado
            respuesta = self.puerto.read(25)
            return respuesta

    def cerrar(self):
        if self.puerto.is_open:
            self.puerto.close()
 