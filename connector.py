def sres(a, b):
	a = a.lower().split(' ')
	b = b.lower().split(' ')
	c = set(a) & set(b)
	r = 0
	for i in (set(a) - c):
		for j in (set(b) - c):
			if i in j or j in i:
				r+=1
	return len(c)+r


def connect(list1, list2, key):
	list3 = []
	for i in list1:
		max_q = 0
		q_id = []
		for j in list2:
			q = sres(i[key], j)
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
			q = sres(i[0][key], j)
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
				q = len(j.split(' '))-sres(i[0][key], j)
				if q < min_q:
					min_q = q
					s = [j]
				elif q == min_q:
					s.append(j)
			q_id = s
			if len(q_id)>1:
				q_id = []
		i[1] = q_id
		#else:
		#	i[1] = []
	return list3
