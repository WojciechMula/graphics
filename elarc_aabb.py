from math import sin, cos, sqrt, pi, atan, atan2
import sys

def ellipse_aabb(a, b, rot=0.0):
	dx = sin(rot)
	dy = cos(rot)
	return atan2(dy*b/a, dx), atan2(-dx*b/a, dy)


def arc_bbox(x0, y0, rx, ry, start=0.0, end=2*pi, rot=0.0):
	cr = cos(rot)
	sr = sin(rot)

	def P(a):
		x = cos(a)*rx
		y = sin(a)*ry
		return (x*cr - y*sr, x*sr + y*cr)
	
	a1, a2 = ellipse_aabb(rx, ry, rot)
	angles = [a1, a2, a1+pi, a2+pi]
	
	X = [P(start)[0], P(end)[0]]
	Y = [P(start)[1], P(end)[1]]
	
	if end > 2*pi:
		start -= 2*pi
		end   -= 2*pi

	for a in angles:
		if a > end:
			a -= 2*pi
		
		x, y = P(a)
		color = "red"
		if start <= a <= end:
			X.append(x)
			Y.append(y)
			color = "blue"
		print '<circle cx="%f" cy="%f" r="2" fill="%s" stroke="%s"/>' % (x0+x, y0+y, color, color)

	return (min(X), min(Y)), (max(X), max(Y))

head = """<?xml version="1.0" ?>
<!DOCTYPE svg  PUBLIC '-//W3C//DTD SVG 1.1//EN' 'http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd'>
<svg height="400" width="400" xmlns="http://www.w3.org/2000/svg">
"""

tail = "</svg>"

def arc_points(x0, y0, rx, ry, start, end, rot):
	cr = cos(rot)
	sr = sin(rot)

	def P(a):
		x = cos(a)*rx
		y = sin(a)*ry
		return (x*cr - y*sr, x*sr + y*cr)
	
	n  = 360/8
	da = (end-start)/(n-1)
	d  = []
	for i in xrange(n):
		a    = start + i*da
		x, y = P(a)
		d.append(x+x0)
		d.append(y+y0)
	return ' '.join(map(str, d))

from random import random

print head
for i in xrange(10):
	x = random()*400
	y = random()*400
#	x = 200
#	y = 200
	rx = (0.1+random())*80
	ry = (0.1+random())*80
	# XXX
	#ry = rx
	start = random()*2*pi
	end   = start + random()*2*pi
	rot   = random()*2*pi

	(xmin, ymin), (xmax, ymax) = arc_bbox(x, y, rx, ry, start, end, rot)
	xmin += x
	xmax += x
	ymin += y
	ymax += y

	print '<rect x="%0.2f" y="%0.2f" width="%0.2f" height="%0.2f" fill="none" stroke="red" stroke-width="0.5"/>' % (xmin, ymin, xmax-xmin, ymax-ymin)

	print '<polyline points="%s" fill="none" stroke="#aaa"/>' % arc_points(x, y, rx, ry, 0, 2*pi, rot)
	print '<polyline points="%s" fill="none" stroke="#000"/>' % arc_points(x, y, rx, ry, start, end, rot)
print tail

# vim: ts=4 sw=4 nowrap
