import requests
import json
from bs4 import BeautifulSoup
import time
#from booking_parser import ParseBooking
from async_booking import ParseBooking
from connector import connect
import traceback
import os

main_url_rh = 'https://search.resort-holiday.com/search_hotel?'

headers = {
    	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Content-type': 'text/html; charset=utf-8', 
        'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.148 YaBrowser/22.7.2.902 Yowser/2.5 Safari/537.36'
}

def main(url_keys):
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
    print('Getting response Resort-Holiday...')
    
    try:
        r = requests.get(url, headers=headers)
        soup = BeautifulSoup(r.text, features="html.parser")
    except Exception as e:
        print('Reconnect...')
        return main()
    try:
        print('Get list...')   
        html_tags = soup.select_one('.resultset').select_one('table').select_one('tbody').select('[class*="price_info"]')
        pagelist = []
        
        for i in html_tags:
            if i.select_one('.btn-group') or i.select_one('[class*="from_the_best"]'):
                continue

            h = {}
            h['Name'] = i.select_one('.link-hotel').text.replace('\n', '')[2:]
            tmp_h = ''
            if '*' in h['Name']:
                tmp_h += h['Name'][h['Name'].index('*')-1:]
                h['Name'] = h['Name'][:h['Name'].index('*')-1]
            elif 'Guest House' in h['Name']:
                tmp_h += h['Name'][h['Name'].index('Guest House'):]
                h['Name'] = h['Name'][:h['Name'].index('Guest House')]
            if '(' in h['Name']:
                tmp_h += h['Name'][h['Name'].index('('):]
                h['Name'] = h['Name'][:h['Name'].index('(')]
            while not h['Name'][0].isalpha():
                h['Name'] = h['Name'][1:]
            while not h['Name'][-1].isalpha():
                h['Name'] = h['Name'][:-1]
            h['tmp'] = tmp_h

            h['Food'] = i.select('td:not([class])')[1].text.replace('\n', '')

            if 'Bed Breakfast' in h['Food']:
                h['Food'] = 'Bed Breakfast'
            elif 'Half Board' in h['Food']:
                h['Food'] = 'Half Board'
            elif 'Full Board' in h['Food']:
                h['Food'] = 'Full Board'
            elif 'All Inclusive' in h['Food']:
                h['Food'] = 'All Inclusive'
            
            room_text = i.select('td:not([class])')[2].text.replace('\n', '').split(' / ')
            h['Room'] = room_text[0]
            
            tmp_p = i.select_one('.td_price').text
            while not tmp_p[0].isdigit():
                tmp_p = tmp_p[1:]
            h['Price_resort'] = int(tmp_p.split(' ')[0])

            h['Price_check_resort'] = f'https://search.resort-holiday.com/bron_person?CATCLAIM={i.get("data-cat-claim")}&TOWNFROMINC=1&STATEINC={url_keys["STATEINC"]}&PACKET=2&GUEST=1'
            h['id_claim'] = i.get('data-cat-claim')

            pagelist.append(h)
    except:
        print('Broken values! Try load page again...')
        print(traceback.print_exc())
        return {'error': 'Broken values! Try load page again...'}
    try:
        print('Start parse Booking.com...')

        cur = ''
        if url_keys['CURRENCY'] == '1':
            cur = 'RUB'
        elif url_keys['CURRENCY'] == '3':
            cur = 'EUR'

        ppl = pagelist.copy()
        ppl.append({"ADULT": int(url_keys['ADULT']), "CHILD": int(url_keys['CHILD']), "AGES": url_keys['AGES'], 'CUR':cur, 'NIGHTS': url_keys['NIGHTS_FROM'], 'DATE': url_keys['CHECKIN_BEG']})

        bookHotels = ParseBooking(ppl)
        #with open('itog.json', encoding='utf-8') as f:
        #    bookHotels = json.load(f)

        resSleeps = str(int(url_keys['ADULT']) + int(url_keys['CHILD']))

        itog_page = []
        
        bk = [k for k in bookHotels]

        #if len(bk) != 0:
        #    

        if len(bk) != 0:
            hotel_table = connect(pagelist, bk, 'Name')
            for c in hotel_table:
                if not c[1][0] in bookHotels:
                    obj_resort = c[0]
                    obj_resort['Price_booking'] = None
                else:
                    bk_rooms = [k for k in bookHotels[c[1][0]] if k != 'url']
                    new_list = connect([c[0]], bk_rooms, 'Room')
                    obj_resort = new_list[0][0]
                    if len(new_list[0][1]) > 1:
                        zzz = new_list[0][1]
                        tmp_hotel = 0
                        for z in range(len(zzz)):
                            hs = False
                            for bzt in bookHotels[c[1][0]][zzz[tmp_hotel]]['Types']:
                                if bzt['Sleeps'] == resSleeps:
                                    hs = True
                                    break
                            if not hs:
                                new_list[0][1].pop(tmp_hotel)
                                tmp_hotel -= 1
                            tmp_hotel += 1
                        if len(new_list[0][1]) > 1:
                            new_list[0][1] = []
                    if new_list[0][1] != []:
                        obj_booking = bookHotels[c[1][0]][new_list[0][1][0]]['Types']
                        obj_book_price = [[x['Price']] for x in obj_booking if x['Sleeps'] == resSleeps]
                        for obj_pr in obj_book_price:
                            if obj_resort['Food'] in obj_pr[0]:
                                obj_resort['Price_booking'] = obj_pr[0][obj_resort['Food']]
                        if not 'Price_booking' in obj_resort:
                            for obj_pr in obj_book_price:
                                if '|'+obj_resort['Food'] in obj_pr[0]:
                                    obj_resort['Price_booking'] = obj_pr[0]['|'+obj_resort['Food']]
                            if not 'Price_booking' in obj_resort:
                                obj_resort['Price_booking'] = None
                        obj_resort['booking_room_name'] = new_list[0][1][0]
                    else:
                        obj_resort['Price_booking'] = None
                    if obj_resort['Name'] == c[1][0] and 'url' in bookHotels[c[1][0]]:
                        obj_resort['url_booking'] = bookHotels[c[1][0]]['url']
                obj_resort['Name'] = obj_resort['Name']+' '+obj_resort['tmp']
                obj_resort.pop('tmp')
                itog_page.append(obj_resort)
        else:
            itog_page = pagelist
                #print('################################')Price

        ipk = 0
        for k in itog_page:
            ipk += 1

            if k["Price_booking"] == None:
                continue

            new_k = k.copy()

            ns = k["Price_booking"].split(', ')
            np = ns[0].split(' (')

            new_k["Price_booking"] = int(np[0])
            new_k["Price_Type"] = np[1][:-1]

            tmp_k = k.copy()
            
            itog_page[ipk-1] = new_k

            if len(ns) > 1:
                tmp_k["Price_booking"] = ', '.join(ns[1:])
                itog_page[ipk:ipk] = [tmp_k]

        result_json[url_keys['PRICEPAGE']] = itog_page
        
        print('\n##################\nPage', (url_keys['PRICEPAGE']), 'is loaded!\n##################\n')

        if soup.select_one('.pager'):
            if soup.select_one('.pager').select('span')[-1].get('class')[0] == 'current_page':
                print('Last page loaded!')
                result_json[url_keys['PRICEPAGE']].append({'LastPage': True})
            else:
                result_json[url_keys['PRICEPAGE']].append({'LastPage': False})
        else:
            print('Last page loaded!')
            result_json[url_keys['PRICEPAGE']].append({'LastPage': True})
            
        return result_json
    
    except Exception as e:
        print('Something wrong! Try again...')
        print(traceback.print_exc())


def start(server_data, file_id):
    print('main parser start')
    strs_tmp = []
    if '4' in server_data['STARS']:
        strs_tmp.append('3')
    if '5' in server_data['STARS']:
        strs_tmp.append('2')
    if '6' in server_data['STARS']:
        strs_tmp.append('7')
    url_keys = {
        'STATEINC': server_data['STATEINC'],           
        'CHECKIN_BEG': server_data['CHECKIN_BEG'],  
        'CHECKIN_END': server_data['CHECKIN_BEG'],  
        'NIGHTS_FROM': server_data['NIGHTS_FROM'],         
        'NIGHTS_TILL': server_data['NIGHTS_FROM'],         
        'ADULT': server_data['ADULT'],               
        'CHILD': server_data['CHILD'],               
        'AGES': server_data['AGES'],
        'CURRENCY': server_data['CURRENCY'],
        'TOWNS': server_data['TOWNS'],
        'HOTELS': server_data['HOTELS'],
        'MEALS': server_data['MEALS'],
        'STARS': strs_tmp,
        'COSTMIN': server_data['COSTMIN'],
        'COSTMAX': server_data['COSTMAX'],
        'FILTER': '1',
        'DOLOAD': 1,   
        'PRICEPAGE': server_data['PRICEPAGE']
    }
    print('Get json:')
    print(url_keys)
    itog_file = main(url_keys)

    if os.path.isfile(f'{file_id}.json'):
        lll = {}
        with open(f'{file_id}.json', encoding='utf-8') as f:
            lll = json.load(f)
        for i in lll:
            lll[i].extend(itog_file[server_data['PRICEPAGE']])
        itog_file = lll

    with open(f'{file_id}.json', 'w', encoding='utf-8') as f:
        json.dump(itog_file, f, ensure_ascii=False, indent=4)
        print('Json file load!')
    return itog_file
