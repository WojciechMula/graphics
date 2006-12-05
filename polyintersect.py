"""
This is sample docstring!
"""

__all__ = ['intersection']

import utils2D

def Sutherland_Hodgman(polygon, convex):
	n      = len(convex)
	result = polygon[:]
	side   = utils2D.vertex_order(convex)
	assert side in ['CW', 'CCW'], ("side is %s" % side)

	for i in xrange(n):
		j  = (i+1) % n
		if side == 'CCW':
			a, b, c = utils2D.line_equation(convex[i], convex[j])
		else:
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

	Function returns polygon that lie on the "positive"
	side of line.
	"""
	n = len(polygon)
	result = []

	xs, ys = polygon[0]
	side_s = (a*xs + b*ys + c) >= 0.0
	for i in xrange(n):
		xn, yn = polygon[(i+1) % n]
		side_n = (a*xn + b*yn + c) >= 0.0

		# both points on "positive" side
		if side_s and side_n:
			result.append((xn, yn))

		# both point on "negative" side
		elif (not side_s) and (not side_n):
			# do not save any point
			pass

		# point on opposite sides
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
	#rof

	return result

intersection = Sutherland_Hodgman

# vim: ts=4 sw=4
