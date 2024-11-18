from configweb import Config
from email_server import EmailServer
import paho.mqtt.client as mqtt
from models import db, Weights, UpperThreshold, ThresholdSensitivity, EmailNotification, Alarms
from sqlalchemy import func
from psycopg2.errors import UniqueViolation
from datetime import datetime, timedelta
import logging
import json

logger = logging.getLogger(__name__)
mqtt_client = mqtt.Client()


def add_weight(sensor_id, weight):
    """
    Adds a new weight entry to the database.

    Args:
        sensor_id (int): The ID of the sensor.
        weight (int): The weight value to be added.

    Exceptions:
        Rolls back the session if an exception occurs during the commit.

    Closes the session after the operation is complete.
    """
    try:
        new_weight = Weights(timestamp=datetime.now(), sensor_id=sensor_id, value=weight)
        db.session.add(new_weight)
        db.session.commit()
        logger.info(f"Added weight: {weight}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding weight: {e}")
        
def add_alarm(sensor_id, weight):
    """
    Adds a new alarm entry to the database.

    Args:
        sensor_id (int): The ID of the sensor.
        weight (int): The weight value that triggered the alarm.

    Exceptions:
        Rolls back the session if an exception occurs during the commit.

    Closes the session after the operation is complete.
    """
    try:
        new_alarm = Alarms(timestamp=datetime.now(), sensor_id=sensor_id, value=weight)
        db.session.add(new_alarm)
        db.session.commit()
        logger.info(f"Added alarm: {weight}")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding alarm: {e}")
        
def get_average_weight(sensor_id):
    """
    Calculates the average weight value of the last minute for a given sensor.

    Args:
        sensor_id (int): The ID of the sensor.

    Returns:
        float: The average weight value of the last minute.

    Exceptions:
        Rolls back the session if an exception occurs during the query.

    Closes the session after the operation is complete.
    """
    try:
        one_minute_ago = datetime.now() - timedelta(minutes=1)
        avg_weight = db.session.query(func.avg(Weights.value)).filter(
            Weights.sensor_id == sensor_id,
            Weights.timestamp >= one_minute_ago
        ).scalar()
        if avg_weight is not None:
            logger.info(f"Average weight for sensor_id {sensor_id} in the last minute: {avg_weight}")
            return avg_weight
        else:
            logger.info(f"No weight data found for sensor_id {sensor_id} in the last minute.")
            raise ValueError(f"No weight data found for sensor_id {sensor_id} in the last minute.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error calculating average weight: {e}")
        raise
            
def get_upper_threshold(sensor_id):
    """
    Retrieves the upper threshold value for a given sensor.

    Args:
        sensor_id (int): The ID of the sensor.

    Returns:
        float: The upper threshold value for the sensor.

    Exceptions:
        Rolls back the session if an exception occurs during the query.

    Closes the session after the operation is complete.
    """
    try:
        upper_threshold = db.session.query(UpperThreshold.value).filter(
            UpperThreshold.sensor_id == sensor_id
        ).scalar()
        if upper_threshold is not None:
            logger.info(f"Upper threshold for sensor_id {sensor_id}: {upper_threshold}")
            return upper_threshold
        else:
            logger.info(f"No upper threshold found for sensor_id {sensor_id}.")
            raise ValueError(f"No upper threshold found for sensor_id {sensor_id}.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error retrieving upper threshold: {e}")
        raise
        
def get_email_adresses(sensor_id):
    """
    Retrieves the email addresses associated with a given sensor.

    Args:
        sensor_id (int): The ID of the sensor.

    Returns:
        list: A list of email addresses associated with the sensor.

    Exceptions:
        Rolls back the session if an exception occurs during the query.

    Closes the session after the operation is complete.
    """
    try:
        email_addresses = db.session.query(EmailNotification.email_address).filter(
            EmailNotification.sensor_id == sensor_id
        ).all()
        email_list = [email[0] for email in email_addresses]
        if not email_list:
            logger.info(f"No email addresses found for sensor_id {sensor_id}.")
            return []
        return email_list
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error retrieving email addresses: {e}")
        raise
        
def get_threshold_sensitivity(sensor_id):
    """
    Retrieves the threshold sensitivity value for a given sensor.

    Args:
        sensor_id (int): The ID of the sensor.

    Returns:
        float: The threshold sensitivity value for the sensor.

    Exceptions:
        Rolls back the session if an exception occurs during the query.

    Closes the session after the operation is complete.
    """
    try:
        threshold_sensitivity = db.session.query(ThresholdSensitivity.value).filter(
            ThresholdSensitivity.sensor_id == sensor_id
        ).scalar()
        if threshold_sensitivity is not None:
            logger.info(f"Threshold sensitivity for sensor_id {sensor_id}: {threshold_sensitivity}")
            return threshold_sensitivity
        else:
            logger.info(f"No threshold sensitivity found for sensor_id {sensor_id}.")
            raise ValueError(f"No threshold sensitivity found for sensor_id {sensor_id}.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error retrieving threshold sensitivity: {e}")
        raise

def initialize_sensor(sensor_id):
    """
    Initializes a sensor by setting default values for the sensor.

    Args:
        sensor_id (int): The ID of the sensor.

    Exceptions:
        Rolls back the session if an exception occurs during the commit.

    Closes the session after the operation is complete.
    """
    try:
        new_upper_threshold = UpperThreshold(sensor_id=sensor_id, value=5)
        new_threshold_sensitivity = ThresholdSensitivity(sensor_id=sensor_id, value=5)
        db.session.add(new_upper_threshold)
        db.session.add(new_threshold_sensitivity)
        db.session.commit()
        logger.info(f"Sensor {sensor_id} initialized.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error initializing sensor: {e}")

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
        mqtt_client.subscribe("mailbox/+/weight")
        mqtt_client.subscribe("mailbox/+/alarm")
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
    email_server = userdata['email_server']    

    if event_type == "weight":
        try:
            weight = json.loads(msg.payload)
            add_weight(sensor_id=sensor_id, weight=weight)
            upper_threshold = get_upper_threshold(sensor_id)
            average_weight = get_average_weight(sensor_id)
            if average_weight + upper_threshold > weight:
                return
            email_adresses = get_email_adresses(sensor_id)
            package_weight = weight - (average_weight)
            send_emails(email_server, "NEW PACKAGE", f"New package detected with weight {package_weight}", email_adresses)
            lower_threshold = weight - get_threshold_sensitivity(sensor_id)
            mqtt_client.publish(f"mailbox/{sensor_id}/arm_alarm", json.dumps({"value": lower_threshold}))
        except UniqueViolation as e:
            initialize_sensor(sensor_id)
            logger.error(f"Error processing weight event: {e} - Sensor initialized.")            
        except Exception as e:
            logger.error(f"Error processing weight event: {e}")
    elif event_type == "alarm":
        weight = json.loads(msg.payload)["value"]
        add_alarm(sensor_id=sensor_id, weight=weight)
        email_adresses = get_email_adresses(sensor_id)
        send_emails(email_server, "ALARM", f"Alarm detected with value {weight}", email_adresses)
    else:
        logger.warning(f"Unknown event type: {event_type}")
        
def control_server_task():
    config = Config()
    
    logging.basicConfig(level=config.LOG_LEVEL.upper(),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    logger.info("Configuration loaded successfully.")
    
    email_server = EmailServer(
        config.EMAIL_SMTP_SERVER, 
        config.EMAIL_PORT, 
        config.EMAIL_USERNAME, 
        config.EMAIL_PASSWORD
    )
    
    mqtt_client.on_connect = on_connect
    mqtt_client.on_disconnect = on_disconnect
    mqtt_client.on_message = on_message
    mqtt_client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
    mqtt_client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
    mqtt_client.user_data_set({
        'email_server': email_server
    })
    
    try:
        mqtt_client.loop_forever()
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
    finally:
        logger.info("Resources cleaned up and server stopped.")

if __name__ == "__main__":
    control_server_task()