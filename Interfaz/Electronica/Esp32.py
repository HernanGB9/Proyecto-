import machine
import time
from machine import Pin

# Pines del HC-SR04
trigger = Pin(15, Pin.OUT)
echo = Pin(2, Pin.IN)

uart = machine.UART(1, baudrate=115200, tx=17, rx=16)

# Función para medir la distancia usando HC-SR04
def medir_distancia():
    trigger.off()
    time.sleep_us(2)
    trigger.on()
    time.sleep_us(10)
    trigger.off()

    while echo.value() == 0:
        pulso_inicio = time.ticks_us()
    while echo.value() == 1:
        pulso_fin = time.ticks_us()

    duracion_pulso = time.ticks_diff(pulso_fin, pulso_inicio)
    distancia = (duracion_pulso * 0.0343) / 2
    return distancia

while True:
    if uart.any():
        command = uart.readline().decode('utf-8').strip()
        
        if command == 'MEDIR_DISTANCIA':
            distancia = medir_distancia()
            uart.write(str(distancia) + '\n')
