from math import sin, cos, pi

def arc_bbox(x0, y0, rx, ry, start=0.0, end=2*pi, rot=0.0):
	cr = cos(rot)
	sr = sin(rot)

	def P(a):
		x = sin(a)*rx
		y = cos(a)*ry
		return (x*cr - y*sr, x*sr + y*cr)
	
	def avg((xa,ya), (xb,yb)):
		return ((xa+xb)/2, (ya+yb)/2)
	
	def dist2((xa,ya), (xb,yb)):
		dx = xa-xb
		dy = ya-yb
		return dx*dx + dy*dy
		
	if rot == 0.0:
		angles = [0.0, math.pi/2, math.pi, 3*math.pi/2]

	else:
		k   = 65
		da  = 2*pi/(k-1)
		pts = [P(i*da) for i in xrange(k)]
		
		arcs = []
		for i in xrange(k-1):
			a1 = i*da
			a2 = (i+1)*da
			p1 = pts[i]
			p2 = pts[i+1]

			arcs.append( (a1,p1, a2,p2) )

		def locate_extremum(initial, cmp, min_d=0.001):
			min_d = min_d * min_d
			queue = initial[:]
			while queue:
				if len(queue) == 1:
					(a1, p1, a2, p2) = item = queue.pop()
					aa = (a1+a2)/2
					pa = P(aa)
					if dist2(pa, avg(p1, p2)) <= min_d:
						return aa

					if cmp(avg(p1,pa), avg(pa,p2)):
						queue.append((a1, p1, aa, pa))
					else:
						queue.append((aa, pa, a2, p2))

				else:
					(a10, p10, a20, p20) = item0 = queue.pop()
					(a11, p11, a21, p21) = item1 = queue.pop()
					if cmp(avg(p10,p20), avg(p11,p21)):
						queue.append(item0)
					else:
						queue.append(item1)

		a1 = locate_extremum(arcs, lambda (x1,y1),(x2,y2): x1 > x2)
		a2 = locate_extremum(arcs, lambda (x1,y1),(x2,y2): y1 > y2)
		angles = [a1, a1+pi, a2, a2+pi]
	#endif
	
	X = [P(start)[0], P(end)[0]]
	Y = [P(start)[1], P(end)[1]]
	import sys
	if end > 2*pi:
		start -= 2*pi
		end   -= 2*pi
	for a in angles:
		if a > end:
			a -= 2*pi
		sys.stderr.write("%s <= %s <= %s\n" % (start, a, end))
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
		x = sin(a)*rx
		y = cos(a)*ry
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
