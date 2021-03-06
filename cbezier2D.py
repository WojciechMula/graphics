# -*- coding: iso-8859-2 -*-
# 2D cubic Beziers releated routines
# License: BSD
#
# Wojciech Mu�a
# wojciech_mula@poczta.onet.pl

# changelog
'''
 6.02.2007:
	+ is_flat2
	+ is_flat3
	* is_flat -> is_flat1

11.11.2006:
	+ point
	+ bbox
	+ cbbox
	+ split
	+ eq_coefs
	+ is_flat
	+ adaptive_split
	+ cc_intersections
	+ cl_intersections
	+ distance
	+ length
'''

from math import sqrt

from poly_root import solve3, solve2
from aabb2D    import bb_points, bb_crossing
from utils2D   import len_sqr, len_sqrt, line_equation, lerp, dotprod2, intersect




def point((A, B, C, D), t):
	"""
	Returns point p(t) at Bezier Curve given as four
	control points A, B, C and D.

	Parameter t have to lie in range [0, 1] but this
	is **not tested**!
	"""
	A = lerp(A, B, t)
	B = lerp(B, C, t)
	C = lerp(C, D, t)
	
	A = lerp(A, B, t)
	B = lerp(B, C, t)
	
	A = lerp(A, B, t)
	return A


def bbox(A, B, C, D):
	"""
	Returns exact bounding box of curve
	"""
	(ax, bx, cx, dx), (ay, by, cy, dy) = eq_coefs(A, B, C, D)

	# find extrema
	# f(t)  = a*t^3 + b*t^2 + c*t + d
	# f'(t) = 3a*t^2 + 2b*t + c
	# find t that f'(t) = 0
	
	def is_root(t):
		return zero(t.imag, 1e-10) and 0.0 <= t.real <= 1.0

	X = [A[0], D[0]]
	for t in [t.real for t in solve2(3*ax, 2*bx, cx) if is_root(t)]:
		t2 = t*t
		t3 = t*t2
		X.append(ax*t3 + bx*t2 + cx*t + dx)
	
	Y = [A[1], D[1]]
	for t in [t.real for t in solve2(3*ay, 2*by, cy) if is_root(t)]:
		t2 = t*t
		t3 = t*t2
		Y.append(ay*t3 + by*t2 + cy*t + dy)
	
	return (min(X), min(Y)), (max(X), max(Y))


def cbbox(A, B, C, D):
	"""
	Returns bounding box of control points
	"""
	return bb_points([A, B, C, D])


def split((A, B, C, D), t):
	"""
	Function splits Bezier curve (given by control
	points A, B, C and D) at point p(t).  De Casteljau
	algorithm is used.

	Returns control points of curves
	"""
	assert 0.0 <= t <= 1.0, "t \in [0,1]"

	p00 = lerp(A, B, t)
	p01 = lerp(B, C, t)
	p02 = lerp(C, D, t)
	
	p10 = lerp(p00, p01, t)
	p11 = lerp(p01, p02, t)
	
	p20 = lerp(p10, p11, t)
	return (A, p00, p10, p20), (p20, p11, p02, D)


def eq_coefs((x0, y0), (x1, y1), (x2, y2), (x3, y3)):
	"""
	Returns coefficients of polynomial represents
	Bezier curve, i.e.
		x(t) = ax*t^3 + bx*t^2 + cx*t + dx
		y(t) = ay*t^3 + by*t^2 + cy*t + dy
	"""
	
	ax =   -x0 + 3*x1 - 3*x2 + x3	# t^3
	bx =  3*x0 - 6*x1 + 3*x2		# t^2
	cx = -3*x0 + 3*x1				# t^1
	dx =    x0						# t^0
	
	ay =   -y0 + 3*y1 - 3*y2 + y3	# t^3
	by =  3*y0 - 6*y1 + 3*y2		# t^2
	cy = -3*y0 + 3*y1				# t^1
	dy =    y0						# t^0

	return (ax, bx, cx, dx), (ay, by, cy, dy)


def is_flat1((A, B, C, D), EPS=1e-6):
	"""
	Checks if Bezier curve is "flat".

	Bezier curve is flat if length of control polyline
	A-B-C-D	is equal length of segment A-D.  Equality
	is checking with some error margin EPS defined by
	user.

	Returns pair:
		1. (|A-B| + |B-C| + |C-D|)/|A-B| < EPS
		2. |A-D|
	"""
	lab = len_sqrt(A, B)
	lbc = len_sqrt(B, C)
	lcd = len_sqrt(C, D)
	lad = len_sqrt(A, D)

	if zero(lad, EPS):
		return False, 0.0
	else:
		return (equal((lab + lbc + lcd)/lad, 1.0, EPS), lad)


def is_flat2((A, B, C, D), d=1e-3):
	x_AC, y_AC = lerp(A, C, 0.5)
	x_BD, y_BD = lerp(B, D, 0.5)

	d1 = abs(x_AC - B[0]) + abs(y_AC - B[1])
	
	d2 = abs(x_BD - C[0]) + abs(y_BD - C[1])

	return d1 <= d and d2 <= d


def is_flat3((A, B, C, D), d=0.1, p=None):
	l_AD  = len_sqrt(A, D)

	if zero(l_AD, 1e-10):
		return (False, 0.0, None, None)

	l_ABp = dotprod2(A, B, D)/l_AD
	l_ACp = dotprod2(A, C, D)/l_AD

	# if C' lie on segment AD and B' lie on segment AD
	# and order of points is A, B', C', D
	if  0.0 < l_ABp < l_ACp < l_AD:
	   
		d_B = sqrt(abs(len_sqr(A, B) - l_ABp*l_ABp))
		d_C = sqrt(abs(len_sqr(A, C) - l_ACp*l_ACp))

		if type(d) is not None:
			d = float(d)
			val = d_B <= d and d_C <= d
		elif type(p) is not None:
			p = float(p)
			val = d_B/d <= p and d_C/d <= p
		else:
			raise ValueError("Either parameter p or d have to be set.")
		
		return (val, l_AD, d_B, d_C)
		
	else:
		return (False, l_AD, None, None)



def adaptive_split((A0, B0, C0, D0), is_flat):
	"""
	Return **sorted** list of pairs (parameter, points)
	at Bezier curve that are define endpoint of flat
	segments of curve.  To determine if segment
	of curve is flat external function is_flat is used.
	
	Example:

	def my_is_flat(A, B, C, D):
		return is_flat((A, B, C, D), 1e-3)
	
	def my_is_flat(A, B, C, D):
		# as above, but segment must be shoter then 0.5 units
		return is_flat((A, B, C, D), 1e-3) and lengh(C, D) < 0.5
	
	tp     = adaptive_split((A, B, C, D), my_is_flat)
	points = [p for t, p in tp]
	canvas.create_line(*points)
	"""

	queue  = [((A0, B0, C0, D0), 0.0, 1.0)]
	result = [(0.0, A0)]

	while queue:
		(A, B, C, D), ta, tb = queue.pop(0)
		if is_flat(A, B, C, D):
			result.append((tb, D))
		else:
			p1, p2 = split((A, B, C, D), 0.5)
			tab    = (ta+tb)/2
			queue.insert(0, (p2, tab, tb))
			queue.insert(0, (p1, ta, tab))

	return result


def cc_intersections(p0, p1, is_flat):
	"""
	Function returns list of intersection points
	of two curves p0 = (A0, B0, C0, D0) and
	p1 = (A1, B1, C1, D1).

	Curves are splitted and when curve segments are flat
	(see functions is_flat, is_flat2) intersection between
	stright lines are calculated.

	Single intersection is given with 3-tuple:
		1. u - parameter on curve p0
		2. v - parameter on curve p1
		3. P - point
	"""

	queue  = [((p0, cbbox(*p0), 0.0, 1.0), (p1, cbbox(*p1), 0.0, 1.0))]
	result = []
	while queue:
		P0, P1 = queue.pop()
		(p0, cbb0, ua, ub), (p1, cbb1, va, vb) = P0, P1
		if bb_crossing(cbb0, cbb1):
			flat0 = is_flat(*p0)
			flat1 = is_flat(*p1)
			if flat1 and flat0:
				# calculate intersection
				try:
					u, v = intersect(p0[0], p0[3], p1[0], p1[3])
				except NameError, e:
					raise e
				except:
					pass
				else:
					if 0.0 <= u <= 1.0 and 0.0 <= v <= 1.0:
						p = lerp(p0[0], p0[3], u)
						u = ua + (ub-ua)*u
						v = va + (vb-va)*v
						result.append((u, v, p))
				continue

			if not flat0 and not flat1:
				subdiv0 = ub-ua > vb-va
			elif not flat0:
				subdiv0 = True
			elif not flat1:
				subdiv0 = False

			if subdiv0:
				p00, p01 = split(p0, 0.5)
				uab = (ua + ub)/2
				queue.append(((p00, cbbox(*p00), ua, uab), P1))
				queue.append(((p01, cbbox(*p01), uab, ub), P1))
			else:
				p10, p11 = split(p1, 0.5)
				vab = (va + vb)/2
				queue.append((P0, (p10, cbbox(*p10), va, vab)))
				queue.append((P0, (p11, cbbox(*p11), vab, vb)))

		else:
			pass

	return result


def cl_intersections((A, B, C, D), (P0, P1), EPS=1e-10):
	"""
	Returns intersection points (parameters) of bezier
	curve A, B, C, D and line defined by point P0, P1
	"""

	# line equation:
	#     a*x + b*y + c = 0                    (1)
	a, b, c = line_equation(P0, P1)
	
	# curve equations:
	#     fx(t) = ax*t^3 + bx*t^2 + cx*t + dx  (2)
	#     fy(t) = ay*t^3 + by*t^2 + cy*t + dy  (3)
	(ax, bx, cx, dx), (ay, by, cy, dy) = eq_coefs(A, B, C, D)
	
	# after substitute 2 & 3 into 1:
	#     a*fx(t) + b*fy(t) + c = 0
	#     (a*ax + b*ay)t^3 + (a*bx + b*by)t^2 + (a*cx + b*cy)t + a*dx + b*dy + d = 0

	result = []
	for t in solve3(a*ax + b*ay, a*bx + b*by, a*cx + b*cy, a*dx + b*dy + d):
		if not zero(t.imag, EPS) or 0.0 < t.real or t.real > 1.0:
			continue
		else:	
			result.append(t.real)

	return result


def distance((A, B, C, D), P, n=64, EPS=1e-2):
	"""
	Returns parametr t of point that lie
	neareast to point P.

	n   - inital number of points
	EPS - tolerance
	
	Function performs some kind of binary search.
	"""
	def nearest(t0, t1):
		dt     = (t1-t0)/(n+1)
		best   = len_sqr(point((A, B, C, D), t0), P)
		best_t = t0

		for i in xrange(1, n):
			t = i*dt + t0
			l = len_sqr(point((A, B, C, D), t), P)
			if l < best:
				best   = l
				best_t = t

		return best_t
	
	t0 = 0.0
	t1 = 1.0
	while t1-t0 > EPS:
		t  = nearest(t1, t0)
		tc = (t0+t1)/2

		if t < tc:
			t1 = tc
		else:
			t0 = tc

		if n > 4:
			n /= 2
	
	return t


def length((A, B, C, D), t0=0.0, t1=1.0, EPS=1e-2):
	"""
	Returns length of piece of Bezier curve t \in [t0, t1].
	Calucations are done with some tolerance EPS.
	"""
	EPS2 = EPS**2.0

	def is_flat(A, B, C, D):
		return len_sqr(B, D) < EPS2
	
	if t1 < 1.0:
		(A, B, C, D), _ = split((A, B, C, D), t1)
	
	if t0 > 0.0:
		_, (A, B, C, D) = split((A, B, C, D), t0/t1)

	p   = [p for t, p in adaptive_split((A, B, C, D), is_flat)]
	len = 0.0
	p0  = p[0]
	for p1 in p[1:]:
		len += len_sqrt(p0, p1)
		p0   = p1
	
	return len


def zero(x, eps=1e-3):
	return abs(x) < eps

def equal(x1, x2, eps=1e-3):
	return abs(x1-x2) < eps

# vim: ts=4 sw=4 nowrap

