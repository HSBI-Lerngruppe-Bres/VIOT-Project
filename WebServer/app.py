from flask import Flask, render_template
from configweb import Config

# Lade die Konfiguration
config = Config()

# Initialisiere die Flask-App
app = Flask(__name__)
app.secret_key = config.SECRET_KEY

# Beispielroute
@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    # Flask-App starten
    app.run(host='0.0.0.0', port=5000, debug=True)
