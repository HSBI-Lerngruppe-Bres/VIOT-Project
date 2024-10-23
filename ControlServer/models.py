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
    Converts specified tables to hypertables using the provided database connection.

    Args:
        connection: A database connection object that allows executing SQL commands.

    The function executes SQL commands to convert the 'weights' and 'alarms' tables
    into hypertables based on the 'timestamp' column.
    """
    with engine.connect() as connection:
        connection.execute(text("SELECT create_hypertable('weights', 'timestamp');"))
        connection.execute(text("SELECT create_hypertable('alarms', 'timestamp');"))
        connection.commit()