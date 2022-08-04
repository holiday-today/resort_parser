from flask import Flask
from flask_restful import Api, Resource, reqparse
import main

app = Flask(__name__)
api = Api()

parser = reqparse.RequestParser()
parser.add_argument('STATEINC', type=str, location='form')
parser.add_argument('CHECKIN_BEG', type=str, location='form')
parser.add_argument('NIGHTS_FROM', type=str, location='form')
parser.add_argument('ADULT', type=str, location='form')
parser.add_argument('CHILD', type=str, location='form')
parser.add_argument('AGES', action='append', location='form')
parser.add_argument('TOWNS', action='append', location='form')
parser.add_argument('HOTELS', action='append', location='form')
parser.add_argument('MEALS', action='append', location='form')
parser.add_argument('STARS', action='append', location='form')


class Main(Resource):
    def get(self):
        return main.main()

    def post(self):
        f = parser.parse_args()
        post_json = {
            'STATEINC': f['STATEINC'],           
            'CHECKIN_BEG': f['CHECKIN_BEG'],  
            'CHECKIN_END': f['CHECKIN_BEG'],  
            'NIGHTS_FROM': f['NIGHTS_FROM'],         
            'NIGHTS_TILL': f['NIGHTS_FROM'],         
            'ADULT': f['ADULT'],               
            'CHILD': f['CHILD'],               
            'AGES': f['AGES'],
            'CURRENCY': '1',            
            'TOWNS': f['TOWNS'],
            'HOTELS': f['HOTELS'],
            'MEALS': f['MEALS'],
            'STARS': f['STARS'],
            'FILTER': '1',              
            'PRICEPAGE': 1,             
            'DOLOAD': 1                 
        }
        return main.start(post_json)


api.add_resource(Main, "/get/allresult")
api.init_app(app)

if __name__ == "__main__":
    print('Server started!')
    app.run(debug=True)
