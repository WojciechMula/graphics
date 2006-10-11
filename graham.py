def graham(points):
	n = len(points)
	if n < 3:
		return points

	# calcuate centroid
	cx  = sum(x for x,y in points)/float(n)
	cy  = sum(y for x,y in points)/float(n)

	drawing.circle((cx,cy), 5)

	# move points by vecotr -cx,-cy
	tmp = [(x-cx, y-cy, i) for i, (x, y) in enumerate(points)]

	# sort them lexicographically
	def alpha( (x, y, i) ):
		d = float(abs(x) + abs(y))
		if x >= 0 and y >= 0:	return y/d
		if x <= 0 and y >= 0:	return 2.0 - y/d
		if x <= 0 and y <= 0:	return 2.0 - y/d
		if x >= 0 and y <= 0:	return 4.0 + y/d
	
	tmp.sort(key=alpha)

	# get a on convex hull - point that has min x
	imin = 0
	for i, (x, _, _) in enumerate(tmp):
		if x < tmp[imin]:
			imin = i
	
	tmp = tmp[imin:] + tmp[:imin]


	# find convex hull

	file = 0

	ai = 0
	while ai < n:
		drawing.clear_drawing()
		for x,y in points:
			drawing.circle((x,y), 4)
		if n == 3:
			break

		bi = (ai + 1) % n
		ci = (bi + 1) % n

		a = tmp[ai]
		b = tmp[bi]
		c = tmp[ci]
		det = -(c[1]-a[1]) * (b[0]-a[0]) + (c[0]-a[0]) * (b[1]-a[1])

		
		pp = [(x+cx, y+cy) for x,y,i in tmp[:ai+1]]
		if pp:
			drawing.polyline(pp, style='tested')
		drawing.line((cx+a[0],cy+a[1]), (cx+c[0],cy+c[1]))

		if det > 0:
			drawing.line((cx+a[0],cy+a[1]), (cx+b[0],cy+b[1]), style='rejected')
			drawing.circle((cx+b[0],cy+b[1]), 3, style='rejected')
		else:
			drawing.line((cx+a[0],cy+a[1]), (cx+b[0],cy+b[1]), style='accepted')
			drawing.circle((cx+b[0],cy+b[1]), 3, style='accepted')

		drawing.save('tmp%02d.svg' % file, prettyXML=True)
		file += 1
			
		if det > 0:
			tmp.pop(bi)
			n = n - 1
			if ai > 0:
				ai = ai - 1
		else:
			ai = ai + 1


	return [i for (x,y,i) in tmp]

if __name__ == '__main__':
	import random

	from random import randint
	from SVG    import SVGDrawing

	class Dummy: pass
	options = Dummy()

	margin = 5
	
	options.n = 8
	options.s = 300

	drawing = SVGDrawing(options.s + 2*margin, options.s + 2*margin)
	drawing.dx = margin
	drawing.dy = margin
	drawing.new_layer('default')
	drawing.new_style('!circle',	('fill', 'black'))
	drawing.new_style('tested', 	('stroke', '#aaa'), ('fill', 'none'))
	drawing.new_style('rejected',	('stroke', 'red'), ('fill', 'red'), ('stroke-width', '2'))
	drawing.new_style('accepted',	('stroke', 'blue'), ('fill', 'blue'))
	drawing.new_style('default',	('stroke', 'black'))

	def point():
		return (random.randint(0, options.s),
		        random.randint(0, options.s))

	random.seed(20)
	points  = [point() for i in xrange(options.n)]
	for x,y in points:
		drawing.circle((x,y), 4)

	indexes = graham(points)
	#drawing.polygon([points[i] for i in indexes])

	#drawing.save('graham.svg', prettyXML=True)
