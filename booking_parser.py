from bs4 import BeautifulSoup
import requests
import json
import time
import datetime

url_getid = 'https://accommodations.booking.com/autocomplete.json'
cok = {
    "query": None,
    "pageview_id": "f3ae6db9c405036b",
    "aid": 304142,
    "language": "ru",
    "size": 5
}
headers = {
            'Content-type': 'text/html; charset=UTF-8', 
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.5005.148 YaBrowser/22.7.2.902 Yowser/2.5 Safari/537.36'
    }

storage = {}

def ParseBooking(data):
    for el in data[:-1]:    
        s = el['Name'].split('*')[0][:-2].split('Guest House')[0]
        if s in storage:
            pass
        else:
            cok["query"] = s
            r = requests.post(url_getid, json=cok)
            dest_id = 0
            for j in r.json()["results"]:
                if j['dest_type'] == 'hotel':
                    dest_id = j['dest_id']
                    break
            if dest_id == 0:
                cok["query"] = s.split('Guest House')[0]
                r = requests.post(url_getid, json=cok)
                for j in r.json()["results"]:
                    if j['dest_type'] == 'hotel':
                        dest_id = j['dest_id']
                        break
                if dest_id == 0:
                    cok["query"] = s.split('Resort')[0]
                    r = requests.post(url_getid, json=cok)
                    for j in r.json()["results"]:
                        if j['dest_type'] == 'hotel':
                            dest_id = j['dest_id']
                            break
                    if dest_id == 0:
                        print(f'Hotel {s} not found!')
                        storage[s] = None
                        continue

            dt = el["Date"][:-4].split('.')
            checkin = datetime.date(int(dt[2]), int(dt[1]), int(dt[0]))
            checkout = checkin + datetime.timedelta(days=int(el["Nights"]))
            
            url_search = f'https://www.booking.com/searchresults.en-gb.html?dest_id={dest_id}&dest_type=hotel&checkin={str(checkin)}&checkout={str(checkout)}&group_adults={data[-1]["ADULT"]}&no_rooms=1&group_children={data[-1]["CHILD"]}'
            for age in data[-1]["AGES"]:
                url_search += f'&age={str(age)}'

            r = requests.get(url_search, headers=headers)
            soup = BeautifulSoup(r.text, features="html.parser")
            
            url_hotel = soup.select_one('.e13098a59f').get('href')
            r = requests.get(url_hotel, headers=headers)
            
            soup = BeautifulSoup(r.text, features="html.parser")
            rooms = soup.select('[class*="js-rt-block-row"]')

            params = {}
            currentRoom = ''
            
            for room in rooms:
                if not room.select_one('.bui-u-sr-only'):
                    continue
                if room.select_one('[class*="-first"]'):
                    currentRoom = room.select_one('.hprt-roomtype-icon-link').text.replace('\n', ' ')
                    RoomBed = ''
                    if 'double' in room.select_one('[class*="bed-types-wrapper"]').text:
                        RoomBed = 'double'
                    else:
                        RoomBed = 'single'
                    params[currentRoom] = {'RoomBed': RoomBed, 'Types': []}

                if room.select_one('li[class="bui-list__item e2e-cancellation"]') or room.select_one('[class*="bui-f-color-destructive"]'):
                    continue

                sleeps = room.select('.bui-u-sr-only')[0].text.replace('\n', ' ').split(' ')
                sleeps = [x for x in sleeps if x.isdigit()]
                if len(sleeps) == 2:
                    sleeps = sleeps[0]+"+"+sleeps[1]
                else:
                    sleeps = sleeps[0]

                price = {}
                priceDefault = int(room.select_one('.prco-valign-middle-helper').text.replace('\n', ' ').split('RUB')[-1][1:].replace(',', ''))
                nalog = room.select_one('[class*="prd-taxes-and-fees-under-price"]').text.split('RUB')
                if len(nalog) == 2:
                    nalog = int(nalog[1].split(' ')[0][1:].replace(',', ''))
                    priceDefault += nalog

                meals = room.select_one('.bui-list__description').text.lower()
                if 'all-inclusive' in meals:
                    price['All Inclusive'] = priceDefault
                elif 'breakfast' in meals and 'dinner' in meals and 'lunch' in meals and 'included' in meals:
                    price['Full Board'] = priceDefault
                elif 'breakfast' in meals and 'dinner' in meals and 'included' in meals:
                    price['Half Board'] = priceDefault
                elif 'breakfast' in meals and 'included' in meals:
                    price['Bed Breakfast'] = priceDefault
                else:
                    price['No meal'] = priceDefault

                dopMeals = room.select_one(".bui-modal__header")
                t = BeautifulSoup(str(dopMeals), features="html.parser")
                t = t.select_one('p').text.split('RUB')
                if len(t) > 1:
                    t_low = t[0].lower()
                    dopPrice = int(t[1].split(' ')[0][1:].replace(',', '')) * int(el["Nights"]) * (data[-1]["ADULT"] + data[-1]["CHILD"])
                    if 'all-inclusive costs' in t_low or 'all inclusive costs' in t_low:
                        price['|All Inclusive'] = priceDefault + dopPrice
                    elif 'full board costs' in t_low:
                        price['|Full Board'] = priceDefault + dopPrice
                    elif 'half board costs' in t_low:
                        price['|Half Board'] = priceDefault + dopPrice
                    elif 'breakfast costs' in t_low:
                        price['|Bed Breakfast'] = priceDefault + dopPrice

                params[currentRoom]['Types'].append({'Sleeps': sleeps, 'Price': price})

            storage[s] = params
            print(f'{s} added!')

    with open('itog.json', 'w', encoding='utf-8') as f:
        json.dump(storage, f, ensure_ascii=False, indent=4)

    return storage
