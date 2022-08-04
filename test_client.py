import requests

c = int(input())
if c == 0:
	res = requests.post("http://127.0.0.1:3000/get/allresult", 
		{
		    'STATEINC': '78',           # Код страны
		    'CHECKIN_BEG': '20220905',  # Дата въезда С гггг.мм.дд
		    'NIGHTS_FROM': '3',         # Мин. кол-во ночей
		    'ADULT': '2',               # Кол-во взрослых
		    'CHILD': '1',               # Кол-во детей
		    'AGES': [
		        9,
		    ],
		    'TOWNS': [                  # Города
		        
		    ],
		    'HOTELS': [                 # Отели
	    	    414, 21,
	    	],
	    	'MEALS': [                  # Питание (аналогично HOTELS)
	    	    
	    	],
	    	'STARS': [                  # Звезды
	    	    
	    	]
		})
else:
	res = requests.get("http://127.0.0.1:3000/get/allresult")
print(res.json())

