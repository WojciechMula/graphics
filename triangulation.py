# -*- coding: iso-8859-2 -*-
# $Id: triangulation.py,v 1.1.1.1 2006-04-03 18:20:33 wojtek Exp $

def triangulate(vertex_list):
	"""
	Function triangulate polygon.
	
	Polygon is represened by vertex_list -- a list of pairs (x,y).

	Function returns list of triangles, where single triangle
	is a three integer -- idexes to vertex_list.

	Algorithm is very similar to well known triangulation of convex polygon:
	the single triangle is "cutted" from polygon and process continues since
	just one triangle left. In case of convex polygon it is simple, but
	for non-convex some additional tests are needed in order to cut correct
	triangles.
	"""
	triangle_list = []

	V = [((x,y), i) for i,(x,y) in enumerate(vertex_list)]

	while len(V) > 3:
		n = len(V)
		E = [(i, (i+1) % n) for i in xrange(n)]

		triangle_found = False
		for k in xrange(n):
			# Check triangle builded with vertices i,k,j
			
			i = (k-1) % n
			j = (k+1) % n

			# Edges builded with i,k and k,j already exists, but
			# edge i,k dosn't.
			x0,y0 = V[i][0]
			x1,y1 = V[j][0]

			# So first we simply check if certain point at the 'new'
			# edge lies inside polygon. If it is outside it means whole
			# edge is outside.
			x,y   = (x0+x1)/2, (y0+y1)/2
			if not point_in_polygon(x,y, V):
				continue

			# Otherwise we check if edge crosses other edges:
			some_intersection = False
			for a,b in E:
				if a==i or a==j or b==i or b==j:
					continue

				if intersection( V[i][0], V[j][0], V[a][0], V[b][0] ) != None:
					some_intersection = True
					break

			# If the edge doesn't cross any other, then we found
			# correct triangle. Triangle (i,j,k) is saved and removed
			# from polygon -- simply corner k is removed.
			if not some_intersection:
				i  = V[i][1]
				j  = V[j][1]
				k2 = V[k][1]
				V.pop(k)
				triangle_list.append( (i,k2,j) )
				triangle_found = True
				break

		assert triangle_found

	return triangle_list + [(V[0][1], V[1][1], V[2][1])]

def point_in_polygon(x,y, V):
	"""
	Function checks if point (x,y) lies inside polygon V. Polygon is
	given as list of vertices (pairs (x,y)).
	"""
	count	= 0
	n	= len(V)

	for i in xrange(n):
		count += edge_cross_halfline( (x,y), V[i][0], V[(i+1) % n][0]) 

	return (count%2) == 1

def edge_cross_halfline( (x,y), (x0,y0), (x1,y1) ):
	"""
	Function checks if a halfline (stared at point (x,y) and 
	parallel to X axis) crossing edge (x0,y0)-(x1,y1).

	Function returns 1 or 0.
	"""

	# ignore horizontal line
	if y1==y0:
		return 0
	
	# line is before halfline's start (can't cross halfline)
	if x0 < x and x1 < x:
		return 0

	# make sure that y0 < y1
	if y0 > y1:
		x0,y0, x1,y1 = x1,y1, x0,y0

	# line is above (can't cross halfline)
	if y0 < y and y1 <= y:
		return 0

	# line is below (can't cross halfline)
	if y0 > y and y1 > y:
		return 0

	# line crosses halfline
	if x0 >= x and x1 >= x:
		return 1
	else:
		t  = (y-y0)/float(y1-y0)
		xp = x0 + t*(x1-x0)      # yp=y
		if xp >= x:
			return 1
		else:
			return 0
	# eop


def intersection((xa,ya), (xb,yb), (xc,yc), (xd,yd)):
	"""
	Function returns intersection point of lines (xa,ya)-(xb,yb)
	and (xc,yc)-(xd,yd). Returns None if there is no intersection.
	
	"""

	# xa + u(xb-xa) = xc + v(xd-xc)
	# ya + u(yb-ya) = yc + v(yd-yc)
	# u \in [0,1]
	# v \in [0,1]
	a11 = float(xb-xa)
	a12 = float(xc-xd)
	a21 = float(yb-ya)
	a22 = float(yc-yd)
	b1  = float(xc-xa)
	b2  = float(yc-ya)

	detA = a11*a22-a12*a21
	if abs(detA) < 1e-8:
		return None
	
	detAu = b1*a22-a12*b2
	detAv = a11*b2-b1*a21

	u = detAu/detA
	if not (0.0 <= u <= 1.0):
		return None

	v = detAv/detA
	if not (0.0 <= v <= 1.0):
		return None
	
	return (xa+u*(xb-xa), ya+u*(yb-ya))


if __name__ == '__main__':
	import Image
	import ImageDraw
	from random import choice

	image = Image.new("RGB", (600, 600))
	draw  = ImageDraw.Draw(image)

	# some polygon I've drawn in Xfig (copy&paste from xfig files)
	poly1 = '3600 7200 1800 5850 3825 5400 1575 4275 3825 3600 4725 6300 6525 6300 3375 2475 675 4950 1575 1125 8100 2025 7650 6300 9000 7650 8550 4275 10575 8550 2025 7875'
	poly2 = '1800 1575 1800 3375 2700 2925 2250 2250 2925 2250 2925 4050 900 3825 1350 900 450 1350 450 5400 4275 5175 4050 2475 3375 3600 3375 1350 6525 5850 2025 6525 2700 9000 10800 7425 6525 450 2250 900'
	poly3 = '1575 900 2925 8100 4725 8100 5400 5625 6075 8100 7875 8100 9000 1125 7650 1125 6750 6750 6075 4050 4725 4050 3825 6975 2700 900'
	poly4 = '2025 1125 1125 2700 2475 1800 2475 1350 3375 3150 900 2925 1350 3825 675 3375 675 1800 1575 1125 1125 450 450 1575 225 3375 900 4500 1800 3600 2025 4725 450 5400 450 4275 0 6300 1350 7200 450 5850 1800 5625 2025 7650 450 7875 450 7200 225 7200 225 8550 3825 8325 2025 5175 4950 8325 2925 4725 4050 4950 4950 6750 5625 4950 6750 6975 5400 7200 4725 6975 5625 8550 4275 8775 8550 8550 8775 4725 6975 5625 6750 4050 4275 4950 6975 2475 7875 4275 9225 3825 9900 7200 11250 5625 10125 3600 8325 2925 9225 1350 10800 3375 11250 900 8100 675 7425 2475 5850 450 4500 3150 3600 1125 4275 3825 2700 675'
	poly5 = '4950 1800 2475 2250 1350 3600 2700 4950 3150 3150 3600 6075 1350 6075 1350 7200 5400 7200 4275 2700 5850 5175 7875 2925 3600 675'
	poly6 = '2250 1125 2250 7650 3150 7650 3150 4950 4950 7650 6075 7650 3825 4500 6300 1125 5175 1125 3150 4050 3150 1125'

	color = ['#f00', '#0f0', '#00f', '#f00', '#ff0', '#f0f', '#0ff']

	for index, coords in enumerate([poly1, poly2, poly3, poly4, poly5, poly6]):

		coords = map(lambda x: int(x)/20, coords.split())
		polygon = [(coords[i], coords[i+1]) for i in xrange(0, len(coords), 2)]

		draw.rectangle( (0,0,600,600), fill="#666" )

		for a,b,c in triangulate(polygon):
			draw.polygon( polygon[a]+polygon[b]+polygon[c], fill=choice(color) )
		
		draw.polygon(polygon)

		image.save("triang%d.bmp" % index, "BMP")
