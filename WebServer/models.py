from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Tabelle für Gewichtsdaten
class Weights(db.Model):
    __tablename__ = 'weights'
    timestamp = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow)
    sensor_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Weights timestamp={self.timestamp}, sensor_id={self.sensor_id}, value={self.value}>"

# Tabelle für Alarme
class Alarms(db.Model):
    __tablename__ = 'alarms'
    timestamp = db.Column(db.DateTime, primary_key=True, default=datetime.utcnow)
    sensor_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<Alarms timestamp={self.timestamp}, sensor_id={self.sensor_id}, value={self.value}>"

# Tabelle für obere Schwellenwerte
class UpperThreshold(db.Model):
    __tablename__ = 'upper_threshold'
    sensor_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<UpperThreshold sensor_id={self.sensor_id}, value={self.value}>"

# Tabelle für untere Schwellenwerte
class LowerThreshold(db.Model):
    __tablename__ = 'lower_threshold'
    sensor_id = db.Column(db.Integer, primary_key=True)
    value = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f"<LowerThreshold sensor_id={self.sensor_id}, value={self.value}>"

# Funktion zur Initialisierung der Datenbank
def init_db(app):
    with app.app_context():
        db.create_all()
        print("Datenbanktabellen wurden erfolgreich erstellt.")
