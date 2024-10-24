from sqlalchemy import Column, Integer, String, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Weights(Base):
    __tablename__ = 'weights'
    timestamp = Column(DateTime, primary_key=True)
    sensor_id = Column(Integer, primary_key=True)
    value = Column(Float)

class Alarms(Base):
    __tablename__ = 'alarms'
    timestamp = Column(DateTime, primary_key=True)
    sensor_id = Column(Integer, primary_key=True)
    value = Column(Float)

class UpperThreshold(Base):
    __tablename__ = 'upper_threshold'
    sensor_id = Column(Integer, primary_key=True)
    value = Column(Float)

class LowerThreshold(Base):
    __tablename__ = 'lower_threshold'
    sensor_id = Column(Integer, primary_key=True)
    value = Column(Float)

class EmailNotification(Base):
    __tablename__ = 'email_notification'
    sensor_id = Column(Integer, primary_key=True)
    email_address = Column(String, primary_key=True)

class ThresholdSensitivity(Base):
    __tablename__ = 'threshold_sensetivety'
    sensor_id = Column(Integer, primary_key=True)
    value = Column(Float)

def setup_hypertables(engine):
    """
    Converts specified tables to hypertables using the provided database engine.

    Args:
        engine: A SQLAlchemy engine object that allows connecting to the database.

    Raises:
        Exception: If there is an error during the execution of the SQL commands.

    The function executes SQL commands to convert the 'weights' and 'alarms' tables
    into hypertables based on the 'timestamp' column.
    """
    with engine.connect() as connection:
        try:
            connection.execute(text("SELECT create_hypertable('weights', 'timestamp');"))
            connection.execute(text("SELECT create_hypertable('alarms', 'timestamp');"))
            connection.commit()
        except Exception as e:
            connection.rollback()
            raise e