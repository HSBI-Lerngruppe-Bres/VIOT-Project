from sqlalchemy import Column, Integer, String, Float, DateTime, text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Weight(Base):
    __tablename__ = 'weights'
    timestamp = Column(DateTime, primary_key=True, default=datetime.now())
    sensor_id = Column(Integer, primary_key=True)
    value = Column(Float, default=0.0)

class Alarm(Base):
    __tablename__ = 'alarms'
    timestamp = Column(DateTime, primary_key=True, default=datetime.now())
    sensor_id = Column(Integer, primary_key=True)
    value = Column(Float, default=0.0)

class UpperThreshold(Base):
    __tablename__ = 'upper_threshold'
    sensor_id = Column(Integer, primary_key=True)
    value = Column(Float, default=5.0)

class LowerThreshold(Base):
    __tablename__ = 'lower_threshold'
    sensor_id = Column(Integer, primary_key=True)
    value = Column(Float, default=0.0)

class EmailNotification(Base):
    __tablename__ = 'email_notification'
    sensor_id = Column(Integer, primary_key=True)
    email_address = Column(String, primary_key=True)

class ThresholdSensitivity(Base):
    __tablename__ = 'threshold_sensetivety'
    sensor_id = Column(Integer, primary_key=True)
    value = Column(Float, default=5.0)

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