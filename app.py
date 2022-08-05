from flask import Flask, request, json
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route("/", methods=["POST"])
def test():
    try:
        f = request.json
        print('First method!')
    except Exception as e1:
        try:
            f = request.get_json(force=True)
            print('Second method!')
        except Exception as e2:
            try:
                f = request.get_json(force=True)
                print('Third method!')
            except Exception as e3:
                return 'Failed!'
    return f
