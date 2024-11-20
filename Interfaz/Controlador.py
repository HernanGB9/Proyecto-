import threading
import time

from PuertoSerie import PuertoSerie
from Convertidor import Convertidor
from Worker import WorkerSignals  # Si necesitas señales de otro módulo

ADMINISTRACION = '0'
CONTROL = 49
MOD_BANDERA = 52

class Controlador:
    def __init__(self, nombre: str = ""):
        print('Dentro del constructor de Controlador')
        self.nombre = nombre
        self.led_real = False
        self.led = False
        self.funcionando = True
        self.convertidor = Convertidor()
        self.puerto_serie = PuertoSerie()
        self.worker = None
        self.tarea = threading.Thread(target=self.run_controladora)
        self.tarea.start()

    def prender_led(self, estado):
        if estado:
            mensaje = self.convertidor.generar_mensaje(CONTROL, MOD_BANDERA, [0, 1])
        else:
            mensaje = self.convertidor.generar_mensaje(CONTROL, MOD_BANDERA, [1, 1])
        print(f"El mensaje a enviar es: {mensaje} ", ' '.join('{0:02X}'.format(e) for e in mensaje))
        self.puerto_serie.enviar_mensaje(mensaje)

    def run_controladora(self):
        self.puerto_serie.abrir()
        while self.funcionando:
            if self.worker:
                self.worker.senal_parpadeo(self.led)
                time.sleep(1)
                self.led = not self.led
                self.worker.senal_parpadeo(self.led)
        self.puerto_serie.cerrar()

    def establecer_worker(self, worker):
        self.worker = worker

    def detener(self):
        self.funcionando = False
        if self.tarea:
            self.tarea.join()
        print("Se ha detenido")

if __name__ == "__main__":
    # Esto permite probar el controlador de forma independiente si es necesario.
    controlador = Controlador("1")
