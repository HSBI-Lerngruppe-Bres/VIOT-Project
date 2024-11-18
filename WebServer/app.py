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

@app.route('/')
def home():
    return "Smart Mailbox Dashboard"

if __name__ == '__main__':
    app.run(debug=True)
