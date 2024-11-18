import sys
import paho.mqtt.client as mqtt
import logging
from datetime import datetime
from models import db, Weights, Alarms
from app import app, send_weight_update, send_alarm_update
from configweb import config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MQTTClient:
    def __init__(self, broker, port, username=None, password=None):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        if username and password:
            self.client.username_pw_set(username, password)
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.client.connect(self.broker, self.port, 60)

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected successfully")
            client.subscribe("mailbox/sensors")
            client.subscribe("mailbox/alarms")
        else:
            logger.error(f"Connect failed with code {rc}")

    def on_message(self, client, userdata, msg):
        logger.info(f"Received message: {msg.payload.decode()} on topic: {msg.topic}")
        timestamp = datetime.utcnow()

        with app.app_context():  # Stelle sicher, dass wir uns im Anwendungskontext befinden
            if msg.topic == "mailbox/sensors":
                value = float(msg.payload.decode())
                weight_entry = Weights(sensor_id=1, value=value, timestamp=timestamp)
                db.session.add(weight_entry)
                db.session.commit()
                send_weight_update(1, value, timestamp)

            elif msg.topic == "mailbox/alarms":
                alarm_message = msg.payload.decode()
                alarm_entry = Alarms(sensor_id=1, value=alarm_message, timestamp=timestamp)
                db.session.add(alarm_entry)
                db.session.commit()
                send_alarm_update(1, alarm_message, timestamp)

    def run(self):
        self.client.loop_forever()

if __name__ == '__main__':
    try:
        mqtt_client = MQTTClient(config.MQTT_BROKER, config.MQTT_PORT, config.MQTT_USERNAME, config.MQTT_PASSWORD)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    mqtt_client.run()
