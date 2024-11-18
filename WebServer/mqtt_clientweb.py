import sys
import paho.mqtt.client as mqtt
import logging
from configweb import Config
from models import db, Weights, Alarms
from datetime import datetime, timezone
from app import app  # Import Flask-App

class MQTTClient:
    def __init__(self, broker, port, username=None, password=None, logger=None):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.logger = logger or logging.getLogger(__name__)

        if username and password:
            self.client.username_pw_set(username, password)

        # Setze alle Callback-Funktionen
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect

        # Hier explizit den on_message Callback festlegen
        self.client.on_message = self.on_message
        self.client.on_subscribe = self.on_subscribe

    def on_subscribe(self, client, userdata, mid, granted_qos):
        print(f"Subscribed successfully with QoS {granted_qos}")
        self.logger.info(f"Subscribed successfully with QoS {granted_qos}")

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Connected successfully")
        else:
            self.logger.error(f"Connect failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        self.logger.info("Disconnected with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        print("on_message called")
        print(f"Message received: {msg.payload.decode()} on topic: {msg.topic}")
        self.logger.info(f"Received message: {msg.payload.decode()} on topic: {msg.topic}")

        if msg.topic == "mailbox/sensors":
            try:
                data = float(msg.payload.decode())
                with app.app_context():
                    new_weight = Weights(
                        timestamp=datetime.now(timezone.utc),
                        sensor_id=1,
                        value=data
                    )
                    db.session.add(new_weight)
                    db.session.commit()
                    self.logger.info(f"Weight data saved: {data}")
            except Exception as e:
                self.logger.error(f"Error saving weight data: {e}")

        elif msg.topic == "mailbox/alarms":
            try:
                alarm_value = msg.payload.decode()
                with app.app_context():
                    new_alarm = Alarms(
                        timestamp=datetime.now(timezone.utc),
                        sensor_id=1,
                        value=alarm_value
                    )
                    db.session.add(new_alarm)
                    db.session.commit()
                    self.logger.info(f"Alarm data saved: {alarm_value}")
            except Exception as e:
                self.logger.error(f"Error saving alarm data: {e}")


    def set_on_message(self, on_message):
        self.client.on_message = on_message

    def subscribe(self, topic):
        self.client.subscribe(topic)
        self.logger.info(f"Subscribed to topic: {topic}")

    def send(self, topic, payload):
        self.client.publish(topic, payload)
        self.logger.info(f"Sent message: {payload} to topic: {topic}")

    def run(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            
            # Abonniere die Themen
            self.subscribe("mailbox/sensors")
            self.subscribe("mailbox/alarms")

            # Starte die Endlosschleife
            self.client.loop_forever()
        except Exception as e:
            self.logger.error(f"Failed to connect to MQTT broker: {e}")
            sys.exit(1)



if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    config = Config()

    mqtt_client = MQTTClient(
        broker=config.MQTT_BROKER,
        port=config.MQTT_PORT,
        username=config.MQTT_USERNAME,
        password=config.MQTT_PASSWORD
    )

    mqtt_client.subscribe("mailbox/sensors")
    mqtt_client.subscribe("mailbox/alarms")
    mqtt_client.run()
