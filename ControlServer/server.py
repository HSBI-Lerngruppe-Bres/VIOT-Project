from config import Config
from database_connector import DatabaseConnector
from mqtt_client import MQTTClient
from email_server import EmailServer
import paho.mqtt.client as mqtt

import logging

logger = logging.getLogger(__name__)

def on_connect(client, userdata, flags, rc):
    """
    Callback function for when the client receives a CONNACK response from the server.

    Args:
        client (mqtt.Client): The client instance for this callback.
        userdata (any): The private user data as set in Client() or userdata_set().
        flags (dict): Response flags sent by the broker.
        rc (int): The connection result.
    """
    if rc == 0:
        logger.info("Connected successfully")
    else:
        logger.error(f"Connect failed with code {rc}")

def on_disconnect(client, userdata, rc):
    """
    Callback function for when the client disconnects from the broker.

    Args:
        client (mqtt.Client): The client instance for this callback.
        userdata (any): The private user data as set in Client() or userdata_set().
        rc (int): The disconnection result.
    """
    logger.info("Disconnected with result code " + str(rc))

def on_message(client, userdata, msg):
    """
    Callback function for when a PUBLISH message is received from the server.

    Args:
        client (mqtt.Client): The client instance for this callback.
        userdata (any): The private user data as set in Client() or userdata_set().
        msg (mqtt.MQTTMessage): The message instance containing topic and payload.
    """
    logger.info(f"Received message: {msg.payload} on topic: {msg.topic}")

def main():
    # Load configuration
    config = Config('config.yml')
    
    # Set up logging
    logging.basicConfig(level=config.log_level.upper(),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create a file handler
    file_handler = logging.FileHandler(config.log_file)
    file_handler.setLevel(config.log_level.upper())
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Create a console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.log_level.upper())
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    # Get the logger and set the handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Log configuration details
    logger.info("Configuration loaded successfully.")
    
    # Initialize database connector
    db_connector = DatabaseConnector(
        config.db_user, 
        config.db_password, 
        config.db_host, 
        config.db_port, 
        config.db_name,
        logger=logger
    )
    
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set(config.mqtt_username, config.mqtt_password)
    mqtt_client.connect(config.mqtt_broker, config.mqtt_port, 60)
    
    email_server = EmailServer(
        config.email_smtp_server, 
        config.email_port, 
        config.email_username, 
        config.email_password
    )
    
    mqtt_client.subscribe("test_topic")
    mqtt_client.publish("test_topic", "Hello, World!")

    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
    finally:
        logger.info("Resources cleaned up and server stopped.")

if __name__ == "__main__":
    main()