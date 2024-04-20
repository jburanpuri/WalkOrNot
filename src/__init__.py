from flask import Flask
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

load_dotenv()


def create_app():
    app = Flask(__name__)
    app.config["MONGO_URI"] = os.getenv(
        "MONGO_URI")

    mongo = PyMongo(app)

    from .views import main
    app.register_blueprint(main)

    return app
