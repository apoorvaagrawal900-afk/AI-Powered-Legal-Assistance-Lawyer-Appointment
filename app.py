from flask import Flask
from models import db, User
from config import Config

app=Flask(__name__)
app.config.from_object(Config)

db.init_app(app)

with app.app_context():
    db.create_all()

    
@app.route('/')
def home():
    return "Welcome to AI-Powered Legal Assistance and Lawer Appointment"

if __name__=="__main__":
    app.run(debug=True)
    
