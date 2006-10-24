# -*- coding: iso-8859-2 -*-
# 
# A set of 2D geometry releated procedures.
#
# Wojciech Muła
# License: BSD

__changelog__ = """
24.10.2006
	- lerp1D, lerp, line_equation, intersect, intersect2
"""

def lerp1D(a, b, t):
	return a + (b-a)*t


def lerp((xa, ya), (xb, yb), t):
	return (xa + (xb-xa)*t, ya + (yb-ya)*t)


def line_equation((xa, ya), (xb, yb)):
	"""
	Function returns coefficients of line
	equation a*x + b*y + c = 0.  Line 
	goes over points A and B.
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

# vim: ts=4 sw=4 noexpandtabs nowrap
