import yaml

class Config:
    def __init__(self, config_file):
        with open(config_file, 'r') as file:
            config = yaml.safe_load(file)
        
        self.mqtt_broker = config['mqtt'].get('broker')
        self.mqtt_port = config['mqtt'].get('port')
        self.mqtt_client_id = config['mqtt'].get('client_id')
        self.mqtt_topic = config['mqtt'].get('topic')
        self.mqtt_qos = config['mqtt'].get('qos')
        self.mqtt_keep_alive = config['mqtt'].get('keep_alive')
        self.mqtt_clean_session = config['mqtt'].get('clean_session')
        self.mqtt_username = config['mqtt'].get('username')
        self.mqtt_password = config['mqtt'].get('password')

        self.db_host = config['database'].get('host')
        self.db_port = config['database'].get('port')
        self.db_name = config['database'].get('name')
        self.db_user = config['database'].get('user')
        self.db_password = config['database'].get('password')

        self.email_smtp_server = config['email'].get('smtp_server')
        self.email_port = config['email'].get('port')
        self.email_username = config['email'].get('username')
        self.email_password = config['email'].get('password')
        self.email_from_address = config['email'].get('from_address')

        self.log_level = config['logging'].get('level')
        self.log_file = config['logging'].get('file')

if __name__ == "__main__":
    config = Config('config.yml')
    print(config.mqtt_broker)
    print(config.db_host)
    print(config.email_smtp_server)
    print(config.log_level)