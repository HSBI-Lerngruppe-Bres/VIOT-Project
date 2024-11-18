import sys
import paho.mqtt.client as mqtt
import logging
from configweb import Config

class MQTTClient:
    def __init__(self, broker, port, username=None, password=None, logger=None):
        self.broker = broker
        self.port = port
        self.client = mqtt.Client()
        self.logger = logger or logging.getLogger(__name__)

        if username and password:
            self.client.username_pw_set(username, password)

        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.logger.info("Connected successfully")
        else:
            self.logger.error(f"Connect failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        self.logger.info("Disconnected with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        self.logger.info(f"Received message: {msg.payload.decode()} on topic: {msg.topic}")

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
            self.client.loop_start()
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

    mqtt_client.subscribe(config.MQTT_TOPIC)
    mqtt_client.send(config.MQTT_TOPIC, "Test message from WebServer")
    mqtt_client.run()
