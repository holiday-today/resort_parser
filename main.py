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
    'STATEINC': '78',           # Код страны
    'CHECKIN_BEG': '20220905',  # Дата въезда С гггг.мм.дд
    'CHECKIN_END': '20220905',  # Дата въезда ПО гггг.мм.дд
    'NIGHTS_FROM': '3',         # Мин. кол-во ночей
    'NIGHTS_TILL': '3',         # Макс. кол-во ночей
    'ADULT': '2',               # Кол-во взрослых
    'CHILD': '1',               # Кол-во детей
    'AGES': [
        9,
    ],
    'CURRENCY': '1',            # Валюта [1: RUB, 3:EUR]
    'TOWNS': [                  # Города
        
    ],   
    'HOTELS': [                 # Отели
        414,
    ],
    'MEALS': [                  # Питание (аналогично HOTELS)
        
    ],
    'STARS': [                  # Звезды
        
    ],
    'FILTER': '1',              # НЕ ТРОГАТЬ! Дефолт
    'PRICEPAGE': 1,             # Страница
    'DOLOAD': 1                 # НЕ ТРОГАТЬ! Дефолт Загрузчик поиска
}

result_json = {}

bla1 = open('itog.json', 'w', encoding='utf-8')
bla1.close()
bla1 = open('data.json', 'w', encoding='utf-8')
bla1.close()

def main():
    while True:
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
            continue
        try:
            with open('qq.html', 'w', encoding='utf-8') as f:
                f.write(r.text)
            html_tags = soup.select('[class*="price_info"]')
            print('Get list...')
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
            continue
        try:
            ppl = pagelist.copy()
            ppl.append({"ADULT": int(url_keys['ADULT']), "CHILD": int(url_keys['CHILD']), "AGES": url_keys['AGES']})

            print('Start parse Booking.com...')
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
    
            #break # только одна страница
            if soup.select_one('.pager'):
                if soup.select_one('.pager').select('span')[-1].get('class')[0] == 'current_page':
                    break
                else:
                    input('Press any key to continue...')
                    input()
                    print('')
            else:
                break
            url = main_url_rh
            url_keys['PRICEPAGE'] += 1
        except Exception as e:
            print('Something wrong! Try again...')
            print(traceback.print_exc())
            break


if __name__ == '__main__':
    r = requests.post("https://dashboard.heroku.com/apps/holiday-today/get/allresult")
    r = r.json()
    url_keys = {
        'STATEINC': r['STATEINC'],           
        'CHECKIN_BEG': r['CHECKIN_BEG'],  
        'CHECKIN_END': r['CHECKIN_BEG'],  
        'NIGHTS_FROM': r['NIGHTS_FROM'],         
        'NIGHTS_TILL': r['NIGHTS_FROM'],         
        'ADULT': r['ADULT'],               
        'CHILD': r['CHILD'],               
        'AGES': r['AGES'],
        'CURRENCY': '1',            
        'TOWNS': r['TOWNS'],
        'FILTER': '1',              
        'PRICEPAGE': 1,             
        'DOLOAD': 1                 
    }
    main()
