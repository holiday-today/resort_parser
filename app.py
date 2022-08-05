from flask import Flask, request, json
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route("/", methods=["POST"])
def test():
    try:
        f = request.form
    except Exception as e1:
        try:
            f = request.get_json(force=True)
        except Exception as e2:
            return 'Failed 2'
    return f
