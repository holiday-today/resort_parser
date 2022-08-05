from flask import Flask, jsonify, request
from flask_restful import Api, Resource
import main
import json

app = Flask(__name__)
api = Api()

def to_json(data):
    data = str(data).split("'")[1].split('&')
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
        k, v = el.split('=')[0], el.split('=')[1]
        if post_json[k] is None:
            post_json[k] = v
        else:
            post_json[k].append(v)
    return post_json


class Main(Resource):
    def get(self):
        return main.main()

    def post(self):
        if (request.headers.get('Content-Type') == 'application/json'):
            myjson = request.data
            return main.start(to_json(myjson))
        else:
            return 'Content-Type not supported!'


api.add_resource(Main, "/get/allresult")
api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True)
