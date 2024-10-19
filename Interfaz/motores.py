import serial

# Configurar el puerto serial
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

# Función para activar el motor
def activar_motor():
    ser.write(b'ACTIVAR_MOTOR\n')

# Función para detener el motor
def detener_motor():
    ser.write(b'DETENER_MOTOR\n')

# Función para activar el pistón
def activar_piston():
    ser.write(b'ACTIVAR_PISTON\n')
