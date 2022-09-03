from bs4 import BeautifulSoup
import requests
import json
import time
import datetime
import asyncio
import aiohttp
from multiprocessing import Process, freeze_support, Manager

url_getid = 'https://accommodations.booking.com/autocomplete.json'
cok = {
    "query": None,
    "pageview_id": "f3ae6db9c405036b",
    "aid": 304142,
    "language": "en-gb",
    "size": 3
}
headers = {
    'Content-type': 'text/html; charset=UTF-8', 
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    "User-Agent": "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/78.0.3904.87 Safari/537.36"
}

async def get_page_data(session, page, dop_data):
    cok['query'] = page
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
                            return {page: {}}
        url_search = f'https://www.booking.com/searchresults.en-gb.html?dest_id={dest_id}&dest_type=hotel&checkin={str(dop_data[0])}&checkout={str(dop_data[1])}&group_adults={dop_data[2]}&no_rooms=1&group_children={dop_data[3]}'
        try:
            for age in dop_data[4]:
                url_search += f'&age={str(age)}'
            async with session.get(url_search, headers=headers, timeout=10) as response2:
                print(f'{response2.status}: {page}')
                if response2.status == 200:
                    return {page: await response2.text()}
        except Exception:
            return {page: {}}


async def gather_data(data, dop):
    async with aiohttp.ClientSession() as session:
        
        tasks = []

        for page in data:
            task = asyncio.create_task(get_page_data(session, page, dop))
            tasks.append(task)

        return await asyncio.gather(*tasks)

#############################################################################

# # error возможна по limit

# async def get_hotel(session, hotel_name, hotel_id, dop_data):
#     url_search = f'https://www.booking.com/searchresults.en-gb.html?dest_id={hotel_id}&dest_type=hotel&checkin={str(dop_data[0])}&checkout={str(dop_data[1])}&group_adults={dop_data[2]}&no_rooms=1&group_children={dop_data[3]}'
#     for age in dop_data[4]:
#         url_search += f'&age={str(age)}'
#     async with session.get(url_search, headers=headers) as response:
#         print(f'{response.status}: {hotel_name}')
#         return {hotel_name: await response.text()}


# async def parse_hotels(data, dop_data):
#     async with aiohttp.ClientSession() as session:
#         tasks = []

#         for hotel in data:
#             hot_data = list(hotel.keys())[0]
#             task = asyncio.create_task(get_hotel(session, hot_data, hotel[hot_data], dop_data))
#             tasks.append(task)

#         return await asyncio.gather(*tasks)

#############################################################################

async def get_hotel_data(session, hotel, hotelUrl, cur):
    url_hotel = hotelUrl.split('&checkin=')
    url_hotel = url_hotel[0] + '&selected_currency=' + cur + '&checkin=' + url_hotel[1]
    if cur == 'RUB':
        cur = 'RUB'
    elif cur == 'EUR':
        cur = '€'
    try:
        async with session.get(url_hotel, headers=headers, timeout=10) as response:
            print(f'{response.status}: {hotel}')
            if response.status == 200:
                return [hotel, url_hotel, await response.text(), cur]
    except asyncio.TimeoutError:
        print(f'TimeOut: {hotel}')
        return [hotel, url_hotel]


async def parsw(mylist, cur):
    async with aiohttp.ClientSession() as session:
        tasks = []
        mylist = dict(mylist)
        for hotel in mylist:
            task = asyncio.create_task(get_hotel_data(session, hotel, mylist[hotel], cur))
            tasks.append(task)

        return await asyncio.gather(*tasks)

#############################################################################

def main_parser(datalist, storage, tt):
    nights = tt[0]
    cnt_a = tt[1]
    cnt_c = tt[2]
    for el in datalist:
        name_h = el[0]
        url_h = el[1]

        if len(el) == 2:
            params = {}
            params['url'] = url_h
            storage[name_h] = params
            print(f'"{name_h}" is failed to connection!')
            continue

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
    
                params[currentRoom] = {'Types': []}
    
            sleeps = room.select('.bui-u-sr-only')[0].text.replace('\n', ' ').split(' ')
            sleeps = [x for x in sleeps if x.isdigit()]
            if len(sleeps) == 2:
                sleeps = sleeps[0]+"+"+sleeps[1]
            else:
                sleeps = sleeps[0]
    
            price = {}
            priceDefault = int(room.select_one('.prco-valign-middle-helper').text.replace('\n', ' ').split(cur)[-1][1:].replace(',', ''))
            pd = priceDefault
            nalog = room.select_one('[class*="prd-taxes-and-fees-under-price"]').text.split(cur)
            if len(nalog) == 2:
                nalog = int(nalog[1].split(' ')[0][1:].replace(',', ''))
                priceDefault += nalog
    
            meals = room.select_one('.bui-list__description').text.lower()
            if 'all-inclusive' in meals:
                price['All Inclusive'] = str(priceDefault)
            elif 'breakfast' in meals and 'dinner' in meals and 'lunch' in meals and 'included' in meals:
                price['Full Board'] = str(priceDefault)
            elif 'breakfast' in meals and 'dinner' in meals and 'included' in meals:
                price['Half Board'] = str(priceDefault)
            elif 'breakfast' in meals and 'included' in meals:
                price['Bed Breakfast'] = str(priceDefault)
            else:
                price['Без питания'] = str(priceDefault)
    
            dopMeals = room.select_one(".bui-modal__header")
            t = BeautifulSoup(str(dopMeals), features="html.parser")
            t = t.select_one('p').text.split(cur)
    
            if len(t) > 1:
                t_low = t[0].lower()
                dopPrice = int(t[1].split(' ')[0][1:].replace(',', '')) * int(nights) * (int(cnt_a) + int(cnt_c))
                if 'all-inclusive costs' in t_low or 'all inclusive costs' in t_low:
                    price['|All Inclusive'] = str(priceDefault + dopPrice)
                elif 'full board costs' in t_low:
                    price['|Full Board'] = str(priceDefault + dopPrice)
                elif 'half board costs' in t_low:
                    price['|Half Board'] = str(priceDefault + dopPrice)
                elif 'breakfast costs' in t_low:
                    price['|Bed Breakfast'] = str(priceDefault + dopPrice)

            types = {'Sleeps': sleeps, 'Price': price}

            #print(price)

            refnd = room.select_one('li[class*="e2e-cancellation"]').select_one('.bui-list__description').text.replace('\n', ' ')[1:-1]

            if room.select_one('[class*="bui-f-color-destructive"]'):
                types['Discount'] = str(int(room.select_one('[class*="bui-f-color-destructive"]').text.replace('\n', ' ').split(cur)[-1][1:].replace(',', '')) - pd) + f' ({refnd})'
            else:
                types['Discount'] = None

            for meal_el in types['Price']:
                types['Price'][meal_el] += f' ({refnd})'

            for elem in params[currentRoom]['Types']:
                if types['Sleeps'] == elem['Sleeps']:
                    if [k for k in elem['Price']] == [k for k in types['Price']]:
                        for k in elem['Price']:
                            if k in types['Price']:
                                elem['Price'][k] += f', {types["Price"][k]}'
                                types["Price"].pop(k)
                        if elem['Discount'] != None  and types['Discount'] != None :
                            elem['Discount'] += f', {types["Discount"]}'
                            types.pop('Discount')

            if types["Price"] != {}:
                params[currentRoom]['Types'].append(types)
        
        params = {key:value for key, value in params.items() if value['Types'] != []}
        params['url'] = url_h
        storage[name_h] = params # RecursionError: maximum recursion depth exceeded while pickling an object
        print(f'"{name_h}" added!')
        if params == {}:
            print(f'"{name_h}" is empty!')


def my_function(a_el, soups, tt):
    for i in a_el:
        soup = BeautifulSoup(list(i.values())[0], features="html.parser")
        url_hotel = soup.select_one('a.e13098a59f').get('href')
        soups[list(i)[0]] = url_hotel
        print(f'"{list(i)[0]}" url got!')


def my_async(hh, func, tt=0):
    lh = len(hh)
    my_collection = {}

    p = 6
    
    if lh == 0:
        return {}

    manager = Manager()

    for times in range(0, lh, p):
        soups = manager.dict()
        b = []

        for i in range(times, min(lh, p)):
            b.append(Process(target=func, args=([hh[i:i+1], soups, tt])))
        for i in b:
            i.start()
        for i in b:
            i.join()

        lh -= p
        my_collection.update(soups)

    return my_collection

#############################################################################

def ParseBooking(data):
    query = set([i["Name"] for i in data[:-1]])

    nights = data[-1]['NIGHTS']

    dt = data[-1]['DATE']
    checkin = datetime.date(int(dt[:4]), int(dt[4:6]), int(dt[6:]))
    checkout = checkin + datetime.timedelta(days=int(nights))

    cnt_a = data[-1]['ADULT']
    cnt_c = data[-1]['CHILD']

    dop_data = [checkin, checkout, cnt_a, cnt_c, data[-1]["AGES"]]

    print("Async booking parser start!")
    hotels_names = asyncio.run(gather_data(query, dop_data))
    unfound_hotels = [i for i in hotels_names if list(i.values())[0] == {}]
    hotels_names = [i for i in hotels_names if list(i.values())[0] != {}]

    print("Parse Hotels...")
    #hotels_html = asyncio.run(parse_hotels(hotels_names, dop_data))
    hhkeys = [{list(k.keys())[0]: list(k.values())[0]} for k in list(hotels_names)]
    
    print("Making soups...")
    final_hot_urls = my_async(hhkeys, my_function)

    print("Getting hotels urls...")
    a = asyncio.run(parsw(final_hot_urls, data[-1]['CUR']))

    print("Parse data...")
    res_data = dict(my_async(a, main_parser, [nights, cnt_a, cnt_c]))
    #res_data = {key:value for key, value in get_soups.items()} # if value != {}

    for x in unfound_hotels:
        res_data.update(x)

    with open('itog.json', 'w', encoding='utf-8') as f:
        print('Wroten to file!')
        json.dump(res_data, f, ensure_ascii=False, indent=4)
    
    return res_data

#############################################################################
