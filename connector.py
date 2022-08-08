import re

def sres(a, b):
	a = re.split(' |-', a.lower())
	b = re.split(' |-', b.lower())
	c = set(a) & set(b)
	return len(c)

def chng(x):
	if 'one' in x.lower():
		return x.replace('One', '1').replace('one', '1')
	elif 'two' in x.lower():
		return x.replace('Two', '1').replace('two', '1')
	elif 'three' in x.lower():
		return x.replace('Three', '1').replace('three', '1')
	elif 'four' in x.lower():
		return x.replace('Four', '1').replace('four', '1')
	elif 'five' in x.lower():
		return x.replace('Five', '1').replace('five', '1')
	elif 'six' in x.lower():
		return x.replace('Six', '1').replace('six', '1')
	else:
		return x
	#return x.replace('One', '1').replace('one', '1').replace('Two', '2').replace('two', '2').replace('Three', '3').replace('three', '3').replace('Four', '4').replace('four', '4').replace('Five', '5').replace('five', '5')

def connect(list1, list2, key):
	list3 = []
	for i in list1:
		max_q = 0
		q_id = []
		for j in list2:
			q = sres(chng(i[key]), chng(j))
			if q > max_q:
				q_id = [j]
				max_q = q
			elif q == max_q:
				q_id.append(j)
		list3.append([i, q_id])
	
	for i in list3:
		max_q = 0
		q_id = []
		for j in i[1]:
			q = sres(chng(i[0][key]), chng(j))
			if q > max_q:
				q_id = [j]
				max_q = q
			elif q == max_q:
				q_id.append(j)
		#if len(set([x["Room"] for x in q_id])) == 1:
		if len(q_id)>1:
			min_q = 99
			s = []
			for j in q_id:
				q = len(re.split(' |-', j))-sres(chng(i[0][key]), chng(j))
				if q < min_q:
					min_q = q
					s = [j]
				elif q == min_q:
					s.append(j)
			q_id = s
		i[1] = q_id
		#else:
		#	i[1] = []
	return list3
