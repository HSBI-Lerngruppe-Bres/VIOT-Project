from sqlalchemy import create_engine
from models import Base, setup_hypertables, Weight, Alarm, UpperThreshold, EmailNotification, ThresholdSensitivity
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from datetime import datetime, timedelta


class DatabaseConnector:
    def __init__(self, username, password, host, port, database, logger=None):
        """
        Initializes the database connector with the given parameters and sets up the database engine and session.

        Args:
            username (str): The username for the database.
            password (str): The password for the database.
            host (str): The host address of the database.
            port (int): The port number to connect to the database.
            database (str): The name of the database.
        """
        self.DATABASE_URL = f"postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}"
        self.engine = create_engine(self.DATABASE_URL)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.logger = logger
        self.Base = Base
        self.Base.metadata.create_all(bind=self.engine)
        
        try:
            setup_hypertables(self.engine)
        except Exception as e:
            self.logger.error(f"Error creating hypertable: {e}")
        self.logger.info("Database tables created successfully.")
        
        
    def add_weight(self, sensor_id, weight):
        """
        Adds a new weight entry to the database.

        Args:
            sensor_id (int): The ID of the sensor.
            weight (int): The weight value to be added.

        Exceptions:
            Rolls back the session if an exception occurs during the commit.

        Closes the session after the operation is complete.
        """
        session = self.SessionLocal()
        try:
            new_weight = Weight(timestamp=datetime.now(), sensor_id=sensor_id, value=weight)
            session.add(new_weight)
            session.commit()
            self.logger.info(f"Added weight: {weight}")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error adding weight: {e}")
        finally:
            session.close()   
            
    def add_alarm(self, sensor_id, weight):
        """
        Adds a new alarm entry to the database.

        Args:
            sensor_id (int): The ID of the sensor.
            weight (int): The weight value that triggered the alarm.

        Exceptions:
            Rolls back the session if an exception occurs during the commit.

        Closes the session after the operation is complete.
        """
        session = self.SessionLocal()
        try:
            new_alarm = Alarm(timestamp=datetime.now(), sensor_id=sensor_id, value=weight)
            session.add(new_alarm)
            session.commit()
            self.logger.info(f"Added alarm: {weight}")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error adding alarm: {e}")
        finally:
            session.close()
            
    def get_average_weight(self, sensor_id):
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
        session = self.SessionLocal()
        try:
            one_minute_ago = datetime.now() - timedelta(minutes=1)
            avg_weight = session.query(func.avg(Weight.value)).filter(
                Weight.sensor_id == sensor_id,
                Weight.timestamp >= one_minute_ago
            ).scalar()
            if avg_weight is not None:
                self.logger.info(f"Average weight for sensor_id {sensor_id} in the last minute: {avg_weight}")
                return avg_weight
            else:
                self.logger.info(f"No weight data found for sensor_id {sensor_id} in the last minute.")
                raise ValueError(f"No weight data found for sensor_id {sensor_id} in the last minute.")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error calculating average weight: {e}")
            raise
        finally:
            session.close()
               
    def get_upper_threshold(self, sensor_id):
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
        session = self.SessionLocal()
        try:
            upper_threshold = session.query(UpperThreshold.value).filter(
                UpperThreshold.sensor_id == sensor_id
            ).scalar()
            if upper_threshold is not None:
                self.logger.info(f"Upper threshold for sensor_id {sensor_id}: {upper_threshold}")
                return upper_threshold
            else:
                self.logger.info(f"No upper threshold found for sensor_id {sensor_id}.")
                raise ValueError(f"No upper threshold found for sensor_id {sensor_id}.")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error retrieving upper threshold: {e}")
            raise
        finally:
            session.close()
            
    def get_email_adresses(self, sensor_id):
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
        session = self.SessionLocal()
        try:
            email_addresses = session.query(EmailNotification.email_address).filter(
            EmailNotification.sensor_id == sensor_id
            ).all()
            email_list = [email[0] for email in email_addresses]
            if not email_list:
                self.logger.info(f"No email addresses found for sensor_id {sensor_id}.")
                return []
            return email_list
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error retrieving email addresses: {e}")
            raise
        finally:
            session.close()
            
    def get_threshold_sensitivity(self, sensor_id):
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
        session = self.SessionLocal()
        try:
            threshold_sensitivity = session.query(ThresholdSensitivity.value).filter(
                ThresholdSensitivity.sensor_id == sensor_id
            ).scalar()
            if threshold_sensitivity is not None:
                self.logger.info(f"Threshold sensitivity for sensor_id {sensor_id}: {threshold_sensitivity}")
                return threshold_sensitivity
            else:
                self.logger.info(f"No threshold sensitivity found for sensor_id {sensor_id}.")
                raise ValueError(f"No threshold sensitivity found for sensor_id {sensor_id}.")
        except Exception as e:
            session.rollback()
            self.logger.error(f"Error retrieving threshold sensitivity: {e}")
            raise
        finally:
            session.close()

    def initialize_sensor(self, sensor_id):
        """
        Initializes a sensor by setting default values for the sensor.

        Args:
            sensor_id (int): The ID of the sensor.

        Exceptions:
            Rolls back the session if an exception occurs during the commit.

        Closes the session after the operation is complete.
        """
        session = self.SessionLocal()
        try:
            new_upper_threshold = UpperThreshold(sensor_id=sensor_id, value=0.0)
            new_threshold_sensitivity = ThresholdSensitivity(sensor_id=sensor_id, value=10.0)
            session.add(new_upper_threshold)
            session.add(new_threshold_sensitivity)
            session.commit()
            self.logger.info(f"Sensor {sensor_id} initialized.")
        except Exception as e:
            session.rollback()
        finally:
            session.close()
        
# Example usage:
# db_connector = DatabaseConnector("username", "password", "localhost", 5432, "mydatabase")