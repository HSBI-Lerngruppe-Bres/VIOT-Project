from config import Config
from database_connector import DatabaseConnector
from email_server import EmailServer
import paho.mqtt.client as mqtt

import logging
import json

logger = logging.getLogger(__name__)

def send_emails(email_server, subject, body, email_addresses):
    logger.info(f"Sending email to {email_addresses} with subject: {subject} and body: {body}")
    for email_address in email_addresses:
        email_server.send_email(email_address, subject, body)

def on_connect(mqtt_client, userdata, flags, rc):
    """
    Callback function for when the client receives a CONNACK response from the server.

    Args:
        mqtt_client (mqtt.Client): The client instance for this callback.
        userdata (any): The private user data as set in Client() or userdata_set().
        flags (dict): Response flags sent by the broker.
        rc (int): The connection result.
    """
    if rc == 0:
        logger.info("Connected successfully")
    else:
        logger.error(f"Connect failed with code {rc}")

def on_disconnect(mqtt_client, userdata, rc):
    """
    Callback function for when the client disconnects from the broker.

    Args:
        mqtt_client (mqtt.Client): The client instance for this callback.
        userdata (any): The private user data as set in Client() or userdata_set().
        rc (int): The disconnection result.
    """
    logger.info("Disconnected with result code " + str(rc))

def on_message(mqtt_client, userdata, msg):
    """
    Callback function for when a PUBLISH message is received from the server.

    Args:
        mqtt_client (mqtt.Client): The client instance for this callback.
        userdata (any): The private user data as set in Client() or userdata_set().
        msg (mqtt.MQTTMessage): The message instance containing topic and payload.
    """
    logger.info(f"Received message: {msg.payload} on topic: {msg.topic}")
    
    splitted_topic = msg.topic.split('/')
    event_type = splitted_topic[2]
    sensor_id = splitted_topic[1]
    db_connector = userdata['db_connector']
    email_server = userdata['email_server']    

    if event_type == "weight":
        try:
            weight = json.loads(msg.payload)["value"]
            db_connector.add_weight(sensor_id=sensor_id, weight=weight)
            upper_threshold = db_connector.get_upper_threshold(sensor_id)
            average_weight = db_connector.get_average_weight(sensor_id)
            if average_weight + upper_threshold > weight:
                return
            email_adresses = db_connector.get_email_adresses(sensor_id)
            package_weight = weight - (average_weight)
            send_emails(email_server, "NEW PACKAGE", f"New package detected with weight {package_weight}", email_adresses)
            lower_threshold = weight - db_connector.get_threshold_sensitivity(sensor_id)
            mqtt_client.publish(f"mailbox/{sensor_id}/arm_alarm", json.dumps({"value": lower_threshold}))
        except Exception as e:
            db_connector.initialize_sensor(sensor_id)
            logger.error(f"Error processing weight event: {e} - Sensor initialized.")            
    elif event_type == "alarm":
        alarm = json.loads(msg.payload)["value"]
        db_connector.add_alarm(sensor_id=sensor_id, alarm=alarm)
        email_adresses = db_connector.get_email_adresses(sensor_id)
        send_emails(email_server, "ALARM", f"Alarm detected with value {alarm}", email_adresses)
    else:
        logger.warning(f"Unknown event type: {event_type}")
        
def main():
    config = Config('config.yml')
    
    logging.basicConfig(level=config.log_level.upper(),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    file_handler = logging.FileHandler(config.log_file)
    file_handler.setLevel(config.log_level.upper())
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.log_level.upper())
    console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info("Configuration loaded successfully.")
    
    db_connector = DatabaseConnector(
        config.db_user, 
        config.db_password, 
        config.db_host, 
        config.db_port, 
        config.db_name,
        logger=logger
    )
    
    email_server = EmailServer(
        config.email_smtp_server, 
        config.email_port, 
        config.email_username, 
        config.email_password
    )
    
    mqtt_client = mqtt.Client()
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set(config.mqtt_username, config.mqtt_password)
    mqtt_client.connect(config.mqtt_broker, config.mqtt_port, 60)
    mqtt_client.user_data_set({
        'db_connector': db_connector,
        'email_server': email_server
    })
    
    mqtt_client.subscribe("mailbox/+/weight")
    mqtt_client.subscribe("mailbox/+/alarm")
    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
    finally:
        logger.info("Resources cleaned up and server stopped.")

if __name__ == "__main__":
    main()