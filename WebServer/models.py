from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Weights(db.Model):
    __tablename__ = 'weights'
    timestamp = db.Column(db.DateTime, primary_key=True, default=datetime.now)
    sensor_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

class Alarms(db.Model):
    __tablename__ = 'alarms'
    timestamp = db.Column(db.DateTime, primary_key=True, default=datetime.now)
    sensor_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.String(50), nullable=False)

class UpperThreshold(db.Model):
    __tablename__ = 'upper_threshold'
    sensor_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

class LowerThreshold(db.Model):
    __tablename__ = 'lower_threshold'
    sensor_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)
    
class EmailNotification(db.Model):
    __tablename__ = 'email_notification'
    sensor_id = db.Column(db.Integer, primary_key=True)
    email_address = db.Column(db.String, primary_key=True)

class ThresholdSensitivity(db.Model):
    __tablename__ = 'threshold_sensetivety'
    sensor_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float)

class AlarmStatus(db.Model):
    __tablename__ = 'alarm_status'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)


def init_db(app):
    """
    Initialize the database with the given Flask application context.
    This function sets up the database by initializing the app with the database,
    creating all database tables, and setting up hypertables.
    Args:
        app (Flask): The Flask application instance.
    Returns:
        None
    """
    with app.app_context():
        db.init_app(app)
        db.create_all()
        setup_hypertables(db.engine)
        print("Datenbanktabellen wurden erfolgreich erstellt.")

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
            connection.execute(db.text("SELECT create_hypertable('weights', 'timestamp');"))
            connection.execute(db.text("SELECT create_hypertable('alarms', 'timestamp');"))
            connection.commit()
        except Exception as e:
            connection.rollback()