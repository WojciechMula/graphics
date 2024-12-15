# -*- coding: iso-8859-2 -*-
# Wojciech Muła, http://0x80.pl/
# $Date: 2007-03-04 22:37:37 $, $Revision: 1.2 $
#
# public domain



def fill_trapezium(x1,x2, x3,x4, y1,y2, color, skip_first=False):
	"""
	Fill trapezium defined by four points: (x1, y1), (x2, y1), (x3, y2), (x4, y4)
	"""
	dy  = y2-y1
	if dy == 0:
		return

	dxl = float(x3-x1)/dy
	dxr = float(x4-x2)/dy
	xl  = float(x1)
	xr  = float(x2)

	if (x1 != x2 and x1 > x2) or (x1 == x2 and dxl > dxr):
		dxl, dxr = dxr, dxl
		xl, xr   = xr, xl

	if skip_first: # skip first (bottom) scanline
		xl += dxl
		xr += dxr
		y1 += 1
		
	for y in xrange(y1, y2+1): # y \in [y1, y2]
		draw.line( [xl,y, xr,y], fill=color )
		xl += dxl
		xr += dxr


def fill_triangle((x0,y0), (x1,y1), (x2,y2), color):
	if y0 > y1:
		x0,x1 = x1,x0
		y0,y1 = y1,y0
	if y0 > y2:
		x0,x2 = x2,x0
		y0,y2 = y2,y0
	if y1 > y2:
		x1,x2 = x2,x1
		y1,y2 = y2,y1

	t   = float(y1-y0)/float(y2-y0)
	x11 = x0 + t*(x2-x0)
	x11 = int(x11)
	
	fill_trapezium(x0,x0, x1,x11, y0,y1, color)
	fill_trapezium(x1,x11, x2,x2, y1,y2, color, true)


def fill_quad(points, color=None):
	min = points[0][1]
	max = points[0][1]
	D   = 0 # top
	A   = 0 # bottom
	for i in xrange(1, 4):
		y = points[i][1]
		if y < min:
			min = y
			A = i
		if y > max:
			max = y
			D = i


	def X((xa,ya), (xb,yb), (x, y)):
		t = (y-ya)/float(yb-ya)
		return xa + t*(xb-xa)

	def circle(x,y,r):
		draw.ellipse([x-r,y-r, x+r,y+r])

	n = abs(A - D)

	if n == 1 or n == 3: # case I
		return

		BC = {
		# (A, D) -> (B, C)
		  (0, 1):   (3, 2),
		  (0, 3):   (1, 2),
		  (1, 0):   (2, 3),
		  (1, 2):   (0, 3),
		  (2, 1):   (3, 0),
		  (2, 3):   (1, 0),
		  (3, 0):   (2, 1),
		  (3, 2):   (0, 1),
		}

		B, C = CD[A, D]
		
		A = points[A]
		B = points[B]
		C = points[C]
		D = points[D]

		x_b  = B[0]
		x_c  = C[0]
		x_b1 = X(A, D, B)
		x_c1 = X(A, D, C)

		fill_trapezium(A[0], A[0], x_b, x_b1,   A[1], B[1], color or "#f00")
		fill_trapezium(x_b, x_b1,  x_c, x_c1,   B[1], C[1], color or "#0f0", True)
		fill_trapezium(x_c, x_c1,  D[0], D[0],  C[1], D[1], color or "#00f", True)
		
	else: # case II
		B = (D + 1) % 4
		C = (D - 1) % 4
		if points[B][1] > points[C][1]: # swap
			B, C = C, B
		
		A = points[A]
		B = points[B]
		C = points[C]
		D = points[D]

		x_b  = B[0]
		x_c  = C[0]
		x_b1 = X(A, C, B)
		x_c1 = X(B, D, C)

		fill_trapezium(A[0], A[0], x_b, x_b1,   A[1], B[1], color or "#00f")
		fill_trapezium(x_b, x_b1,  x_c1, x_c,   B[1], C[1], color or "#0f0", True)
		fill_trapezium(x_c, x_c1,  D[0], D[0],  C[1], D[1], color or "#f00", True)
				

if __name__ == '__main__':
	import Image, ImageDraw, ImageFont
	try:
		from isconvex import isconvex
	except ImportError:
		isconvex = lambda x: True
	
	w = 500
	h = 500
	image = Image.new("RGB", (w, h))
	draw  = ImageDraw.Draw(image)
	font  = ImageFont.load_default() 

	
	from random import randint, seed

	for k in xrange(20):
		
		draw.rectangle((0,0, w,h), fill="#333")

		while True:
			p = []
			for i in xrange(4):
				x = randint(0,w-1)
				y = randint(0,h-1)
				p.append( (x, y) )

			if isconvex(p):
				break

		fill_quad(p)

		draw.line(p+p[:1], fill="white")
#		fill_quad(p, "red")
#		for i, (x, y) in enumerate(p):
#			draw.text((x, y), str(i), font=font)

		image.save("fill-test%02d.bmp" % k, "BMP")

# vim: ts=4 sw=4 nowrap
