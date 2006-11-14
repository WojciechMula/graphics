# -*- coding: iso-8859-2 -*-
# 2D AABB releated routines
# License: BSD
#
# Wojciech Muła
# wojciech_mula@poczta.onet.pl

# changelog
'''
11.11.2006:
	+ bb_points
	+ add_point
	+ add_bbox
	+ add_points
	+ point_inside
	+ bb_inside
	+ bb_crossing
'''

"""
AABB is a pair of points: left upper & right lower corner
"""

def bb_points(P):
	"""
	AABB of set of points (or polygon, polyline, etc.)
	"""
	minx = min(x for x, y in P)
	maxx = max(x for x, y in P)
	miny = min(y for x, y in P)
	maxy = max(y for x, y in P)

	return ((minx, miny), (maxx, maxy))


def add_point(((minx, miny), (maxx, maxy)), (x, y)):
	"""
	AABB of existing bounding box and point.
	"""
	if   x < minx: minx = x
	elif x > maxx: maxx = x
	
	if   y < miny: miny = y
	elif y > maxy: maxy = y

	return ((minx, miny), (maxx, maxy))


def add_bbox(BB, ((minx, miny), (maxx, maxy))):
	"""
	AABB of two bboxes
	"""
	BB = add_point(BB, (minx, miny))
	BB = add_point(BB, (maxx, maxy))
	return BB


def add_points(((minx, miny), (maxx, maxy)), P):
	"""
	AABB of existing bounding box and
	set of points (or polygon, polyline, etc.)
	"""
	BB = points(P)
	BB = add_point(BB, (minx, miny))
	BB = add_point(BB, (maxx, maxy))
	return BB


def point_inside(((minx, miny), (maxx, maxy)),  (x, y)):
	"""
	Returns True if point lie inside of AABB
	"""
	return minx <= x <= maxx and miny <= y <= maxy


def bb_inside(BB1, ((minx, miny), (maxx, maxy))):
	"""
	Returns True if BB2 lie inside BB1
	"""
	return p_inside(BB1, (minx, miny)) and p_inside(BB1, (maxx, maxy))

def bb_crossing(((minx1, miny1), (maxx1, maxy1)), ((minx2, miny2), (maxx2, maxy2))):
	"""
	Returns true if BB1 and BB2 are crossing
	"""
	return not (maxx2 < minx1 or minx2 > maxx1) and \
	       not (maxy2 < miny1 or miny2 > maxy1)

# vim: ts=4 sw=4 nowrap noexpandtab
