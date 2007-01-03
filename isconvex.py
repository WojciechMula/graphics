# Wojciech Mula

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

if __name__ == '__main__':
	a = 0.0
	b = 1.0
	c = 0.5

	p1 = [(a,a), (b,a), (b,b), (a,b)]
	p2 = [(a,a), (c,c), (b,a), (b,b), (a,b)]

	print isconvex(p1)
	print isconvex(p2)

# vim: ts=4 sw=4
