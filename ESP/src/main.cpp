#include <Arduino.h>
#include <HX711.h>
#include <WiFi.h>
#include <PubSubClient.h>
#include "config.h"

WiFiClient espClient;
PubSubClient client(espClient);
HX711 scale;

// Alarm und Gewichtssensor Variablen
int threshold = 200;          // Beispiel-Schwellenwert für das Gewicht in Gramm
bool alarmArmed = false;      // Statusvariable: gibt an, ob der Alarm scharfgestellt ist
unsigned long disarmTime = 0; // Zeitpunkt, an dem der Alarm zuletzt deaktiviert wurde (in Millisekunden seit Start)
#define BUZZER_PIN 15         // GPIO for buzzer (D15)

// Funktionsdeklarationen
void setup_wifi();
void callback(char *topic, byte *message, unsigned int length);
void reconnect();
int readWeightSensor();

void setup()
{
  Serial.begin(115200);                // Startet die serielle Kommunikation
  setup_wifi();                        // Initialisiert die WLAN-Verbindung
  client.setServer(mqtt_server, 1883); // Setzt den MQTT-Server und Port
  client.setCallback(callback);        // Setzt die Funktion, die bei eingehenden MQTT-Nachrichten aufgerufen wird
}

// Herstellen einer WLAN-Verbindung
void setup_wifi()
{
  WiFi.begin(wifi_ssid, wifi_password); // SSID und Passwort des WLANs
  while (WiFi.status() != WL_CONNECTED)
  { // Wartet, bis die WLAN-Verbindung hergestellt ist
    delay(500);
    Serial.print("."); // Zeigt Verbindungsschritte im seriellen Monitor
  }
  Serial.println("WiFi verbunden"); // Meldet erfolgreiche WLAN-Verbindung
}

void callback(char *topic, byte *message, unsigned int length)
{
  // wird aufgerufen, wenn eine Nachricht vom MQTT-Broker empfangen wird
  String messageTemp;
  for (int i = 0; i < length; i++)
  {
    messageTemp += (char)message[i];
  }

  if (String(topic) == "mailbox/" + String(sensor_id) + "/disarm_alarm")
  {
    disarmTime = millis(); // Setzt den Zeitpunkt des Deaktivierens auf die aktuelle Zeit
    alarmArmed = false;
    digitalWrite(BUZZER_PIN, LOW);
  }
  else if (String(topic) == "mailbox/" + String(sensor_id) + "/arm_alarm")
  {
    alarmArmed = true; // Setzt die Alarmstatusvariable auf "scharfgestellt"

    // Threshold aus der Nachricht extrahieren und ändern
    int newThreshold = messageTemp.toInt(); // Konvertiert die Nachricht in einen Integer
    if (newThreshold > 0)
    {                           // Nur positive Werte akzeptieren
      threshold = newThreshold; // Aktualisiert den Threshold-Wert
      Serial.print("Neuer Threshold gesetzt: ");
      Serial.println(threshold);
    }
    else
    {
      Serial.println("Ungültiger Threshold-Wert empfangen. Threshold bleibt unverändert.");
    }
  }
}

void loop()
{
  if (!client.connected())
  {              // Prüft, ob der ESP32 noch mit dem MQTT-Broker verbunden ist
    reconnect(); // Versucht die Verbindung zum MQTT-Broker wiederherzustellen
  }
  client.loop(); // Hält die MQTT-Verbindung aufrecht und verarbeitet eingehende Nachrichten

  int weight = readWeightSensor(); // Ruft die aktuelle Gewichtsmessung vom Sensor ab

  // Gewicht senden
  client.publish(("mailbox/" + String(sensor_id) + "/weight").c_str(), String(weight).c_str());

  // Alarm Logik
  if (alarmArmed && millis() - disarmTime > 300000 && weight < threshold)
  {
    // Falls der Alarm scharfgestellt ist und die 5-Minuten-Sperrzeit abgelaufen ist und das Gewicht unter dem Schwellenwert liegt, wird der Alarm ausgelöst
    client.publish(("mailbox/" + String(sensor_id) + "/alarm").c_str(), "1"); // Sendet eine Alarmnachricht über MQTT
  }
}

int readWeightSensor()
{
  float weight = 0;
  // Read weight value from the HX711
  if (scale.is_ready())
  {
    weight = scale.get_units(10); // Average 10 readings for stability
    Serial.print("Weight: ");
    Serial.print(weight);
    Serial.println(" grams");
  }
  else
  {
    Serial.println("HX711 not ready");
  }

  delay(1000); // Read weight every second
  return weight;
}

// falls die Verbindung zum MQTT-Broker verloren geht
void reconnect()
{
  while (!client.connected())
  { // Solange der Client nicht verbunden ist, versucht er sich zu verbinden
    if (client.connect("ESP32Client", mqtt_user, mqtt_password))
    {
      client.subscribe(("mailbox/" + String(sensor_id) + "/disarm_alarm").c_str()); // Abonniert das Topic zum Deaktivieren des Alarms
      client.subscribe(("mailbox/" + String(sensor_id) + "/arm_alarm").c_str());    // Abonniert das Topic zum Aktivieren des Alarms
    }
    else
    {
      delay(5000); // Falls die Verbindung fehlschlägt, wartet er 5 Sekunden, bevor er es erneut versucht
    }
  }
}
