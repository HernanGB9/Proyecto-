import serial

# Configurar el puerto serial
ser = serial.Serial('/dev/ttyUSB0', 115200, timeout=1)

# Función para medir la distancia usando el ESP32
def medir_distancia():
    ser.write(b'MEDIR_DISTANCIA\n')
    response = ser.readline().decode('utf-8').strip()

    if response:
        try:
            return float(response)
        except ValueError:
            print(f"Error al convertir '{response}' a float")
            return None
    else:
        print("No se recibió una respuesta desde el ESP32")
        return None

# Función para detectar si hay un coco en el sensor E18-D80NK
def detectar_coco():
    ser.write(b'DETECTAR_COCO\n')
    response = ser.readline().decode('utf-8').strip()
    return response == 'COCO_DETECTADO'
