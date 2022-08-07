from flask import Flask, request, json
import main
import logging
from flask_cors import CORS

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

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
def test():
    try:
        f = request.json
    except Exception as e1:
        return 'Bad response json :('
    print('we have json!')
    print(f)
    return main.start(to_main_json(f))
