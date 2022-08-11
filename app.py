from flask import Flask, request, json
import main
import logging
from flask_cors import CORS
import parse_resort_states
import async_booking

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
    try:
        f = request.json
    except Exception as e1:
        return 'Bad response json :('
    print('we have json!')
    print(f)
    return main.start(to_main_json(f))

@app.route("/state", methods=["GET"])
def get_states():
    return parse_resort_states.start()

@app.route("/city/<int:state_id>", methods=["GET"])
def get_cities(state_id):
    return parse_resort_states.start(state_id)

@app.route("/test", methods=["POST"])
def test():
    if __name__ == '__main__':
        async_booking.qq()
    return "1"
