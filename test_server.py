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
        print(f['HOTELS'])
        return main.start(f)


api.add_resource(Main, "/get/allresult")
api.init_app(app)

if __name__ == "__main__":
    app.run(debug=True, port=3000, host="127.0.0.1")
