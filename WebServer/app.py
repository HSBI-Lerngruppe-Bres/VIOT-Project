from flask import Flask, render_template
from models import db, init_db, Weights, Alarms
from configweb import config

app = Flask(__name__)
app.config['SECRET_KEY'] = config.SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = config.DB_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialisiere die Datenbank
init_db(app)

@app.route('/')
def index():
    weights = Weights.query.all()
    alarms = Alarms.query.all()
    return render_template('index.html', weights=weights, alarms=alarms)

if __name__ == '__main__':
    app.run(debug=True)
