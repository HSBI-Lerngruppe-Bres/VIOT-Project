#include <Arduino.h>
#include <HX711.h>
#include <PubSubClient.h>
#include <WiFi.h>

#include "config.h"

WiFiClient espClient;
PubSubClient client(espClient);
HX711 scale;

// Alarm und Gewichtssensor Variablen
int threshold = -9999999;  // Beispiel-Schwellenwert für das Gewicht in Gramm
                           // threshold is deactivated
unsigned long disarmTime =
    -999999;  // Zeitpunkt, an dem der Alarm zuletzt deaktiviert wurde (in
              // Millisekunden seit Start) Alarm zunächst aktiviert
bool alarmTriggerd = false;
#define BUZZER_PIN 15  // GPIO for buzzer (D15)
#define DOUT_PIN 2     // GPIO for data pin (D2)
#define SCK_PIN 4      // GPIO for clock pin (D4)

// Funktionsdeklarationen
void setup_wifi();
void callback(char *topic, byte *message, unsigned int length);
void reconnect();
int readWeightSensor();

void setup() {
  Serial.begin(115200);                 // Startet die serielle Kommunikation
  pinMode(BUZZER_PIN, OUTPUT);           // Setzt den Buzzer
  digitalWrite(BUZZER_PIN, LOW);         // Deaktiviert den Buzzer
  setup_wifi();                         // Initialisiert die WLAN-Verbindung
  client.setServer(mqtt_server, 1883);  // Setzt den MQTT-Server und Port
  client.setCallback(callback);  // Setzt die Funktion, die bei eingehenden
                                 // MQTT-Nachrichten aufgerufen wird
  scale.begin(DOUT_PIN, SCK_PIN);
  scale.set_scale(-582.72);  // Replace with your calibration factor
  scale.tare();              // Reset the scale to 0
}

// Herstellen einer WLAN-Verbindung
void setup_wifi() {
  WiFi.begin(wifi_ssid, wifi_password);  // SSID und Passwort des WLANs
  while (WiFi.status() !=
         WL_CONNECTED) {  // Wartet, bis die WLAN-Verbindung hergestellt ist
    delay(500);
    Serial.print(".");  // Zeigt Verbindungsschritte im
                        // seriemailbox/+/arm_alarmllen Monitor
  }
  Serial.println("WiFi verbunden");  // Meldet erfolgreiche WLAN-Verbindung
}

void callback(char *topic, byte *message, unsigned int length) {
  // wird aufgerufen, wenn eine Nachricht vom MQTT-Broker empfangen wird
  String messageTemp;
  for (int i = 0; i < length; i++) {
    messageTemp += (char)message[i];
  }

  if (String(topic) == "mailbox/" + String(sensor_id) + "/disarm_alarm") {
    disarmTime = millis();  // Setzt den Zeitpunkt des Deaktivierens auf die
                            // aktuelle Zeit
    digitalWrite(BUZZER_PIN, LOW);
  } else if (String(topic) == "mailbox/" + String(sensor_id) + "/arm_alarm") {
    // Threshold aus der Nachricht extrahieren und ändern
    int newThreshold =
        messageTemp.toInt();   // Konvertiert die Nachricht in einen Integer
    threshold = newThreshold;  // Aktualisiert den Threshold-Wert
    Serial.print("Neuer Threshold gesetzt: ");
    Serial.println(threshold);
    alarmTriggerd = false;  // Setzt den Alarm-Trigger zurück
  }
}

void loop() {
  if (!client.connected()) {  // Prüft, ob der ESP32 noch mit dem MQTT-Broker
                              // verbunden ist
    reconnect();  // Versucht die Verbindung zum MQTT-Broker wiederherzustellen
  }
  client.loop();  // Hält die MQTT-Verbindung aufrecht und verarbeitet
                  // eingehende Nachrichten
  int weight =
      readWeightSensor();  // Ruft die aktuelle Gewichtsmessung vom Sensor ab
  // Gewicht senden
  client.publish(("mailbox/" + String(sensor_id) + "/weight").c_str(),
                 String(weight).c_str());

  Serial.println("Alarm Time: " + String(millis() - disarmTime));
  // Alarm Logik
  if (!alarmTriggerd && millis() - disarmTime > 300000 && weight < threshold) {
    // Falls der Alarm scharfgestellt ist und die 5-Minuten-Sperrzeit abgelaufen
    // ist und das Gewicht unter dem Schwellenwert liegt, wird der Alarm
    // ausgelöst
    Serial.println("Alarm ausgelöst!");
    digitalWrite(BUZZER_PIN, HIGH);  // Aktiviert den Alarmton
    client.publish(("mailbox/" + String(sensor_id) + "/alarm").c_str(),
                   "1");   // Sendet eine Alarmnachricht über MQTT
    alarmTriggerd = true;  // Setzt den Alarm-Trigger auf true um zu verhindern,
                           // dass der Alarm mehrmals ausgelöst wird
  }
}

int readWeightSensor() {
  float weight = 0;
  // Read weight value from the HX711
  if (scale.is_ready()) {
    weight = scale.get_units(20);  // Average 10 readings for stability
    Serial.print("Weight: ");
    Serial.print(weight);
    Serial.println(" grams");
  } else {
    Serial.println("HX711 not ready");
  }

  delay(1000);  // Read weight every second
  return weight;
}

// falls die Verbindung zum MQTT-Broker verloren geht
void reconnect() {
  while (!client.connected()) {  // Solange der Client nicht verbunden ist,
                                 // versucht er sich zu verbinden
    Serial.println("Verbindung zum MQTT-Broker wird hergestellt...");
    if (client.connect("ESP32Client", mqtt_user, mqtt_password)) {
      Serial.println("Verbunden mit MQTT-Broker");
      client.subscribe(
          ("mailbox/" + String(sensor_id) + "/disarm_alarm")
              .c_str());  // Abonniert das Topic zum Deaktivieren des Alarms
      client.subscribe(
          ("mailbox/" + String(sensor_id) + "/arm_alarm")
              .c_str());  // Abonniert das Topic zum Aktivieren des Alarms
    } else {
      delay(5000);  // Falls die Verbindung fehlschlägt, wartet er 5 Sekunden,
                    // bevor er es erneut versucht
    }
  }
}
