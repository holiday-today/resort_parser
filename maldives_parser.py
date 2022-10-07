import requests
import json
from bs4 import BeautifulSoup
import time
from connector import connect
import traceback
import os

main_url_rh = 'https://online.maldives.ru/search_hotel?'

headers = {
    	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-type': 'text/html; charset=utf-8', 
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.148 YaBrowser/22.7.2.902 Yowser/2.5 Safari/537.36'
}

def main(url_keys, claim):
    url = main_url_rh
    result_json = {}
    for key, value in url_keys.items():
        if isinstance(value, list):
            if len(value) > 0:
                url += key + '=' + str(value[0])
                for i in range(1, len(value)):
                    url += '%2C' + str(value[i])
                url += '&'
        else:
            url += key + '=' + str(value)
            url += '&'
    
    print(f'Getting url: {url}')
    r = ''
    print('Getting response Maldives...')
    
    try:
        r = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, features="html.parser")
    except Exception as e:
        print('Reconnect...')
        return main(url_keys, claim)
    try:
        html_tags = soup.select_one('.control_hotels').select_one('[class*="checklistbox"]').select('label')
        a = [tag.text for tag in html_tags]
        nameMald = connect([claim],a,'Name')

        foodMald = ''
        if claim["Food"] == "Bed Breakfast":
            foodMald = '4'
        elif claim["Food"] == "Half Board":
            foodMald = '5'
        elif claim["Food"] == "Full Board":
            foodMald = '6'
        elif claim["Food"] == "All Inclusive":
            foodMald = '3'
        
        if len(nameMald[0][1]) == 1:
            my_el = nameMald[0][1][0]
            c_id = a.index(my_el)
            hotel_id = html_tags[c_id].select_one('input').get('value')
        else:
            return f"Не удалось найти отель {claim['Name']}", 403

        url += f'HOTELS={hotel_id}&MEALS={foodMald}'
        print(url)
        r = requests.get(url, headers=headers, verify=False)
        soup = BeautifulSoup(r.text, features="html.parser")

        if len(str(soup.select_one('.resultset'))) < 100:
            return "Нет данных!", 402

        print('Get list...')   
        table_elements = soup.select_one('.resultset').select_one('table').select_one('tbody').select('[class*="price_info"]')
        pagelist = []
        rm_lst = []

        for i in table_elements:
            #if i.select_one('.btn-group') or i.select_one('[class*="from_the_best"]'):
            #    continue
            h = {}

            h['Tour'] = i.select_one('.tour').select_one('a').text
            
            room_text = i.select('td:not([class])')[2].text.replace('\n', '').split(' / ')
            h['Room'] = room_text[0]
            rm_lst.append(room_text[0])
            
            tmp_p = i.select_one('.td_price').text
            while not tmp_p[0].isdigit():
                tmp_p = tmp_p[1:]
            h['Price'] = int(tmp_p.split(' ')[0])

            h['Price_check_url'] = f'https://online.maldives.ru/bron_person?CATCLAIM={i.get("data-cat-claim")}'

            pagelist.append(h)
    except:
        print('Broken values! Try load page again...')
        print(traceback.print_exc())
        return {'error': 'Broken values! Try load page again...'}

    room_name = connect([claim], rm_lst, 'Room')
    if len(set(room_name[0][1])) == 1:
        itog_room = []
        my_el = room_name[0][1][0]
        for cc in range(len(rm_lst)):
            if rm_lst[cc] == my_el:
                itog_room.append({'Transfer': pagelist[cc]['Tour'], 'Price_Maldives': pagelist[cc]['Price'], 'Price_check_maldives': pagelist[cc]['Price_check_url']})
    else:
        return f"Не удалось найти комнату {claim['Room']}", 402
    return {'data': itog_room}, 200


def start(server_data, id_claim, file_id):
    print('Get json:')
    print(server_data)

    my_load = {}
    with open(f'{file_id}.json') as f:
        my_load = json.load(f)

    mft = {}
    for i in my_load['1'][:-1]:
        if i["id_claim"] == f'{id_claim}':
            mft = i
            break

    if mft == {}:
        return "Несуществующий id_claim", 404

    return main(server_data, mft)


if __name__ == '__main__':
    w = {
        "STATEINC": "50",
        "CHECKIN_BEG": "20221020",
        "NIGHTS_FROM": "7",
        "ADULT": "2",
        "CHILD": "0",
        "AGES": [
            "0"
        ],
        "TOWNS": [],
        "CURRENCY": "1",
        "STARS": [],
        "PRICEPAGE": 1,
        "HOTELS": [],
        "MEALS": [],
        "DOLOAD": 1
    }
    print(start(w, "0x430A0000000202000000010000003200000003000000006CE70ADFAF34000000006AB707000003D8000000F0000000040000000400000000000000000000000100000000AF3B000007000000000075F3500000000202020000636363AF340000AF3B0000020000000003000000000000000000000000000000000000000000000000", "file1664820590.991211"))
