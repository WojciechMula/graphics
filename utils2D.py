# -*- coding: iso-8859-2 -*-
# 
# A set of 2D geometry releated procedures.
#
# Wojciech Muła
# License: BSD

# changelog
"""
23.11.2006
	+ len_manh
11.11.2006
	+ len_sqr
	+ length (len_sqrt)
	+ dotprod
	+ dotprod2
	+ neg
	+ add
	+ sub
	+ set_length
	+ set_length2
	+ triangle_height
24.10.2006
	+ lerp1D
	+ lerp
	+ line_equation
	+ intersect
	+ intersect2
"""

from math import sqrt, hypot
from isconvex import *

def lerp1D(a, b, t):
	return a + (b-a)*t


def lerp((xa, ya), (xb, yb), t):
	return (xa + (xb-xa)*t, ya + (yb-ya)*t)


def line_equation((xa, ya), (xb, yb)):
	"""
	Function returns coefficients of line
	equation a*x + b*y + c = 0.  Line 
	goes throught points A and B.
	"""

	dx = xb-xa
	dy = yb-ya

	a  =  dy
	b  = -dx
	c  = -(a*xa + b*ya)

	return (a, b, c)


def intersect((xa, ya), (xb, yb), (xc, yc), (xd, yd)):
	"""
	Function checks if two lines defined by points A-B and C-D
	have common point.

	Function solves system of equation:
		1. xa + (xb - xa) * u = xc + (xd - xc) * v
		2. ya + (yb - ya) * u = yc + (yd - yc) * v
	
	and returns u, v if solution exists, None othewise.

	a) If u, v exists then lines have common point.
	b) If 0 <= u <= 1 then line C-D and segment A-B have common point.
	c) If 0 <= v <= 1 then line A-B and segment C-D have common point.
	d) if both u and v lie in range [0, 1] then segments A-B and C-D
	   have common point.
	"""

	b1 = xc - xa
	b2 = yc - ya

	a11 =   xb - xa
	a12 = -(xd - xc)

	a21 =   yb - ya
	a22 = -(yd - yc)

	detA = a11*a22 - a21*a12
	
	if abs(detA) < 1e-7:
		return None
	
	detU = b1*a22 - b2*a12
	detV = a11*b2 - a21*b1

	u = detU/detA
	v = detV/detA

	return (u, v)

def intersect2((xa, ya), (xb, yb), (a, b, c)):
	"""
	Function checks if two lines have common points.
	First line is defined with points A and B
	(P(t) = A + t(B-A)), second line using equation
	a*x + b*y + c = 0.

	Function returns parametr t or None.
	"""

	D = a*(xb-xa) + b*(yb-ya)
	if abs(D) < 1e-8: return None
	
	N = a*xa + b*ya + c
	return -N/D


def len_manh((xa, ya), (xb, yb)):
	return abs(xa-xb) + abs(ya-yb)


def len_sqr((xa, ya), (xb, yb)):
	"""
	Returns |AB|^2
	"""
	dx = xa - xb
	dy = ya - yb
	return dx*dx + dy*dy


def length((xa, ya), (xb, yb)):
	"Returns length of segment: |AB|"
	return hypot(xa-xb, ya-yb)

len_sqrt = length # alias

def neg(x, y):
	"Returns -V"
	return (-x, -y)


def add((xa, ya), (xb, yb)):
	"Returns A+B"
	return (xa+xb, ya+yb)


def sub((xa, ya), (xb, yb)):
	"Returns A-B"
	return (xa-xb, ya-yb)


def set_length((xa, ya), length):
	"Returns vec length*A/|A|"
	l = sqrt(xa*xa + ya*ya)
	if zero(l, 1e-10):
		return (0.0, 0.0)
	else:
		return (length*xa/l, length*ya/l)

def set_length2(A, B, length):
	"Returns vec A + length*(B-A)/|BA|"
	D = set_length(sub(A, B), length)
	return add(A, D)


def dotprod((xa, ya), (xb, yb)):
	"""
	Returns dot product: A.B
	"""
	return xa*xb + ya*yb


def dotprod2((xa, ya), (xb, yb), (xc, yc)):
	"""
	Returns dot product: (B-A).(C-A)
	"""
	return (xb-xa)*(xc-xa) + (yb-ya)*(yc-ya)

def triangle_height(A, B, C):
	"Returns height of triangle ABC at point B"
	
	l2 = len_sqr(A, B)
	if zero(l, 1e-10):
		return 0.0
	else:
		l = sqrt(l2)
		d = dotprod2(A, B, C)/l
		return sqrt(abs(l2 - d))

def equal(a, b, EPS=1e-10):
	return abs(a-b) < EPS

def zero(x, EPS=1e-10):
	return abs(x) < EPS

# vim: ts=4 sw=4 noexpandtab nowrap
