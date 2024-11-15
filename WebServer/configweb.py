import yaml
import os

class Config:
    def __init__(self):
        # Lade die Konfigurationsdatei
        config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Flask-Konfiguration
        self.SECRET_KEY = config['flask']['secret_key']

        # MQTT-Konfiguration
        self.MQTT_BROKER = config['mqtt']['broker']
        self.MQTT_PORT = config['mqtt']['port']
        self.MQTT_CLIENT_ID = config['mqtt']['client_id']
        self.MQTT_TOPIC = config['mqtt']['topic']
        self.MQTT_QOS = config['mqtt']['qos']
        self.MQTT_KEEP_ALIVE = config['mqtt']['keep_alive']
        self.MQTT_CLEAN_SESSION = config['mqtt']['clean_session']
        self.MQTT_USERNAME = config['mqtt']['username']
        self.MQTT_PASSWORD = config['mqtt']['password']

        # Datenbank-Konfiguration
        self.DB_HOST = config['database']['host']
        self.DB_PORT = config['database']['port']
        self.DB_NAME = config['database']['name']
        self.DB_USER = config['database']['user']
        self.DB_PASSWORD = config['database']['password']

# Beispielverwendung
config = Config()
print("MQTT Broker:", config.MQTT_BROKER)
print("Datenbankname:", config.DB_NAME)
