# -*- coding: iso-8859-2 -*-
# Convex polygon utils
#
# Wojciech Muła, http://wmula.republika.pl/
# public domain

# changelog
"""
21.02.2007 - point_in_convex_polygon
 3.01.2007 - vertex_order, isconvex expressed using vertex_order
 9.05.2005 - isconvex
"""

def isconvex(poly):
	"""
	Checks if 'poly' is convex; polygon is given
	as list of pairs (x,y).
	"""
	n = len(poly)
	if n < 3:
		# not a polygon
		return False
	elif n == 3:
		# triangles are convex polygons
		return True
	else:
		return vertex_order(poly) in ['CW', 'CCW']


def vertex_order(poly):
	n = len(poly)
	if n < 3:
		# not a polygon
		return 'unspecified'


	# Algorithm:
	#   We check all triples of adjecent points. For example if polygon
	#   is defined by five points A,B,C,D,E we check A,B,C; B,C,D; C,D,E;
	#   D,E,A; E,A,B.
	#
	#   First two points defines a line, and we check on which line's side
	#   lie third point. If all "third" points lie on the same side then
	#   polygon is convex.

	valid_side = None
	for i in xrange(n):
		j = (i+1) % n
		k = (i+2) % n

		# Get three adjecent vertices
		x0, y0 = poly[i] # A
		x1, y1 = poly[j] # B
		x2, y2 = poly[k] # C 

		# Get side  (line is given as a*x+b*y+c=0, where c=0)
		side = (y1-y0)*(x2-x0) - (x1-x0)*(y2-y0)

		if side != 0.0:
			if valid_side is None:
				valid_side = side > 0.0
			elif (side > 0.0) != valid_side: # other side:
				return 'nonconvex'           # polygon isn't convex
	
	if valid_side > 0:
		return 'CCW'
	else:
		return 'CW'


def point_in_convex_polygon(points, (x, y)):
	"""
	Returns true if point (x,y) lie inside
	of convex polygon given with points
	"""
	side = None
	n    = len(points)
	for i in xrange(n):
		xi, yi = points[i]
		xj, yj = points[(i+1) % n]

		d = (x - xi)*(yj - yi) - (y - yi)*(xj - xi)
		if d == 0.0:
			continue
		else:
			if side is None:
				side = d > 0.0

			# point have to lie at the same side
			# of all lines
			elif (d > 0.0) != side:
				return False
	
	return True


if __name__ == '__main__':
	a = 0.0
	b = 1.0
	c = 0.5

	p1 = [(a,a), (b,a), (b,b), (a,b)]
	p2 = [(a,a), (c,c), (b,a), (b,b), (a,b)]

	print isconvex(p1)
	print isconvex(p2)
	
	import Image
	import ImageDraw
	import aabb2D

	poly = "74.0 191.0 156.0 245.0 321.0 274.0 464.0 248.0 389.0 101.0 258.0 53.0 112.0 94.0"
	poly = map(float, poly.split())
	poly = zip(poly, poly[1:])[::2]

	((xmin, ymin), (xmax, ymax)) = aabb2D.bb_points(poly)

	image = Image.new("RGB", (int(xmax+20), int(ymax+20)))
	draw  = ImageDraw.Draw(image)
	draw.polygon(poly);

	for y in xrange(int(ymin), int(ymax)+1):
		print "%d of %d" % (y, int(ymax))
		for x in xrange(int(xmin), int(xmax)+1):
			if point_in_convex_polygon(poly, (x, y)):
				image.putpixel((x, y), (255, 0, 0))

	image.save('test.bmp');

# vim: ts=4 sw=4 nowrap
