def convex_hull(points):
	n = len(points)
	if n < 3:
		return points

	# calcuate centroid
	cx  = sum(x for x,y in points)/float(n)
	cy  = sum(y for x,y in points)/float(n)

	# move points by vector (-cx,-cy)
	tmp = [(x-cx, y-cy, i) for i, (x, y) in enumerate(points)]

	# sort them lexicographically
	def alpha(x, y):
		d = float(abs(x) + abs(y))
		if x >= 0 and y >= 0: return y/d
		if x <= 0 and y >= 0: return 2.0 - y/d
		if x <= 0 and y <= 0: return 2.0 + abs(y)/d
		if x >= 0 and y <= 0: return 4.0 - abs(y)/d
	
	def sort_fun( (x1, y1, i1), (x2, y2, i2) ):
		a1 = alpha(x1, y1)
		a2 = alpha(x2, y2)
		if a1 == a2:
			r1 = x1*x1 + y1*y1
			r2 = x2*x2 + y2*y2
			return cmp(r1, r2)
		else:
			return cmp(a1, a2)
		
	tmp.sort(sort_fun)

	# get a point on convex hull - point that has min x
	imin = 0
	for i, (x, y, _) in enumerate(tmp):
		if y < tmp[imin][1]:
			imin = i
		elif y == tmp[imin][1]:
			if x < tmp[imin][0]:
				imin = i

	tmp = tmp[imin:] + tmp[:imin]

	# find convex hull
	ai = 0
	while ai < n:
		bi = (ai + 1) % n
		ci = (ai + 2) % n

		a = tmp[ai]
		b = tmp[bi]
		c = tmp[ci]
		det = (c[0]-a[0]) * (b[1]-a[1]) - (c[1]-a[1]) * (b[0]-a[0])

		if det >= 0.0:
			tmp.pop(bi)
			n = n - 1
			if ai > 0:
				ai = ai - 1
		else:
			ai = ai + 1


	return [(x+cx, y+cy, i) for x, y, i in tmp]
