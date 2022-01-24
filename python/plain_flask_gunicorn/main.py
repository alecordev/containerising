import flask
from flask import jsonify

app = flask.Flask(__name__)


@app.route("/")
def index():
    response = {
        "key": "value",
    }
    return jsonify(response)
