from flask import Flask, request, json
import main
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
            for i in data[el]:
                post_json[el].append(i)
    return post_json

test_item = 0

@app.route("/", methods=["POST"])
def test():
    print(f'test_item: {test_item}')
    test_item += 1
    try:
        f = request.json
    except Exception as e1:
        return 'Bad response json :('
    print('we have json!')
    print(f)
    return main.start(to_main_json(f))
