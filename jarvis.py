from math import acos, sqrt, pi

class Point:
	__slots__ = ['x', 'y']
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __str__(self):
		return "<Point %s, %s>" % (self.x, self.y)


def side(A, B, C):
	dx1 = B.x - A.x
	dy1 = B.y - A.y

	dx2 = C.x - A.x
	dy2 = C.y - A.y

	return (dx1*dy2 - dx2*dy1)


def jarvis(points):
	P = Q = points[0]
	for p in points[1:]:
		x = p.x
		y = p.y
		if p.y > P.y or (P.y == y and x > P.x):
			P = p
		
		if y < Q.y or (Q.y == y and x > Q.x):
			Q = p

	
	def alpha(x, y):
		r = x*x + y*y
		d = float(abs(x) + abs(y))
		if x >= 0 and y >= 0: return (y/d, r)
		if x <= 0 and y >= 0: return (2.0 - y/d, r)
		if x <= 0 and y <= 0: return (2.0 + abs(y)/d, r)
		if x >= 0 and y <= 0: return (4.0 - abs(y)/d, r)

	def angle(S, T):
		dx = T.x - S.x
		dy = T.y - S.y
		if dy < 0:
			return 100
		else:
			return alpha(dx, dy)[0]

	convex_hull = []

	# step 1
	S = Q
	while True:
		T = None
		Ta = None
		for p in points:
			if p is S:
				continue

			a = angle(S, p)
			if T is None or a < Ta:
				T = p
				Ta = a

		assert T is not None

		S = T
		convex_hull.append(S.x)
		convex_hull.append(S.y)
		if S == P:
			break


	# step 2
	S = P
	while True:
		T = None
		Ta = None
		for p in points:
			if p is S:
				continue

			a = angle(p, S)
			if T is None or a < Ta:
				T = p
				Ta = a

		assert T is not None

		S = T
		convex_hull.append(S.x)
		convex_hull.append(S.y)
		if S == Q:
			break

	return convex_hull


def jarvis(points):
	
	# find first point on CH
	P = points[0]
	for p in points[1:]:
		x = p.x
		y = p.y
		if p.y > P.y or (P.y == y and x > P.x):
			P = p
	
	P0 = Point(P.x - 100, P.y)
	P1 = P
	CH = [P0, P1]

	i  = 1
	while True:
		A = CH[i]
		B = CH[i-1]
		print len(points)

		for j, P in enumerate(points):
			if P is not A and P is not B:
				if side(A, B, P) > 0:
					B = P
				else:
					#if len(CH) > 2 and side(CH[1], CH[-1], P) > 0:
					#	points[j] = None

					if len(CH) > 1 and side(CH[1], B, P) > 0 and side(CH[-1], B, P) < 0:
						points[j] = None

		points = [P for P in points if P is not None]

		assert B is not None
		if B == CH[1]:
			break
		else:
			CH.append(B)
			i += 1

	#
	return [(P.x, P.y) for P in CH[1:]]



if __name__ == '__main__':
	import Image
	import ImageDraw
	from random import randint, seed

#	seed(100)

	S = 700
	n = 25*10
	points = [Point(randint(0, S), randint(0, S)) for i in xrange(n)]
	image = Image.new("RGB", (S, S))
	draw  = ImageDraw.Draw(image)

	def pt(p, color, r=4):
		draw.ellipse([p.x - r, p.y - r, p.x + r, p.y + r], fill = color)

	for p in points:
		pt(p, "#f00")

	try:
		convex_hull = jarvis(points)
		print len(convex_hull), convex_hull
		draw.polygon(convex_hull)
	finally:
		image.save("1.png", "PNG");
