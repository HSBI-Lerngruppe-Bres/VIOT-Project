from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Weights(db.Model):
    __tablename__ = 'weights'
    timestamp = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow)
    sensor_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

class Alarms(db.Model):
    __tablename__ = 'alarms'
    timestamp = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow)
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

def init_db(app):
    with app.app_context():
        db.init_app(app)
        db.create_all()
        print("Datenbanktabellen wurden erfolgreich erstellt.")
