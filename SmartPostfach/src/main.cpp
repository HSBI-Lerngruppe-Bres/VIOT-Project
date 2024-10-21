#include <Arduino.h>
#include <HX711.h>

#define DOUT_PIN 2     // GPIO for data pin (D2)
#define SCK_PIN 4      // GPIO for clock pin (D4)
#define BUZZER_PIN 15  // GPIO for buzzer (D15)

HX711 scale;

void setup() {
  // Initialize serial communication for debugging
  Serial.begin(115200);
  delay(5000);

  // Initialize the buzzer
  pinMode(BUZZER_PIN, OUTPUT);

  // Buzz on startup
  digitalWrite(BUZZER_PIN, HIGH);
  delay(500);  // 500ms buzz duration
  digitalWrite(BUZZER_PIN, LOW);

  // Initialize the HX711 weight sensor
  scale.begin(DOUT_PIN, SCK_PIN);

  // Check if the HX711 is connected properly
  if (scale.is_ready()) {
    Serial.println("HX711 initialized successfully.");
  } else {
    Serial.println("HX711 not found. Please check the wiring.");
    while (1);  // Stop if the HX711 isn't ready
  }

  // Set your calibration factor for HX711
  scale.set_scale(-582.72);  // Replace with your calibration factor
  scale.tare();              // Reset scale to 0
}

void loop() {
  // Read weight value from the HX711
  if (scale.is_ready()) {
    float weight = scale.get_units(10);  // Average 10 readings for stability
    Serial.print("Weight: ");
    Serial.print(weight);
    Serial.println(" grams");
  } else {
    Serial.println("HX711 not ready");
  }

  delay(1000);  // Read weight every second
}
