#!/usr/bin/env python3
import os
from flask import Flask, request, render_template_string
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

uri = os.getenv("MONGO_URI")
client = MongoClient(uri, server_api=ServerApi('1'))

try:
    client.admin.command('ping')
    print("Pinged your deployment. You successfully connected to MongoDB!")
except Exception as e:
    print(f"Failed to connect to MongoDB: {e}")

db = client['history']


@app.route("/", methods=["GET", "POST"])
def main():
    if request.method == "POST":
        user_input = request.form.get("user_input", "")
        if user_input:
            db.inputs.insert_one({"input": user_input})

    inputs = db.inputs.find().sort("_id", -1)
    history = [input['input'] for input in inputs]

    return render_template_string('''
        <h1>Input Form</h1>
        <form action="/" method="POST">
            <input name="user_input" type="text">
            <input type="submit" value="Submit!">
        </form>
        <h2>History</h2>
        <ul>
        {% for input in history %}
            <li>{{ input }}</li>
        {% endfor %}
        </ul>
    ''', history=history)


if __name__ == '__main__':
    app.run(debug=True)
