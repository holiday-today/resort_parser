from flask import Flask, request, json
import main
import logging
from flask_cors import CORS
import parse_resort_states
import async_booking
import os, glob
import maldives_parser

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
        'COSTMIN': None,
        'COSTMAX': None,  
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


@app.before_first_request
def flcl():
    for filename in glob.glob("*.json"):
        os.remove(filename)


@app.route("/", methods=["POST"])
def get_full_response():
    try:
        f = request.json
    except Exception as e1:
        return 'Bad response json :('
    print('we have json!')
    print(f)
    file_id = f['id']
    f.pop('id')
    endres = main.start(to_main_json(f), file_id)
    if 'error' in endres:
        return "Нет данных", 406
    else:
        return "File ready!", 200
        #return endres


@app.route("/state", methods=["GET"])
def get_states():
    return parse_resort_states.start()


@app.route("/city/<int:state_id>", methods=["GET"])
def get_cities(state_id):
    return parse_resort_states.start(state_id)


@app.route("/getfiles/<string:file_id>", methods=["GET"])
def get_file(file_id):
    lll = {}
    if os.path.isfile(f'{file_id}.json'):
        with open(f'{file_id}.json', encoding='utf-8') as f:
            lll = json.load(f)
        return lll
    else:
        return 'File not ready yet! Please wait a 30 seconds more...', 423


@app.route("/getfiles/count", methods=["GET"])
def cnt_files():
    return str(len(glob.glob("*.json")))


@app.route("/maldives/<string:id_claim>", methods=["GET"])
def get_mald(id_claim):
    try:
        f = request.json
    except Exception as e1:
        return 'Bad response json :('
    new_f = {
        'STATEINC': f['STATEINC'],
        'CHECKIN_BEG': f['CHECKIN_BEG'],
        'CHECKIN_END': f['CHECKIN_BEG'],
        'NIGHTS_FROM': f['NIGHTS_FROM'],
        'NIGHTS_TILL': f['NIGHTS_FROM'],
        'ADULT': f['ADULT'],
        'CHILD': f['CHILD'],
        'AGES': f['AGES'],
        'CURRENCY': f['CURRENCY'],
        'FILTER': '1',
        'PRICEPAGE': '1',
        'DOLOAD': 1
    }
    return maldives_parser.start(new_f, id_claim, f['id'])
