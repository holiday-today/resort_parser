from bs4 import BeautifulSoup
import requests
import json
import time
import datetime
from fake_useragent import UserAgent
import asyncio
import aiohttp
from multiprocessing import Process, freeze_support, Manager

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
    'user-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.106 Safari/537.36"
}

async def get_page_data(session, page):
    cok['query'] = page.split('Guest House')[0]

    async with session.post(url_getid, json=cok) as response:
        get_json = await response.json()
        dest_id = 0
        for j in get_json["results"]:
            if j['dest_type'] == 'hotel':
                dest_id = j['dest_id']
                break
        if dest_id == 0:
            cok["query"] = page.split('Guest House')[0]
            async with session.post(url_getid, json=cok) as response2:
                get_json = await response2.json()
                for j in get_json["results"]:
                    if j['dest_type'] == 'hotel':
                        dest_id = j['dest_id']
                        break
                if dest_id == 0:
                    cok["query"] = page.split('Resort')[0]
                    async with session.post(url_getid, json=cok) as response3:
                        get_json = await response3.json()
                        for j in get_json["results"]:
                            if j['dest_type'] == 'hotel':
                                dest_id = j['dest_id']
                                break
                        if dest_id == 0:
                            print(f'Hotel {page} not found!')
                            return {}
        return {page: dest_id}


async def gather_data(data):
    async with aiohttp.ClientSession() as session:
        
        tasks = []

        for page in data:
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        return await asyncio.gather(*tasks)

#############################################################################

# error возможна по limit

async def get_hotel(session, hotel_name, hotel_id, dop_data):
    url_search = f'https://www.booking.com/searchresults.en-gb.html?dest_id={hotel_id}&dest_type=hotel&checkin={str(dop_data[0])}&checkout={str(dop_data[1])}&group_adults={dop_data[2]}&no_rooms=1&group_children={dop_data[3]}'
    for age in dop_data[4]:
        url_search += f'&age={str(age)}'
    async with session.get(url_search, headers=headers) as response:
        print(f'{response.status}: {hotel_name}')
        return {hotel_name: await response.text()}


async def parse_hotels(data, dop_data):
    async with aiohttp.ClientSession() as session:
        tasks = []

        for hotel in data:
            hot_data = list(hotel.keys())[0]
            task = asyncio.create_task(get_hotel(session, hot_data, hotel[hot_data], dop_data))
            tasks.append(task)

        return await asyncio.gather(*tasks)

#############################################################################

async def get_hotel_data(session, hotel, hotelUrl, cur):
    url_hotel = hotelUrl.split('&checkin=')
    url_hotel = url_hotel[0] + '&selected_currency=' + cur + '&checkin=' + url_hotel[1]
    if cur == 'RUB':
        cur = 'RUB'
    elif cur == 'EUR':
        cur = '€'
    async with session.get(url_hotel, headers=headers) as response:
        print(f'{response.status}: {hotel}')
        return [hotel, url_hotel, await response.text(), cur]


async def parsw(mylist, cur):
    async with aiohttp.ClientSession() as session:
        tasks = []
        mylist = dict(mylist)
        for hotel in mylist:
            task = asyncio.create_task(get_hotel_data(session, hotel, mylist[hotel], cur))
            tasks.append(task)

        return await asyncio.gather(*tasks)

#############################################################################
nights = 0
cnt_a = 0
cnt_c = 0

def main_parser(datalist, storage):
    for el in datalist:
        name_h = el[0]
        url_h = el[1]
        r = el[2]
        cur = el[3]
    
        soup = BeautifulSoup(r, features="html.parser")
        rooms = soup.select('[class*="js-rt-block-row"]')
        params = {}
        currentRoom = ''
        
        for room in rooms:
            if not room.select_one('.bui-u-sr-only'):
                continue
    
            if room.select_one('[class*="-first"]'):
                currentRoom = room.select_one('.hprt-roomtype-icon-link').text.replace('\n', ' ')
                
                while not currentRoom[0].isalpha():
                    currentRoom = currentRoom[1:]
                while not currentRoom[-1].isalpha():
                    currentRoom = currentRoom[:-1]
    
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
            priceDefault = int(room.select_one('.prco-valign-middle-helper').text.replace('\n', ' ').split(cur)[-1][1:].replace(',', ''))
            nalog = room.select_one('[class*="prd-taxes-and-fees-under-price"]').text.split(cur)
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
                price['Без питания'] = priceDefault
    
            dopMeals = room.select_one(".bui-modal__header")
            t = BeautifulSoup(str(dopMeals), features="html.parser")
            t = t.select_one('p').text.split(cur)
    
            if len(t) > 1:
                t_low = t[0].lower()
                dopPrice = int(t[1].split(' ')[0][1:].replace(',', '')) * int(nights) * (int(cnt_a) + int(cnt_c))
                if 'all-inclusive costs' in t_low or 'all inclusive costs' in t_low:
                    price['|All Inclusive'] = priceDefault + dopPrice
                elif 'full board costs' in t_low:
                    price['|Full Board'] = priceDefault + dopPrice
                elif 'half board costs' in t_low:
                    price['|Half Board'] = priceDefault + dopPrice
                elif 'breakfast costs' in t_low:
                    price['|Bed Breakfast'] = priceDefault + dopPrice
            params[currentRoom]['Types'].append({'Sleeps': sleeps, 'Price': price})
        
        params = {key:value for key, value in params.items() if value['Types'] != []}
        params['url'] = url_h
        storage[name_h] = params
        print(f'{name_h} added!')
        if params == {}:
            print(f'{name_h} is empty!')

    #with open('itog.json', 'w', encoding='utf-8') as f:
    #    print('Wroten to file!')
    #    json.dump(res_data, f, ensure_ascii=False, indent=4)


def my_function(a_el, soups):
    for i in a_el:
        soup = BeautifulSoup(list(i.values())[0], features="html.parser")
        url_hotel = soup.select_one('.e13098a59f').get('href')
        soups[list(i)[0]] = url_hotel


def my_async(hh, func):
    manager = Manager()
    soups = manager.dict()
    a = len(hh)//2
    p = Process(target=func, args=([hh[:a], soups]))
    g = Process(target=func, args=([hh[a:], soups]))
    p.start()
    g.start()
    p.join()
    g.join()
    return soups

#############################################################################

def ParseBooking(data):
    global soups
    query = set([i["Name"] for i in data[:-1]])

    nights = data[-1]['NIGHTS']

    dt = data[-1]['DATE']
    checkin = datetime.date(int(dt[:4]), int(dt[4:6]), int(dt[6:]))
    checkout = checkin + datetime.timedelta(days=int(nights))

    cnt_a = data[-1]['ADULT']
    cnt_c = data[-1]['CHILD']

    dop_data = [checkin, checkout, cnt_a, cnt_c, data[-1]["AGES"]]

    print("Async booking parser start!")
    hotels_names = asyncio.run(gather_data(query))
    hotels_names = [i for i in hotels_names if i != {}]

    print("Parse Hotels...")
    hotels_html = asyncio.run(parse_hotels(hotels_names, dop_data))
    hhkeys = [{list(k.keys())[0]: list(k.values())[0]} for k in list(hotels_html)]
    
    print("Making soups...")
    final_hot_urls = my_async(hhkeys, my_function)

    print("Getting hotels urls...")
    a = asyncio.run(parsw(final_hot_urls, data[-1]['CUR']))

    print("Parse data...")
    get_soups = dict(my_async(a, main_parser))
    res_data = {key:value for key, value in get_soups.items() if len(value) > 0} # if value != {}
    #with open('itog.json', 'w', encoding='utf-8') as f:
    #    print('Wroten to file!')
    #    json.dump(res_data, f, ensure_ascii=False, indent=4)
    return res_data

#############################################################################
