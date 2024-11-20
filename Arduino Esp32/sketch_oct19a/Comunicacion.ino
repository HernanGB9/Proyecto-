#include <WiFi.h>
#include <TaskScheduler.h>

// Configuración de pines
#define TRIG_PIN 5
#define ECHO_PIN 18
#define MOTOR_PIN 2
#define SENSOR_BARRERA 15
#define PISTON_PIN 4
#define BUTTON_STOP 21
#define BUTTON_START 22

// Variables de configuración WiFi
char ssid[32];
char password[64];
uint16_t port;
WiFiServer server(0); // El puerto se configurará dinámicamente

// Estados del sistema
bool motorActive = false;
bool pistonActive = false;
bool systemActive = true;

// Scheduler
Scheduler runner;

// Declaración de funciones
void readSensors();
void handleWiFiCommands();
void handleSerialCommands();
void sendState(Stream &stream);
void getWiFiConfig();
void checkButtons();
void selectConnectionMode();

// Tareas
Task taskMeasureSensors(1000, TASK_FOREVER, &readSensors);
Task taskWiFiCommands(10, TASK_FOREVER, &handleWiFiCommands);
Task taskSerialCommands(10, TASK_FOREVER, &handleSerialCommands);
Task taskCheckButtons(100, TASK_FOREVER, &checkButtons);

// Variable para el modo de conexión
String connectionMode = "";

void setup() {
  Serial.begin(115200);

  // Configuración de pines
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(MOTOR_PIN, OUTPUT);
  pinMode(SENSOR_BARRERA, INPUT_PULLUP);
  pinMode(PISTON_PIN, OUTPUT);
  pinMode(BUTTON_STOP, INPUT_PULLUP);
  pinMode(BUTTON_START, INPUT_PULLUP);
  digitalWrite(MOTOR_PIN, LOW);
  digitalWrite(PISTON_PIN, LOW);

  // Seleccionar el modo de conexión
  selectConnectionMode();

  // Configurar tareas del Scheduler
  runner.addTask(taskMeasureSensors);
  runner.addTask(taskCheckButtons);

  // Activar solo el hilo correspondiente
  if (connectionMode == "WiFi") {
    getWiFiConfig();
    WiFi.begin(ssid, password);
    Serial.print("Conectando a WiFi");
    while (WiFi.status() != WL_CONNECTED) {
      delay(500);
      Serial.print(".");
    }
    Serial.println("\nWiFi conectado");
    Serial.print("IP asignada: ");
    Serial.println(WiFi.localIP());
    server = WiFiServer(port);
    server.begin();
    Serial.println("Servidor iniciado");
    runner.addTask(taskWiFiCommands);
    taskWiFiCommands.enable();
  } else if (connectionMode == "Serial") {
    Serial.println("Modo Serial activado.");
    runner.addTask(taskSerialCommands);
    taskSerialCommands.enable();
  }

  // Activar las tareas comunes
  taskMeasureSensors.enable();
  taskCheckButtons.enable();
}

void loop() {
  runner.execute();
}

// Leer sensores y actualizar estados
void readSensors() {
  if (!systemActive) return;

  // Medir distancia con el sensor HC-SR04
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH);
  float distance = duration / 58.2;

  // Estado del sensor de barrera
  bool sensorBarrier = digitalRead(SENSOR_BARRERA) == LOW;

  // Actualizar estado del motor y pistón según sensores
  if (distance >= 2.0 && distance <= 3.0 && !motorActive) {
    motorActive = true;
    digitalWrite(MOTOR_PIN, HIGH);
    Serial.println("Motor activado: Distancia en rango (2-3 cm)");
  }

  if (sensorBarrier && motorActive) {
    motorActive = false;
    pistonActive = true;
    digitalWrite(MOTOR_PIN, LOW);
    digitalWrite(PISTON_PIN, HIGH);
    Serial.println("Pistón activado, motor desactivado: Sensor de barrera activado");
  } else if (!sensorBarrier && pistonActive) {
    pistonActive = false;
    digitalWrite(PISTON_PIN, LOW);
    Serial.println("Pistón desactivado: Sensor de barrera desactivado");
  }
}

// Verificar botones de Paro y Arranque
void checkButtons() {
  if (digitalRead(BUTTON_STOP) == LOW) {
    systemActive = false;
    motorActive = false;
    pistonActive = false;
    digitalWrite(MOTOR_PIN, LOW);
    digitalWrite(PISTON_PIN, LOW);
    Serial.println("Sistema detenido manualmente");
  }

  if (digitalRead(BUTTON_START) == LOW) {
    systemActive = true;
    Serial.println("Sistema reanudado manualmente");
  }
}

// Manejar comandos WiFi
void handleWiFiCommands() {
  WiFiClient client = server.available();
  if (client) {
    Serial.println("Cliente conectado");
    while (client.connected()) {
      if (client.available()) {
        byte command = client.read();
        processCommand(command, client);
      }
    }
    client.stop();
    Serial.println("Cliente desconectado");
  }
}

// Manejar comandos Serial
void handleSerialCommands() {
  if (Serial.available()) {
    byte command = Serial.read();
    processCommand(command, Serial);
  }
}

// Procesar comandos (compartido entre WiFi y Serial)
void processCommand(byte command, Stream &stream) {
  switch (command) {
    case 0x01: // Encender motor
      motorActive = true;
      digitalWrite(MOTOR_PIN, HIGH);
      stream.println("Motor activado");
      break;

    case 0x02: // Apagar motor
      motorActive = false;
      digitalWrite(MOTOR_PIN, LOW);
      stream.println("Motor desactivado");
      break;

    case 0x03: // Activar pistón
      pistonActive = true;
      digitalWrite(PISTON_PIN, HIGH);
      stream.println("Pistón activado");
      break;

    case 0x04: // Desactivar pistón
      pistonActive = false;
      digitalWrite(PISTON_PIN, LOW);
      stream.println("Pistón desactivado");
      break;

    case 0x05: // Solicitar estado
      sendState(stream);
      break;

    case 0x06: // Paro de emergencia
      systemActive = false;
      motorActive = false;
      pistonActive = false;
      digitalWrite(MOTOR_PIN, LOW);
      digitalWrite(PISTON_PIN, LOW);
      stream.println("Sistema detenido manualmente");
      break;

    case 0x07: // Reanudar sistema
      systemActive = true;
      stream.println("Sistema reanudado manualmente");
      break;

    default:
      stream.println("Comando no reconocido");
      break;
  }
}

// Enviar el estado actual al cliente o Serial
void sendState(Stream &stream) {
  stream.println("Motor: " + String(motorActive ? "Encendido" : "Apagado") +
                 ", Pistón: " + String(pistonActive ? "Activado" : "Desactivado") +
                 ", Barrera: " + String(digitalRead(SENSOR_BARRERA) == LOW ? "Activado" : "No activado"));
}

// Seleccionar el modo de conexión
void selectConnectionMode() {
  while (true) {
    Serial.println("Seleccione el modo de conexión: (WiFi/Serial)");
    while (!Serial.available());
    String input = Serial.readStringUntil('\n');
    input.trim();
    if (input.equalsIgnoreCase("WiFi")) {
      connectionMode = "WiFi";
      break;
    } else if (input.equalsIgnoreCase("Serial")) {
      connectionMode = "Serial";
      break;
    } else {
      Serial.println("Entrada no válida. Por favor, ingrese 'WiFi' o 'Serial'.");
    }
  }
}

// Obtener configuración WiFi del usuario
void getWiFiConfig() {
  while (true) {
    Serial.println("Ingrese SSID:");
    while (!Serial.available());
    Serial.readBytesUntil('\n', ssid, sizeof(ssid) - 1);
    ssid[strcspn(ssid, "\n")] = 0; // Eliminar salto de línea

    Serial.println("Ingrese contraseña:");
    while (!Serial.available());
    Serial.readBytesUntil('\n', password, sizeof(password) - 1);
    password[strcspn(password, "\n")] = 0;

    Serial.println("Ingrese el puerto:");
    while (!Serial.available());
    String portInput = Serial.readStringUntil('\n');
    portInput.trim();
    port = portInput.toInt();

    if (port > 0 && port <= 65535) {
      Serial.println("Datos ingresados:");
      Serial.print("SSID: "); Serial.println(ssid);
      Serial.print("Contraseña: "); Serial.println(password);
      Serial.print("Puerto: "); Serial.println(port);
      Serial.println("¿Son correctos? (si/no):");
      while (!Serial.available());
      String response = Serial.readStringUntil('\n');
      response.trim();
      if (response.equalsIgnoreCase("si")) break;
    } else {
      Serial.println("Puerto inválido. Intente nuevamente.");
    }
  }
}
