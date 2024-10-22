import sys
import paho.mqtt.client as mqtt
import logging

class MQTTClient:
    def __init__(self, broker, port, username=None, password=None, logger=None):
        """
        Initialize the MQTTClient instance.

        Args:
            broker (str): The address of the MQTT broker.
            port (int): The port number to connect to the MQTT broker.
            username (str, optional): Username for broker authentication.
            password (str, optional): Password for broker authentication.
            logger (logging.Logger, optional): Logger instance for logging messages.
        """
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
        """
        Callback function for when the client receives a CONNACK response from the server.

        Args:
            client (mqtt.Client): The client instance for this callback.
            userdata (any): The private user data as set in Client() or userdata_set().
            flags (dict): Response flags sent by the broker.
            rc (int): The connection result.
        """
        if rc == 0:
            self.logger.info("Connected successfully")
        else:
            self.logger.error(f"Connect failed with code {rc}")

    def on_disconnect(self, client, userdata, rc):
        """
        Callback function for when the client disconnects from the broker.

        Args:
            client (mqtt.Client): The client instance for this callback.
            userdata (any): The private user data as set in Client() or userdata_set().
            rc (int): The disconnection result.
        """
        self.logger.info("Disconnected with result code " + str(rc))

    def on_message(self, client, userdata, msg):
        """
        Callback function for when a PUBLISH message is received from the server.

        Args:
            client (mqtt.Client): The client instance for this callback.
            userdata (any): The private user data as set in Client() or userdata_set().
            msg (mqtt.MQTTMessage): The message instance containing topic and payload.
        """
        self.logger.info(f"Received message: {msg.payload} on topic: {msg.topic}")

    def set_on_message(self, on_message):
        """
        Set a custom callback function for when a PUBLISH message is received from the server.

        Args:
            on_message (function): The callback function to handle received messages.
        """
        self.client.on_message = on_message

    def subscribe(self, topic):
        """
        Subscribe to a topic.

        Args:
            topic (str): The topic to subscribe to.
        """
        self.client.subscribe(topic)
        self.logger.info(f"Subscribed to topic: {topic}")

    def send(self, topic, payload):
        """
        Publish a message to a topic.

        Args:
            topic (str): The topic to publish to.
            payload (str): The message payload to send.
        """
        self.client.publish(topic, payload)
        self.logger.info(f"Sent message: {payload} to topic: {topic}")

    def run(self):
        """
        Connect to the broker and start the network loop.
        """
        self.client.connect(self.broker, self.port, 60)
        self.client.loop_forever()
