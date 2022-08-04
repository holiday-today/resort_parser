from flask import Flask, json, request
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

@app.route('/')
def index():

    return "<p>Hello, World</p>"