from flask import Flask, request, json
import main
import logging
from flask_cors import CORS
import parse_resort_states
import async_booking
import os

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

CORS(app)

def to_main_json(data):
    post_json = {
        'STATEINC': None,           
        'CHECKIN_BEG': None,  
        'CHECKIN_END': None,  
        'NIGHTS_FROM': None,         
        'NIGHTS_TILL': None,         
        'ADULT': None,               
        'CHILD': None,               
        'AGES': [],
        'CURRENCY': '1',            
        'TOWNS': [],
        'HOTELS': [],
        'MEALS': [],
        'STARS': [],
        'FILTER': '1',              
        'PRICEPAGE': '1',             
        'DOLOAD': 1                 
    }
    for el in data:
        if post_json[el] == None or post_json[el] == '1':
            post_json[el] = data[el]
        elif post_json[el] == []:
            for i in data[el]:
                post_json[el].append(i)
    return post_json

@app.route("/", methods=["POST"])
def get_full_response():
    os.remove("data.json")
    try:
        f = request.json
    except Exception as e1:
        return 'Bad response json :('
    print('we have json!')
    print(f)
    result = main.start(to_main_json(f))
    return result

@app.route("/state", methods=["GET"])
def get_states():
    return parse_resort_states.start()

@app.route("/city/<int:state_id>", methods=["GET"])
def get_cities(state_id):
    return parse_resort_states.start(state_id)

@app.route("/getfiles", methods=["GET"])
def test():
    if os.path.isfile("data.json"):
        with open('data.json', encoding='utf-8') as f:
            bookHotels = json.load(f)
        return bookHotels
    else:
        return 'File not ready yet! Please wait a 30 seconds more...', 423
