def convex_hull(points):
	n = len(points)
	if n < 3:
		return None
	elif n == 3:
		return [(p, i) for i, p in enumerate(points)]

	# calcuate centroid
	cx  = sum(x for x,y in points)/float(n)
	cy  = sum(y for x,y in points)/float(n)

	def alpha(x, y):
		r = x*x + y*y
		d = float(abs(x) + abs(y))
		if x >= 0 and y >= 0: return (y/d, r)
		if x <= 0 and y >= 0: return (2.0 - y/d, r)
		if x <= 0 and y <= 0: return (2.0 + abs(y)/d, r)
		if x >= 0 and y <= 0: return (4.0 - abs(y)/d, r)

	# move points by vector (-cx,-cy)
	tmp = [ (x, y, i, alpha(x-cx, y-cy))
		for i, (x, y) in enumerate(points)]

	# sort them lexicographically
	tmp.sort(key=lambda (x, y, i, v): v)

	# get a point on convex hull - point that has min. y and x
	imin = 0
	for i, (x, y, _, _) in enumerate(tmp):
		if y < tmp[imin][1]:
			imin = i
		elif y == tmp[imin][1]:
			if x < tmp[imin][0]:
				imin = i

	tmp = tmp[imin:] + tmp[:imin]

	# find convex hull
	ai = 0
	while ai < n:
		xa, ya, _, _ = tmp[ai]
		xb, yb, _, _ = tmp[(ai + 1) % n]
		xc, yc, _, _ = tmp[(ai + 2) % n]

		if (xc-xa) * (yb-ya) - (yc-ya) * (xb-xa) >= 0.0:
			tmp.pop((ai + 1) % n)
			n = n - 1
			if ai > 0:
				ai = ai - 1
		else:
			ai = ai + 1


	return [((x, y), i) for (x, y, i, _) in tmp]

# vim: ts=4 sw=4
