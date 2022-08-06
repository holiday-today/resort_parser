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

@app.route("/", methods=["POST"])
def test():
    try:
        f = request.json
    except Exception as e1:
        return 'Bad response json :('
    print('we have json!')
    print(f)
    return main.start(to_main_json(f))


testing = {
    "1": [
        {
            "Name": "Constance Ephelia Resort 5*",
            "Date": "05.09.2022, Пн",
            "Nights": "3",
            "Food": "Half Board",
            "Room": "Junior Suite",
            "Sleeps": "2+1",
            "Price": {
                "resort-holiday": 122847,
                "booking": 159137
            },
            "booking_room_name": " Junior Suite "
        },
        {
            "Name": "Constance Ephelia Resort 5*",
            "Date": "05.09.2022, Пн",
            "Nights": "3",
            "Food": "Full Board",
            "Room": "Junior Suite",
            "Sleeps": "2+1",
            "Price": {
                "resort-holiday": 137217,
                "booking": null
            },
            "booking_room_name": " Junior Suite "
        },
        {
            "Name": "Constance Ephelia Resort 5*",
            "Date": "05.09.2022, Пн",
            "Nights": "3",
            "Food": "Half Board",
            "Room": "Senior Suite",
            "Sleeps": "2+1",
            "Price": {
                "resort-holiday": 143183,
                "booking": 182134
            },
            "booking_room_name": " Senior Suite "
        },
        {
            "Name": "Constance Ephelia Resort 5*",
            "Date": "05.09.2022, Пн",
            "Nights": "3",
            "Food": "Full Board",
            "Room": "Senior Suite",
            "Sleeps": "2+1",
            "Price": {
                "resort-holiday": 157552,
                "booking": null
            },
            "booking_room_name": " Senior Suite "
        },
        {
            "Name": "Constance Ephelia Resort 5*",
            "Date": "05.09.2022, Пн",
            "Nights": "3",
            "Food": "Half Board",
            "Room": "Senior Suite",
            "Sleeps": "3",
            "Price": {
                "resort-holiday": 158451,
                "booking": 191332
            },
            "booking_room_name": " Senior Suite "
        },
        {
            "Name": "Constance Ephelia Resort 5*",
            "Date": "05.09.2022, Пн",
            "Nights": "3",
            "Food": "Full Board",
            "Room": "Senior Suite",
            "Sleeps": "3",
            "Price": {
                "resort-holiday": 179941,
                "booking": null
            },
            "booking_room_name": " Senior Suite "
        },
        {
            "Name": "Constance Ephelia Resort 5*",
            "Date": "05.09.2022, Пн",
            "Nights": "3",
            "Food": "Bed Breakfast",
            "Room": "2 Bedroom Family Villa",
            "Sleeps": "2+1",
            "Price": {
                "resort-holiday": 254996,
                "booking": null
            },
            "booking_room_name": " Three-Bedroom Family Villa with Private Pool "
        },
        {
            "Name": "Constance Ephelia Resort 5*",
            "Date": "05.09.2022, Пн",
            "Nights": "3",
            "Food": "Bed Breakfast",
            "Room": "2 Bedroom Family Villa",
            "Sleeps": "3",
            "Price": {
                "resort-holiday": 254996,
                "booking": null
            },
            "booking_room_name": " Three-Bedroom Family Villa with Private Pool "
        }
    ]
}

@app.route("/result", methods=["POST"])
def result():
    return testing
