#define TRIGGER_PIN 15  // Trigger del HC-SR04
#define ECHO_PIN 2      // Echo del HC-SR04
#define MOTOR_PIN 16    // Pin para el motor DC
#define PISTON_PIN 4    // Pin para el pistón

void setup() {
  // Iniciar el puerto serial
  Serial.begin(115200);
  
  // Configurar pines del sensor HC-SR04
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Configurar pines para el motor y el pistón
  pinMode(MOTOR_PIN, OUTPUT);
  pinMode(PISTON_PIN, OUTPUT);
}

void loop() {
  if (Serial.available()) {
    String command = Serial.readStringUntil('\n');
    command.trim();  // Eliminar espacios y saltos de línea

    if (command == "MEDIR_DISTANCIA") {
      float distancia = medirDistancia();
      Serial.println(distancia);
    } else if (command == "ACTIVAR_MOTOR") {
      digitalWrite(MOTOR_PIN, HIGH);  // Encender motor
      Serial.println("MOTOR_ACTIVADO");
    } else if (command == "DETENER_MOTOR") {
      digitalWrite(MOTOR_PIN, LOW);   // Apagar motor
      Serial.println("MOTOR_DETENIDO");
    } else if (command == "ACTIVAR_PISTON") {
      digitalWrite(PISTON_PIN, HIGH);  // Activar pistón
      delay(1000);  // Simular movimiento del pistón
      digitalWrite(PISTON_PIN, LOW);   // Desactivar pistón
      Serial.println("PISTON_ACTIVADO");
    } else if (command == "DETECTAR_COCO") {
      // Simular detección del coco (puedes conectar un sensor aquí)
      bool cocoDetectado = false; // Cambia esto según tu sensor

      if (cocoDetectado) {
        Serial.println("COCO_DETECTADO");
      } else {
        Serial.println("NO_COCO");
      }
    }
  }
}

// Función para medir la distancia usando HC-SR04
float medirDistancia() {
  // Enviar un pulso de 10us
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);

  // Medir la duración del pulso en el pin de ECHO
  long duracion = pulseIn(ECHO_PIN, HIGH);

  // Calcular la distancia en cm
  float distancia = duracion * 0.034 / 2;
  return distancia;
}
