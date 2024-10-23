from config import Config
from database_connector import DatabaseConnector
from mqtt_client import MQTTClient
import logging
import time

def main():
    # Load configuration
    config = Config('config.yml')
    
    # Set up logging
    logging.basicConfig(filename=config.log_file, level=config.log_level.upper(),
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)
    
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
    
    mqtt_client = MQTTClient(
        config.mqtt_broker, 
        config.mqtt_port, 
        config.mqtt_username, 
        config.mqtt_password,
        logger=logger
    )
    
    mqtt_client.subscribe("test_topic")
        
    try:
        mqtt_client.run()
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Server stopped by user.")
    finally:
        logger.info("Resources cleaned up and server stopped.")

if __name__ == "__main__":
    main()