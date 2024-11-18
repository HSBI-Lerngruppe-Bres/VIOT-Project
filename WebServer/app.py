from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_socketio import SocketIO
from models import db, init_db, Weights, Alarms
from configweb import config

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisiere SocketIO
socketio = SocketIO(app)

# Initialisiere die Datenbank
init_db(app)


@app.route('/')
def index():
    # Gewichtsdaten aus der Datenbank abrufen
    weights = Weights.query.order_by(Weights.timestamp.desc()).all()
    # Alarmdaten aus der Datenbank abrufen
    alarms = Alarms.query.order_by(Alarms.timestamp.desc()).all()

    print("Gewichtsdaten:", weights)
    print("Alarmdaten:", alarms)

    return render_template('index.html', weights=weights, alarms=alarms)



# Funktion zum Senden von MQTT-Nachrichten an die Clients
def send_weight_update(sensor_id, value, timestamp):
    socketio.emit('new_weight', {'sensor_id': sensor_id, 'value': value, 'timestamp': str(timestamp)})

def send_alarm_update(sensor_id, value, timestamp):
    socketio.emit('new_alarm', {'sensor_id': sensor_id, 'value': value, 'timestamp': str(timestamp)})


if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
