from datetime import datetime, timezone
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Weights(db.Model):
    __tablename__ = 'weights'
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, nullable=False)
    value = db.Column(db.Float, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

class Alarms(db.Model):
    __tablename__ = 'alarms'
    id = db.Column(db.Integer, primary_key=True)
    sensor_id = db.Column(db.Integer, nullable=False)
    value = db.Column(db.String(50), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.now(timezone.utc), nullable=False)

class UpperThreshold(db.Model):
    __tablename__ = 'upper_threshold'
    sensor_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

class LowerThreshold(db.Model):
    __tablename__ = 'lower_threshold'
    sensor_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

def init_db(app):
    with app.app_context():
        db.create_all()
        print("Datenbanktabellen wurden erfolgreich erstellt.")
