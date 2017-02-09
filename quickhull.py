from math import acos, sqrt, pi

class Point:
	__slots__ = ['x', 'y']
	def __init__(self, x, y):
		self.x = x
		self.y = y

	def __str__(self):
		return "<Point %s, %s>" % (self.x, self.y)

	__repr__ = __str__


def side(A, B, P):
	dx = B.x - A.x
	dy = B.y - A.y

	a = dy
	b = -dx
	c = -(a * B.x + b * B.y)

	return a * P.x + b * P.y + c


def quickhull(points):
	A = B = points[0]
	for p in points[1:]:
		x = p.x
		y = p.y
		if A.x < x:
			A = p
		if B.x > x:
			B = p

	s1 = set()
	s2 = set()
	for p in points:
		if p is not A and p is not B:
			if side(A, B, p) > 0:
				s1.add(p)
			else:
				s2.add(p)


	def QH(A, B, P):
		if len(P) == 0:
			return []
		elif len(P) == 1:
			C = P.pop()
			draw.polygon([A.x, A.y, B.x, B.y, C.x, C.y])
			return [C]

		dx = B.x - A.x
		dy = B.y - A.y
		a = dy
		b = -dx
		c = -(a * B.x + b * B.y)

		C = None
		D = None
		for p in P:
			d = a * p.x + b * p.y + c
			if C is None or d > D:
				C = p
				D = d

		draw.polygon([A.x, A.y, B.x, B.y, C.x, C.y])
		assert C is not None

		s1 = set()
		s2 = set()
		for p in P:
			if p is C:
				continue

			if side(A, C, p) > 0:
				s1.add(p)
			elif side(C, B, p) > 0:
				s2.add(p)

		#print s1, s2
		return QH(A, C, s1) + [C] + QH(C, B, s2)


	return [A] + QH(A, B, s1) + [B] + QH(B, A, s2)


if __name__ == '__main__':
	import Image
	import ImageDraw
	from random import randint, seed

#	seed(100)

	S = 700
	n = 320
	points = [Point(randint(0, S), randint(0, S)) for i in xrange(n)]
	image = Image.new("RGB", (S, S))
	draw  = ImageDraw.Draw(image)

	def pt(p, color="#00f"):
		draw.ellipse([p.x - r, p.y - r, p.x + r, p.y + r], fill = color)

	r = 4
	for p in points:
		pt(p)

	try:
		convex_hull = []
		for p in quickhull(points):
			convex_hull.append(p.x)
			convex_hull.append(p.y)

		#print len(convex_hull), convex_hull
		draw.polygon(convex_hull)
	finally:
		image.save("1.png", "PNG");
