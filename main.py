import requests
import json
from bs4 import BeautifulSoup
import time
from booking_parser import ParseBooking
from connector import connect
import traceback
from fake_useragent import UserAgent

main_url_rh = 'https://search.resort-holiday.com/search_hotel?'

headers = {
    	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-type': 'text/html; charset=utf-8', 
        'user-agent': UserAgent().random
}

# пример
url_keys = {
}

result_json = {}

bla1 = open('itog.json', 'w', encoding='utf-8')
bla1.close()
bla1 = open('data.json', 'w', encoding='utf-8')
bla1.close()

def main():
    global url_keys
    url = main_url_rh
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
    
    r = ''
    print('Getting response Resort-Holiday...')
    
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, features="html.parser")
    except Exception as e:
        print('Reconnect...')
        return main()
    try:
        print('Get list...')   
        html_tags = soup.select('[class*="price_info"]')
        pagelist = []
        
        for i in html_tags:
            if i.select_one('.btn-group'):
                continue
            
            h = {}
            h['Name'] = i.select_one('.link-hotel').select_one('a').text.replace('\n', '')
            h['Date'] = i.select_one('.sortie').text.replace('\n', '')
            h['Nights'] = i.select_one('.c').text.replace('\n', '')
            h['Food'] = i.select('td:not([class])')[1].text.replace('\n', '')
            
            room_text = i.select('td:not([class])')[2].text.replace('\n', '').split(' / ')
            h['Room'] = room_text[0]
            h['Sleeps'] = room_text[1].split('(')[0].split(' ')[0]
            
            h['Price'] = {}
            h['Price']['resort-holiday'] = int(i.select_one('.td_price').text.replace('\n', '').split(' ')[0])
            
            pagelist.append(h)
    except:
        print('Broken values! Try load page again...')
        print(traceback.print_exc())
        return main()
    try:
        print('Start parse Booking.com...')

        ppl = pagelist.copy()
        ppl.append({"ADULT": int(url_keys['ADULT']), "CHILD": int(url_keys['CHILD']), "AGES": url_keys['AGES']})
        
        bookHotels = ParseBooking(ppl)

        bk = [k for k in bookHotels]
        hotel_table = connect(pagelist, bk, 'Name')
        itog_page = []
        
        for c in hotel_table:
            bk_rooms = [k for k in bookHotels[c[1][0]]]
            new_list = connect([c[0]], bk_rooms, 'Room')
            obj_resort = new_list[0][0]
            if new_list[0][1] != []:
                obj_booking = bookHotels[c[1][0]][new_list[0][1][0]]['Types']
                obj_book_price = [x['Price'] for x in obj_booking if x['Sleeps'] == obj_resort['Sleeps']]
                for obj_pr in obj_book_price:
                    if obj_resort['Food'] in obj_pr:
                        obj_resort['Price']['booking'] = obj_pr[obj_resort['Food']]
                if not 'booking' in obj_resort['Price']:
                    for obj_pr in obj_book_price:
                        if '|'+obj_resort['Food'] in obj_pr:
                            obj_resort['Price']['booking'] = obj_pr['|'+obj_resort['Food']]
                    if not 'booking' in obj_resort['Price']:
                        obj_resort['Price']['booking'] = None
                obj_resort['booking_room_name'] = new_list[0][1][0]
            else:
                obj_resort['Price']['booking'] = None
            itog_page.append(obj_resort)
            #print('################################')
            
        result_json[url_keys['PRICEPAGE']] = itog_page
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(result_json, f, ensure_ascii=False, indent=4)

        print('\n##################\nPage', (url_keys['PRICEPAGE']), 'is loaded!\n##################\n')

        if soup.select_one('.pager'):
            if soup.select_one('.pager').select('span')[-1].get('class')[0] == 'current_page':
                print('Last page loaded!')
            else:
                print(f'{url_keys["PRICEPAGE"]} pages loaded!')
                url_keys['PRICEPAGE'] += 1
        return result_json
    except Exception as e:
        print('Something wrong! Try again...')
        print(traceback.print_exc())


def start(server_data):
    global url_keys
    url_keys = {
        'STATEINC': server_data['STATEINC'],           
        'CHECKIN_BEG': server_data['CHECKIN_BEG'],  
        'CHECKIN_END': server_data['CHECKIN_BEG'],  
        'NIGHTS_FROM': server_data['NIGHTS_FROM'],         
        'NIGHTS_TILL': server_data['NIGHTS_FROM'],         
        'ADULT': server_data['ADULT'],               
        'CHILD': server_data['CHILD'],               
        'AGES': server_data['AGES'],
        'CURRENCY': '1',            
        'TOWNS': server_data['TOWNS'],
        'HOTELS': server_data['HOTELS'],
        'MEALS': server_data['MEALS'],
        'STARS': server_data['STARS'],
        'FILTER': '1',              
        'PRICEPAGE': 1,             
        'DOLOAD': 1                 
    }
    print(url_keys)
    return main()