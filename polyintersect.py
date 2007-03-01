# -*- coding: iso-8859-2 -*-
# Wojciech Muła, http://wmula.republika.pl
# 5.12.2006
#
# Public domain
#
"Polygons intersection; solved using Sutherland-Hodgman algorithm."

__all__ = ['intersection']

import utils2D

def Sutherland_Hodgman(polygon, convex):
	"""
	Returns intersection of polygons, where:

	* polygon - any polygon (list of pairs (x,y))
	* convex  - convex polygon
	"""
	n         = len(convex)
	result    = polygon[:]
	direction = utils2D.vertex_order(convex)
	assert direction in ['CW', 'CCW'], ("Polygon not convex (%s)" % direction)

	for i in xrange(n):
		j  = (i+1) % n
		if direction == 'CCW':
			a, b, c = utils2D.line_equation(convex[i], convex[j])
		else: # CW
			a, b, c = utils2D.line_equation(convex[j], convex[i])

		result  = Sutherland_Hodgman_step(result, (a, b, c))
		if len(result) == 0:
			return []

	return result

def Sutherland_Hodgman_step(polygon, (a,b,c)):
	"""
	Polygon is given as set of pairs (x, y)
	Line is given as set of coefficients a, b, c of
	equation a*x + b*y + c = 0.

	Function returns polygon that lie at the "positive"
	side of line.
	"""
	n = len(polygon)
	result = []

	xs, ys = polygon[0]
	side_s = (a*xs + b*ys + c) >= 0.0
	for i in xrange(n):
		xn, yn = polygon[(i+1) % n]
		side_n = (a*xn + b*yn + c) >= 0.0

		# both points on "positive" side: save N
		if side_s and side_n:
			result.append((xn, yn))

		# both point on "negative" side: do not save anything
		elif (not side_s) and (not side_n):
			pass

		# point on opposite sides: clip, and save P, or P and N
		else:
			t = utils2D.intersect2((xs, ys), (xn, yn), (a, b, c))
			P = utils2D.lerp((xs, ys), (xn, yn), t)
			if side_n:
				result.append(P)
				result.append((xn, yn))
			else:
				result.append(P)

		xs = xn
		ys = yn
		side_s = side_n
	#for

	return result

intersection = Sutherland_Hodgman

# vim: ts=4 sw=4
