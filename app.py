from flask import Flask, json, request
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route('/')
def index():
    cok = {
        "query": 123,
        "pageview_id": "f3ae6db9c405036b",
        "aid": 304142,
        "language": "ru",
        "size": 5
    }
    return cok
