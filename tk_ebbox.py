"""
Exact bounding boxes of uniform B-splines degree 2.

Desingned to calculate bboxes of smoothed lines
and polygons used in Tkinter Canvas.

Author: Wojciech Mula
        wojciech_mula@poczta.onet.pl
"""

# changelog:
# 2x.11.2006

__all__ = ['qbezier_bounds', 'exact_line_bbox', 'exact_polygon_bbox']

def lerp((xa, ya), (xb, yb), t):
	return (xa + t*(xb-xa), ya + t*(yb-ya))

def qbezier_bounds((x0, y0), (x1, y1), (x2, y2)):
	"""
	Returns extents of cubic bezier curve given by three points.
	"""

	# cubic Bezier reprsented in polynomial base
	# f(t) = A*t^2 + B*t + C
	Ax =    x0 - 2*x1 + x2
	Bx = -2*x0 + 2*x1
	Cx =    x0

	Ay =    y0 - 2*y1 + y2
	By = -2*y0 + 2*y1
	Cy =    y0

	# find extremas:
	#	1) x(0) = x0
	#	2) x(1) = y0
	#	3) f(t_e), where f'(t_e)=0 and t_e in (0,1)
	x = [x0,x2]
	if abs(Ax) > 1e-10:
		t  = -Bx/(2*Ax)
		if 0.0 < t < 1.0:
			t2 = t*t
			x.append(Ax*t2 + Bx*t + Cx)

	y = [y0,y2]
	if abs(Ay) > 1e-10:
		t  = -By/(2*Ay)
		if 0.0 < t < 1.0:
			t2 = t*t
			y.append(Ay*t2 + By*t + Cy)
	
	return x, y


def exact_line_bbox(points):
	if len(points) < 2:
		return None
	elif len(points) == 2:
		X = [points[0][0], points[1][0]]
		Y = [points[0][1], points[1][1]]
	elif len(points) == 3:
		X, Y = qbezier_bounds(*points)
	else:
		def pt(points):
			x0, y0 = points[0]
			x1, y1 = points[1]
			p0     = (2*x0-x1, 2*y0-y1)

			x0, y0 = points[-1]
			x1, y1 = points[-2]
			pn     = (2*x0-x1, 2*y0-y1)

			p = [p0] + points[1:-1] + [pn]

			for i in xrange(1, len(points)-1):
				a = p[i-1]
				b = p[i]
				c = p[i+1]

				yield lerp(a, b, 0.5), b, lerp(b, c, 0.5)

		X = []
		Y = []
		for cp in pt(points):
			x, y = qbezier_bounds(*cp)
			X.extend(x)
			Y.extend(y)
	#fi

	return min(X), min(Y), max(X), max(Y)

def exact_polygon_bbox(points):
	if len(points) < 2:
		return None
	elif len(points) == 2:
		X = [points[0][0], points[1][0]]
		Y = [points[0][1], points[1][1]]
	else:
		def pt(points):
			p = points
			n = len(points)
			for i in xrange(n):
				a = p[(i-1) % n]
				b = p[i]
				c = p[(i+1) % n]

				yield lerp(a, b, 0.5), b, lerp(b, c, 0.5)

		X = []
		Y = []
		for cp in pt(points):
			x, y = qbezier_bounds(*cp)
			X.extend(x)
			Y.extend(y)
	#fi

	return min(X), min(Y), max(X), max(Y)

# vim: ts=4 sw=4 nowrap noexpandtab
