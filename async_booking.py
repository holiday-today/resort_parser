from bs4 import BeautifulSoup
import requests
import json
import time
import datetime
from fake_useragent import UserAgent
import asyncio
import aiohttp
from multiprocessing import Process, freeze_support

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

hotels_id = {}
storage = {}

query = ['Four Seasons Hotel Abu Dhabi at Al Maryah Island', 'Kingfisher Retreat',
                'Royal Beach Hotel & Resort',
                'Royal M hotel & Resort Fujairah',
                'Saadiyat Rotana Resort & Villas',
                'Sahara Beach Resort & Spa',
                'Sandy Beach Hotel & Resort Fujairah',
                'Shangri-La Hotel Qaryat Al Beri Abu Dhabi',
                'Sharjah Carlton Hotel',
                'Sharjah Palace Hotel',
                'Sharjah Premiere Hotel & Resort',
                'Sheraton Abu Dhabi Hotel and Resort',
                'Sheraton Sharjah Beach Resort & Spa',
                'Six Senses Zighy Bay',
                'Sofitel Abu Dhabi Corniche',
                'Southern Sun Hotel Abu Dhabi',
                'Swiss-Belhotel Sharjah',
                'Telal Resort AL Ain',
                'The Abu Dhabi Edition',
                'The Act Hotel',
                'The Chedi Al Bait Sharjah',
                'The Ritz Carlton Abu Dhabi Grand Canal',
                'The St. Regis Abu Dhabi',
                'The WB Abu Dhabi, Curio Collection By Hilton']

limit = asyncio.Semaphore(10)

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
                            #hotels_id[page] = None
                            return
        hotels_id[page] = {'dest_id': dest_id}


async def gather_data(data):
    async with aiohttp.ClientSession() as session:
        
        tasks = []

        for page in data:
            task = asyncio.create_task(get_page_data(session, page))
            tasks.append(task)

        await asyncio.gather(*tasks)

#############################################################################

async def get_hotel(session, hotel):
    url_search = f'https://www.booking.com/searchresults.en-gb.html?dest_id={hotels_id[hotel]["dest_id"]}&dest_type=hotel&checkin={20221015}&checkout={20221020}&group_adults={2}&no_rooms=1&group_children={0}'
    global limit
    with await limit:
        async with session.get(url_search, headers=headers) as response:
            soup = BeautifulSoup(await response.text(), features="html.parser")
            #with open(f'{hotel}.html', 'w', encoding='utf-8') as f:
            #    f.write(response_text)
            url_hotel = soup.select_one('.e13098a59f').get('href')
            print(url_hotel)
            hotels_id[hotel]['url'] = url_hotel


async def parse_hotels():
    async with aiohttp.ClientSession() as session:
        
        tasks = []

        for hotel in hotels_id:
            task = asyncio.create_task(get_hotel(session, hotel))
            tasks.append(task)

        await asyncio.gather(*tasks)

#############################################################################

loc_data = [
    'https://www.booking.com/hotel/om/six-senses-hideaway-zighy-bay.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=28922&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=40417068b6410228&srepoch=1660147153&from_beach_sr=1&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/the-ritz-carlton-abu-dhabi-grand-canal.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=474237&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=a3377068f31508b6&srepoch=1660147153&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/sofitel-abu-dhabi-corniche.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=292038&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=42a370681b200230&srepoch=1660147153&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/the-abu-dhabi-edition.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=4125129&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=ea4e706865d102fe&srepoch=1660147153&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/sheraton-sharjah-beach-resort-and-spa.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=1475859&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=587370688a970143&srepoch=1660147154&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/sharjah-palace.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=260010&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=bb287068b69e0012&srepoch=1660147154&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/telal-resort.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=1287536&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=9bde7068463801fc&srepoch=1660147153&from=searchresults',
    'https://www.booking.com/hotel/ae/sahara-beach-resort-amp-spa.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=3153157&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=61bd7068ac6601a8&srepoch=1660147154&from=searchresults',
    'https://www.booking.com/hotel/ae/saadiyat-rotana-resort-and-villas.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=2803703&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=eb427068c10501d4&srepoch=1660147154&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/sharjah-premiere-resort.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=72817&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=1d527068cc2c00ab&srepoch=1660147154&from=searchresults',
    'https://www.booking.com/hotel/ae/carlton-beach-sharjah.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=23243&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=e7987068c62500a7&srepoch=1660147154&from=searchresults',
    'https://www.booking.com/hotel/ae/sheraton-abu-dhabi-resort.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=67443&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=73dd7068bbc60235&srepoch=1660147153&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/the-wb-abu-dhabi-curio-collection-by-hilton.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=7859222&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=0f1e7068196602c3&srepoch=1660147153&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/royal-beach-resort.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=68263&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=06a070682a5401a1&srepoch=1660147153&from_beach_sr=1&beach_sr_walking_distance=1591&from=searchresults',
    'https://www.booking.com/hotel/ae/the-st-regis-saadiyat-island-abu-dhabi.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=321847&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=34927068c5ea009d&srepoch=1660147153&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/four-seasons-abu-dhabi-at-al-maryah-island.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=1690854&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=54f87068549c03be&srepoch=1660147154&from=searchresults',
    'https://www.booking.com/hotel/ae/royal-tulip-the-act.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=2009948&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=cc3b706865d202df&srepoch=1660147153&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/kingfisher-retreat.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=3308353&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=ca5e70685ad900e5&srepoch=1660147153&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/shangri-la-residence.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=492991&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=525270686bef0263&srepoch=1660147154&from_sustainable_property_sr=1&from=searchresults',
    'https://www.booking.com/hotel/ae/royal-m-and-resort-abu-dhabi-abu-dhabi.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=3999335&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=2a777068974801af&srepoch=1660147154&from=searchresults',
    'https://www.booking.com/hotel/ae/sandy-beach-resort.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=175711&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=8e057068f24a00a6&srepoch=1660147153&from_beach_sr=1&beach_sr_walking_distance=515&from=searchresults',
    'https://www.booking.com/hotel/ae/al-bait-sharjah-uae.en-gb.html?aid=304142&ucfs=1&arphpl=1&dest_id=3323556&dest_type=hotel&group_adults=2&req_adults=2&no_rooms=1&group_children=0&req_children=0&hpos=1&hapos=1&sr_order=popularity&srpvid=5fdb70689ccf0311&srepoch=1660147153&from_sustainable_property_sr=1&from=searchresults'
]

async def get_hotel_data(session, hotel):
    async with session.get(hotel, headers=headers) as response2: #hotels_id[hotel]['url']
        print('get_hotel_data')
        #soup = BeautifulSoup(await response2.text(), features="html.parser")
        #rooms = soup.select('[class*="js-rt-block-row"]')
        return await response2.text()


async def parsw():
        async with aiohttp.ClientSession() as session:
            print('parsw')
            tasks = []
    
            for hotel in loc_data: #hotels_id
                task = asyncio.create_task(get_hotel_data(session, hotel))
                tasks.append(task)
    
            return await asyncio.gather(*tasks)


def main():
    print("Let's go!")
    #asyncio.run(gather_data(query))
    #print(time.time() - start_time)
    #print(hotels_id)
    #print("Start parse Hotels!")
    #asyncio.run(parse_hotels())
    #print(time.time() - start_time)
    print("Start parse data!")
    a = asyncio.run(parsw())
    print(time.time() - start_time)
    for i in a:
        soup = BeautifulSoup(i, features="html.parser")
        print(time.time() - start_time)
    print(time.time() - start_time)

#main()
start_time = time.time()

def my_function(a_el):
    for i in a_el:
        soup = BeautifulSoup(i, features="html.parser")
        print(time.time() - start_time)

def f(e):
    print(e)

def qq():
    global start_time
    print('q')
    print(__name__)
    freeze_support()
    a = parsw()
    print(len(a))
    start_time = time.time()
    print(123)
    #e = [BeautifulSoup(i, features="html.parser") for i in a]
    p = Process(target=my_function, args=([a[:11]]))
    g = Process(target=my_function, args=([a[11::]]))
    print(time.time() - start_time)
    g.start()
    p.start()
    p.join()
    g.join()
    print('Final time:', time.time() - start_time)
