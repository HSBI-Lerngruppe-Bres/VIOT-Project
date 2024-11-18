from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from models import db, init_db, Weights, Alarms
from configweb import Config
from control_server import control_server_task
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
    weights = Weights.query.order_by(Weights.timestamp.desc()).all()
    alarms = Alarms.query.order_by(Alarms.timestamp.desc()).all()

    weights_data = [{'sensor_id': w.sensor_id, 'value': w.value, 'timestamp': w.timestamp} for w in weights]
    alarms_data = [{'sensor_id': a.sensor_id, 'value': a.value, 'timestamp': a.timestamp} for a in alarms]

    return {'weights': weights_data, 'alarms': alarms_data}

def control_server_task_context():
    with app.app_context():
        control_server_task()

def main():
    thread = threading.Thread(target=control_server_task_context)
    thread.start()
    
    app.run(host='0.0.0.0', port=5000, debug=True)

if __name__ == '__main__':
    main()
