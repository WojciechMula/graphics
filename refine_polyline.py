# -*- coding: iso-8859-2 -*-
# 
# Wojciech Muła, http://0x80.pl
# 26-27.02.2007
# public domain
# 
# $Date: 2007-02-27 18:42:26 $, $Revision: 1.2 $

def refine_polyline(points, dmax):
	n = len(points)
	if n < 3:
		return points
	
	result = []
	j = 0

	while j < n:
		flat = True
		k    = 2
		for k in xrange(2, n-j):
			# S
			x1, y1 = points[j]

			# E
			x2, y2 = points[j+k]
			
			# equation of line that passes through points S and E
			a = y2 - y1
			b = x1 - x2
			c = -(a*x1 + b*y1)
			D = sqrt(a*a + b*b)

			# Check if all vertices in range P[j+1..j+k-1]
			# lie at distance not greater then dmax from
			# the line
			flat = True
			for i in xrange(j+1, j+k):
				if abs(a*points[i][0] + b*points[i][1] + c)/D > dmax:
					flat = False
					break

			if flat:
				# flat, try advance k
				continue
			else:
				# not flat, use k from previous iteration and break
				k = k - 1
				break

		# save point S
		result.append(points[j])
		j = j + k
	#while

	return result


if __name__ == '__main__':

	from math import *
	from Tkinter import *

	root = Tk()
	canv = Canvas()
	canv.pack()

	def f(x):
		return 110-50*sin(x/10) + 10*cos(x/5) + 40*sin(x/16)

	def evaluate(fun, xmin, xmax, steps):
		dx = (xmax - xmin)/float(steps - 1)
		return [(i*dx, fun(i*dx)) for i in xrange(steps)]

	points  = evaluate(f, 0, 300, 2**10+1)
	maxd    = 0.5
	refined = refine_polyline(points, maxd)

	def flatten(points, dy=0.0):
		for x, y in points:
			y += dy
			#canv.create_oval(x-1, y-1, x+1, y+1, fill="#0f0")
			yield x
			yield y

	canv.create_line([v for v in flatten(points)])
	canv.create_line([v for v in flatten(refined, 00)], fill="red")
	print "samples count: %d, optimized: %d" % (len(points), len(refined))
	raw_input("<Enter>");
	#root.mainloop()

# vim: ts=4 sw=4 nowrap
