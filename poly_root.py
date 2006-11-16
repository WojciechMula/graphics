# -*- coding: iso-8859-2 -*-
#
# Roots of polynomials
#
# License: BSD
#
# Wojciech Muła
# wojciech_mula@poczta.onet.pl

# changelog
'''
11.10.2006:
	+ solve1
8-10.11.2006:
	+ solve3
	+ solve2
'''

from cmath import *

def solve1(a, b):
	"""
	Returns root of equation a*x + b = 0.
	"""
	# a*x + b = 0
	if zero(a, 1e-6):
		return ()
	else:
		return (complex(-b/a),)

def solve2(a, b, c):
	"""
	Returns all roots (real and complex)
	of equation a*x^2 + b*x^1 + c = 0.
	"""

	if zero(a, 1e-6):
		return solve1(b, c)
	else:
		d  = sqrt(b*b - 4*a*c)
		x1 = (-b - d)/(2*a)
		x2 = (-b + d)/(2*a)
		return (x1, x2)

def solve3(a, b, c, d):
	"""
	Returns all roots (real and complex)
	of equation a*x^3 + b*x^2 + c*x + d = 0.
	"""
	a  = float(a)
	b  = float(b)
	c  = float(c)
	d  = float(d)
	if zero(a, 1e6):
		return solve2(b, c, d)

	p  = 1.0/3.0 * (3*a*c - b*b)/(3*a*a)
	q  = 1.0/2.0 * ((2*b*b*b)/(27*a*a*a) - (b*c)/(3*a*a) + d/a)
	z  = -b/(3*a)
		
	if q >= 0.0:
		r = +sqrt(abs(p))
	else:
		r = -sqrt(abs(p))
	
	r3 = r*r*r

	if p < 0.0:
		if q*q + p*p*p <= 0.0:
			fi = acos(q/r3)

			y1 = -2*r*cos(fi/3)
			y2 = +2*r*cos(pi/3 - fi/3)
			y3 = +2*r*cos(pi/3 + fi/3)
		else:
			fi = acosh(q/r3)

			y1 = -2*r*cosh(fi/3)
			y2 =    r*cosh(fi/3) + 1j*sqrt(3)*r*sinh(fi/3)
			y3 =    r*cosh(fi/3) - 1j*sqrt(3)*r*sinh(fi/3)
			
	else: # p >= 0.0
		fi = asinh(q/r3)
		y1 = -2*r*sinh(fi/3)
		y2 =    r*sinh(fi/3) + 1j*sqrt(3)*r*cosh(fi/3)
		y3 =    r*sinh(fi/3) - 1j*sqrt(3)*r*cosh(fi/3)

	return (y1+z, y2+z, y3+z)

def sq3(x):
	if x > 0.0:
		return x**(1.0/3.0)
	else:
		return -(-x)**(1.0/3.0)

def zero(x, eps):
	return abs(x) < eps

# vim: ts=4 sw=4 nowrap
