from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from models import db, init_db, Weights, Alarms, EmailNotification, AlarmStatus
from configweb import Config
from control_server import control_server_task
import paho.mqtt.client as mqtt
import threading

config = Config()

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['DEBUG'] = config.DEBUG

# Initialisiere die Datenbank
init_db(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data')
def data():
    weights = Weights.query.order_by(Weights.timestamp.desc()).limit(10).all()
    alarms = Alarms.query.order_by(Alarms.timestamp.desc()).limit(5).all()

    weights_data = [{'sensor_id': w.sensor_id, 'value': w.value, 'timestamp': w.timestamp} for w in weights]
    alarms_data = [{'sensor_id': a.sensor_id, 'value': a.value, 'timestamp': a.timestamp} for a in alarms]

    return {'weights': weights_data, 'alarms': alarms_data}

@app.route('/add_email', methods=['POST'])
def add_email():
    """
    Fügt eine neue E-Mail-Adresse für Benachrichtigungen hinzu.

    Diese Funktion empfängt eine E-Mail-Adresse über eine POST-Anfrage,
    überprüft, ob die E-Mail-Adresse bereits existiert, und speichert sie
    in der Datenbank, falls sie noch nicht vorhanden ist.

    Returns:
        Response: Eine JSON-Antwort mit einer Erfolgs- oder Fehlermeldung und dem entsprechenden HTTP-Statuscode.
    """
    try:
        email = request.form.get('email')
        print(f"Erhaltene E-Mail: {email}")  # Debugging: Überprüfe die empfangene E-Mail
        sensor_id = 1

        if not email:
            print("Fehler: Keine E-Mail-Adresse übergeben.")  # Debugging
            return jsonify({'message': 'E-Mail-Adresse fehlt.'}), 400

        # Überprüfen, ob die E-Mail-Adresse bereits existiert
        with app.app_context():
            existing_entry = EmailNotification.query.filter_by(sensor_id=sensor_id, email_address=email).first()
            if existing_entry:
                print("Fehler: E-Mail-Adresse existiert bereits.")  # Debugging
                return jsonify({'message': 'E-Mail-Adresse ist bereits registriert.'}), 400

            # Neue E-Mail-Adresse speichern
            new_email = EmailNotification(sensor_id=sensor_id, email_address=email)
            db.session.add(new_email)
            db.session.commit()

        return jsonify({'message': 'E-Mail-Adresse erfolgreich hinzugefügt.'})

    except Exception as e:
        print(f"Interner Serverfehler: {e}")  # Debugging
        return jsonify({'message': f'Interner Serverfehler: {e}'}), 500
    
@app.route('/disarm_alarm', methods=['POST'])
def disarm_alarm():
    """
    Schaltet den Alarm aus.
    
    Diese Funktion empfängt eine POST-Anfrage, um den Alarm auszuschalten.
    Sie sendet eine MQTT-Nachricht an den MQTT-Broker, um den Alarm auszuschalten.
    
    Returns:
        str: Eine Antwort, die anzeigt, dass der Alarm ausgeschaltet wurde.
    """
    try:
        is_active = request.form.get('is_active') == 'true'  # `true` aus der Anfrage konvertieren
        with app.app_context():
            #send mqtt message to disarm alarm
            mqtt_client = mqtt.Client()
            mqtt_client.username_pw_set(config.MQTT_USERNAME, config.MQTT_PASSWORD)
            mqtt_client.connect(config.MQTT_BROKER, config.MQTT_PORT, 60)
            mqtt_client.publish(f"mailbox/{1}/disarm_alarm", "disarm")
            mqtt_client.publish(f"mailbox/{1}/arm_alarm", -9999999)
    except Exception as e:
        print(f"Fehler beim Umschalten des Alarms: {e}")
        return jsonify({'message': f'Fehler: {e}'}), 500
    return "OK"

def control_server_task_context():
    """
    Startet die Funktion `control_server_task` im Anwendungsk
    """
    with app.app_context():
        control_server_task()

def main():
    thread = threading.Thread(target=control_server_task_context)
    thread.start()
    
   
    
    app.run(host='0.0.0.0', port=5001, debug=config.DEBUG)


if __name__ == '__main__':
    main()
