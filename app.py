from flask import Flask, request, json
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

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
        'PRICEPAGE': 1,             
        'DOLOAD': 1                 
    }
    for el in data:
        if post_json[el] is None:
            post_json[el] = data[el]
        else:
            post_json[el].append(data[el])
    return post_json

@app.route("/", methods=["POST"])
def test():
    try:
        f = request.json
    except Exception as e1:
        return 'Bad response json'
    return to_main_json(f)
