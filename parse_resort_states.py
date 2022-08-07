import requests
from bs4 import BeautifulSoup

main_url_rh = 'https://search.resort-holiday.com/search_hotel?'

headers = {
    	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-type': 'text/html; charset=utf-8', 
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.148 YaBrowser/22.7.2.902 Yowser/2.5 Safari/537.36'
}

result = {}


def start(server_data = "states"):
    if server_data == "states":
        try:
            r = requests.get(main_url_rh, headers=headers)
            soup = BeautifulSoup(r.text, features="html.parser")
        except Exception as e:
            print('Bad connection to Resort-Holiday :(')
            return None
        states_info = soup.select_one('.direction_right').select_one('.STATEINC').select('option')
        for i in states_info:
            result[i.text] = i.get('value')
    else:
        try:
            r = requests.get(main_url_rh+'STATEINC='+str(server_data), headers=headers)
            soup = BeautifulSoup(r.text, features="html.parser")
        except Exception as e:
            print('Bad connection to Resort-Holiday :(')
            return None
        cities_info = soup.select_one('.control_townto').select('.groupbox')
        for i in cities_info:
            city_list = i.select('label')[1:]
            for x in city_list:
                result[x.text.replace('\n', '')] = x.select_one('input').get('value')
    return result