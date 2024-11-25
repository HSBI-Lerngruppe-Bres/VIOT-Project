import yaml
import os

class Config:
    def __init__(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.yml')
        with open(config_path, 'r') as file:
            config = yaml.safe_load(file)

        # Flask-Konfiguration
        self.SECRET_KEY = config['flask']['secret_key']
        self.DEBUG = config['flask']['debug']

        # MQTT-Konfiguration
        self.MQTT_BROKER = config['mqtt']['broker']
        self.MQTT_PORT = config['mqtt']['port']
        self.MQTT_CLIENT_ID = config['mqtt']['client_id']
        self.MQTT_USERNAME = config['mqtt']['username']
        self.MQTT_PASSWORD = config['mqtt']['password']

        self.DB_HOST = config['database'].get('host')
        self.DB_PORT = config['database'].get('port')
        self.DB_NAME = config['database'].get('name')
        self.DB_USER = config['database'].get('user')
        self.DB_PASSWORD = config['database'].get('password')

        self.EMAIL_SMTP_SERVER = config['email'].get('smtp_server')
        self.EMAIL_PORT = config['email'].get('port')
        self.EMAIL_USERNAME = config['email'].get('username')
        self.EMAIL_PASSWORD = config['email'].get('password')
        self.EMAIL_FROM_ADDRESS = config['email'].get('from_address')

        self.LOG_LEVEL = config['logging'].get('level')
        self.LOG_FILE = config['logging'].get('file')

        self.DB_URI = f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
