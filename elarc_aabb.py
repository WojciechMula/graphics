# wm, $Date: 2007-03-25 16:27:30 $, $Revision: 1.3 $

from math import sin, cos, pi, atan2

def ellipse_tp(a, b, dx, dy):
	return atan2(dy*b/a, dx)


def elliptical_arc_bbox(x0, y0, rx, ry, start=0.0, end=2*pi, rot=0.0):
	cr = cos(rot)
	sr = sin(rot)

	def P(a):
		x = cos(a)*rx
		y = sin(a)*ry
		return (x*cr - y*sr, x*sr + y*cr)
	
	def angle(a):
		if a < 0.0:
			return a + 2*pi
		elif a > 2*pi:
			return a - 2*pi 
		else:
			return a

	X = [P(start)[0], P(end)[0]]
	Y = [P(start)[1], P(end)[1]]

	start = angle(start)
	end   = angle(end)
	a1    = ellipse_tp(rx, ry, sr, cr)
	a2    = ellipse_tp(rx, ry, -cr, sr)

	for a in map(angle, [a1, a2, a1+pi, a2+pi]):
		if start < end:
			if start <= a <= end:
				x, y = P(a)
				X.append(x)
				Y.append(y)
		else:
			if not (end < a < start):
				x, y = P(a)
				X.append(x)
				Y.append(y)

	return (x0 + min(X), y0 + min(Y)), (x0 + max(X), y0 + max(Y))
