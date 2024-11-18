from flask import Flask, request, jsonify
from models import db, init_db, Weights, Alarms, UpperThreshold, LowerThreshold
from configweb import Config
from datetime import datetime


# Lade die Konfiguration
config = Config()

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Initialisiere die Datenbank
with app.app_context():
    init_db(app)

# Route für die Startseite
@app.route('/')
def home():
    return "Smart Mailbox Dashboard"


# Route zum Einfügen von Gewichtsdaten
@app.route('/add-weight', methods=['POST'])
def add_weight():
    data = request.json
    new_weight = Weights(
        timestamp=datetime.utcnow(),
        sensor_id=data['sensor_id'],
        value=data['value']
    )
    db.session.add(new_weight)
    db.session.commit()
    return jsonify({"message": "Weight data added successfully"}), 201

# Route zum Abrufen von Gewichtsdaten
@app.route('/get-weights', methods=['GET'])
def get_weights():
    weights = Weights.query.all()
    return jsonify([{"timestamp": w.timestamp, "sensor_id": w.sensor_id, "value": w.value} for w in weights])

# Route zum Einfügen von Alarmen
@app.route('/add-alarm', methods=['POST'])
def add_alarm():
    data = request.json
    new_alarm = Alarms(
        timestamp=datetime.utcnow(),
        sensor_id=data['sensor_id'],
        value=data['value']
    )
    db.session.add(new_alarm)
    db.session.commit()
    return jsonify({"message": "Alarm added successfully"}), 201

# Route zum Abrufen von Alarmen
@app.route('/get-alarms', methods=['GET'])
def get_alarms():
    alarms = Alarms.query.all()
    return jsonify([{"timestamp": a.timestamp, "sensor_id": a.sensor_id, "value": a.value} for a in alarms])

if __name__ == '__main__':
    app.run(debug=True)