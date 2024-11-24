import sys
import os
import paho.mqtt.client as mqtt
import logging
from datetime import datetime
from models import db, Weights, Alarms, EmailNotification, AlarmStatus
from app import app
from configweb import config
from email_server import EmailServer


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

    def is_alarm_active(self):
         with app.app_context():
            alarm_status = AlarmStatus.query.first()
            if alarm_status:
                print(f"Alarmstatus in der Datenbank: {alarm_status.is_active}")
                return alarm_status.is_active
            else:
                print("Kein Alarmstatus in der Datenbank. Standardmäßig: AN")
                return True  # Standardmäßig aktiv, wenn kein Status vorhanden
            
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
            if msg.topic == "mailbox/alarms":
                print(f"Alarm empfangen: {msg.payload.decode()}")
                if not self.is_alarm_active():
                    print("Alarm ignoriert, da der Alarm deaktiviert ist.")
                    return

                alarm_message = msg.payload.decode()
                print(f"Speichere Alarm: {alarm_message}")
                alarm_entry = Alarms(sensor_id=1, value=alarm_message, timestamp=timestamp)
                db.session.add(alarm_entry)
                db.session.commit()
                print("Alarm erfolgreich gespeichert.")
                #self.send_alarm_update(1, alarm_message, timestamp)

            elif msg.topic == "mailbox/sensors":
                value = float(msg.payload.decode())
                print(f"Speichere Gewicht: {value}")
                weight_entry = Weights(sensor_id=1, value=value, timestamp=timestamp)
                db.session.add(weight_entry)
                db.session.commit()
                #send_weight_update(1, value, timestamp)


    def send_alarm_update(sensor_id, alarm_message, timestamp):
        with app.app_context():
            email_addresses = EmailNotification.query.filter_by(sensor_id=sensor_id).all()
            if not email_addresses:
                return

            email_server = EmailServer(config.EMAIL_SMTP_SERVER, config.EMAIL_PORT, config.EMAIL_USERNAME, config.EMAIL_PASSWORD)
            email_server.connect()

            for entry in email_addresses:
                email_server.send_email(
                    entry.email_address,
                    f"Alarm ausgelöst: {alarm_message}",
                    f"Ein Alarm wurde ausgelöst:\n\nSensor ID: {sensor_id}\nAlarm: {alarm_message}\nZeit: {timestamp}"
                )

            email_server.disconnect()


    def run(self):
        self.client.loop_forever()

if __name__ == '__main__':
    try:
        mqtt_client = MQTTClient(config.MQTT_BROKER, config.MQTT_PORT, config.MQTT_USERNAME, config.MQTT_PASSWORD)
    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)
    mqtt_client.run()
