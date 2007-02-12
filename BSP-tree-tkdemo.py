import itertools
import string

import utils2D
import aabb2D
import tree_layout


class BSP_node(object):
	def __init__(self, A, B, value, letter):
		self.eq = utils2D.line_equation(A, B)
		self.A  = A
		self.B  = B
		self.left  = None
		self.right = None
		self.value = value

		# tree_layout releated methods/properties
		self.cx = 0.0
		self.cy = 0.0
		self.width  = 20.0
		self.letter = letter

	def side(self, (x, y)):
		a, b, c = self.eq
		return a*x + b*y + c
	
	# tree_layout releated methods/properties
	def __get_childNodes(self):
		return filter(bool, [self.left, self.right])
	childNodes = property(__get_childNodes)

	def hasChildNodes(self):
		return bool(self.left) or bool(self.right)

	def __get_firstChild(self):
		if self.left:
			return self.left
		else:
			return self.right
	firstChild = property(__get_firstChild)

	def __get_lastChild(self):
		if self.right:
			return self.right
		else:
			return self.left
	lastChild = property(__get_lastChild)

	
	def setminx(self, x):
		self.cx = x + self.width/2.0
	
	def maxx(self):
		return self.cx + self.width/2.0


def build_BSP(points, names):
	n = len(points)
	edges = []
	for i in xrange(n):
		e = BSP_node(points[i], points[(i + 1) % n], None, names.next())
		edges.append(e)

	def make_tree(edges):
		if not edges: return None

		l1 = []
		l2 = []
		root = edges.pop()
		for e in edges:
			s1 = root.side(e.A)
			s2 = root.side(e.B)
			if s1 * s2 > 0.0:
				if s1 > 0.0:
					l1.append(e)
				else:
					l2.append(e)
			elif s1 * s2 == 0.0:
				if s1 == 0.0:
					if s2 > 0.0:
						l1.append(e)
					else:
						l2.append(e)
				else:
					if s1 > 0.0:
						l1.append(e)
					else:
						l2.append(e)
			else:
				try:
					u = float(utils2D.intersect2(e.A, e.B, root.eq))
					if 0.0 <= u <= 1.0:
						C  = utils2D.lerp(e.A, e.B, u)
						e1 = BSP_node(e.A, C, None, names.next())
						e2 = BSP_node(C, e.B, None, names.next())
						e1.eq = e2.eq = e.eq

						if s1 >= 0.0:
							l1.append(e1)
							l2.append(e2)
						else:
							l1.append(e2)
							l2.append(e1)
					else:
						raise ValueError("impossible happend - crosspoint outside edge! %f" % u)
				except TypeError:
					raise ValueError("impossible happend - can't find crosspoints!")

		root.left  = make_tree(l1)
		if root.left is None:
			root.left = BSP_node((0.0, 0.0), (1.0, 0.0), True, 'in')

		root.right = make_tree(l2)
		if root.right is None:
			root.right = BSP_node((0.0, 0.0), (1.0, 0.0), False, 'out')

		return root
	
	return make_tree(edges)

def BSP_classify_point(root, P):
	assert root is not None

	node = root
	while node:
		if node.side(P) >= 0.0:
			inside = True
			node   = node.left
		else:
			inside = False
			node   = node.right

	return inside


CLICK1 = '<Button-1>'
CLICK2 = '<Button-3>'
MOTION = '<Motion>'

from random import randint
	
def see(canvas, (cx, cy)):
	cx = int(cx)
	cy = int(cy)

	xo = canvas.canvasx(0)
	yo = canvas.canvasy(0)
	w  = canvas.winfo_width()
	h  = canvas.winfo_height()
	
	canvas.scan_mark(int(cx), int(cy))
	canvas.scan_dragto(int(xo + w/2), int(yo + h/2), 1)

def bintree_walk(root, fun, level=0, param=None):
	if root is None:
		return

	bintree_walk(root.left,  fun, level+1, param)
	bintree_walk(root.right, fun, level+1, param)
	fun(root, level, param)

class BSP_Demo(object):
	def __init__(self, root):
		self.root = root
		self.canv = Tkinter.Canvas(root, bg="white")
		self.tree = Tkinter.Canvas(root, bg="#bbb")
		self.es = EventsSerializer('x', {self.canv: (CLICK1, CLICK2, MOTION)})

		self.random_points()

		def set_function(fun):
			def aux(): self.es.set_function(fun)
			return aux
		
		f = Tkinter.Frame(root)
		i = Tkinter.IntVar(root)
		i.set(0)
		Tkinter.Radiobutton(f, text="Split edge",   variable=i, value=1, command=set_function(self.split_edge)).pack()
		Tkinter.Radiobutton(f, text="Delete point", variable=i, value=2, command=set_function(self.delete_point)).pack()
		Tkinter.Radiobutton(f, text="Move point",   variable=i, value=3, command=set_function(self.move_point)).pack()
		Tkinter.Radiobutton(f, text="Chec point",   variable=i, value=4, command=set_function(self.check_point)).pack()
		Tkinter.Button(f, text="Random", command=self.random_points).pack()
		Tkinter.Button(f, text="Reverse", command=self.reverse_points).pack()
		Tkinter.Button(f, text="Rotate", command=self.rotate_points).pack()
		Tkinter.Button(f, text="Print", command=self.print_points).pack()

		f.pack(side=LEFT)
		self.canv.pack(side=TOP)
		self.tree.pack(side=TOP)
	
	def print_points(self):
		for x, y in self.points:
			print x, y,
		print
	
	def rotate_points(self):
		self.points = self.points[1:] + [self.points[0]]
		self.update()
	
	def reverse_points(self):
		self.points.reverse()
		self.update()
	
	def random_points(self):
		self.points = []
		for i in xrange(5):
			x = float(randint(0, 300))
			y = float(randint(0, 300))
			self.points.append( (x, y) )
		self.update()
	
	def click(self):
		"Return point after click (event CLICK2 acts like ABORT)"
		event = self.es.wait_event(CLICK1, {CLICK2: FunctionInterrupted})
		return (self.canv.canvasx(event.x),
		        self.canv.canvasy(event.y))

	def track_mouse(self):
		"Report mouse position (event CLICK2 is ignored)"
		for name, event in self.es.report_events([MOTION], [CLICK1]):
			yield (self.canv.canvasx(event.x),
		           self.canv.canvasy(event.y))


	def pick_point(self):
		while True:
			x, y = self.click()
			r    = 10.0**2

			for i, (xi, yi) in enumerate(self.points):
				dx = x - xi
				dy = y - yi
				d  = dx*dx + dy*dy
				if d < r:
					return i
		#elihw


	def split_edge(self):
		i = self.pick_point()
		j = (i + 1) % len(self.points)
		C = utils2D.lerp(self.points[i], self.points[j], 0.5)
		self.points.insert(j, C)
		self.update()


	def move_point(self):
		i = self.pick_point()
		for x, y in self.track_mouse():
			self.points[i] = (x, y)
			self.update()
	

	def delete_point(self):
		if len(self.points) > 3:
			del self.points[self.pick_point()]
			self.update()
	

	def check_point(self):
		names = itertools.cycle(string.lowercase)
		root = build_BSP(self.points, names)
		'''
		while True:
			if BSP_classify_point(root, self.click()):
				self.canv.itemconfig('P', outline="blue")
			else:
				self.canv.itemconfig('P', outline="red")
		'''
		tree_layout.TreeLayout2(root, 10.0)
		def make(node, level, extra):
			node.cy = level*40
			w = node.width/2
			i = self.tree.create_rectangle(node.cx - w, node.cy - w, node.cx + w, node.cy + w, fill="white", tags=('letter', node.letter))
			node.item = i
			if node.left:
				i = self.tree.create_line(node.cx, node.cy, node.left.cx, node.left.cy, tags='line')
			if node.right:
				i = self.tree.create_line(node.cx, node.cy, node.right.cx, node.right.cy, tags='line')
			self.tree.create_text(node.cx, node.cy, text=node.letter)

		self.tree.delete('all')
		bintree_walk(root, make)
		self.tree.tag_lower('line', 'all')
		x1,y1, x2,y2 = self.tree.bbox('all')
		see(self.tree, ((x1+x2)/2, (y1+y2)/2))

		colors = ["red", "green", "blue"]
		def make_edges(root, i):
			if root is None:
				return i+1

			item = self.canv.create_line(root.A[0], root.A[1], root.B[0], root.B[1])
			self.canv.itemconfig(item, fill=colors[i % 3], tags=('edge', 'tmp'))

			i = make_edges(root.left, i+1)
			i = make_edges(root.right, i)
			return i+1

		make_edges(root, 0)

		def make_line((xa, ya), (xb, yb)):
			return self.canv.create_line(xa, ya, xb, yb)

		while True:
			P    = self.click()
			self.canv.delete('edge')
			self.tree.itemconfig('letter', fill="white")
			node = root
			k = 0
			while node:
				s = node.side(P)
				
				item = make_line(
					utils2D.lerp(node.A, node.B,  10.0),
					utils2D.lerp(node.A, node.B, -10.0),
				)
				self.canv.itemconfig(item, tags=('edge', 'tmp'), dash=5)
				
				item = make_line(node.A, node.B)

				if s >= 0.0:
					self.canv.itemconfig(item, fill="blue", tags=('edge', 'tmp'))
					self.tree.itemconfig(node.letter, fill="blue")
				else:
					self.canv.itemconfig(item, fill="red", tags=('edge', 'tmp'))
					self.tree.itemconfig(node.letter, fill="red")
				
				D = utils2D.lerp(node.A, node.B, 0.5)
				#C = utils2D.set_length((node.eq[0], node.eq[1]), 20)
				C = utils2D.set_length((node.eq[0], node.eq[1]), 10)
				E = utils2D.add(D, C)
				#item = make_line(D, utils2D.add(D, C))
				#self.canv.itemconfig(item, tags=('edge', 'tmp'))
				item = self.canv.create_text(E[0], E[1], text=node.letter, tags=('edge', 'tmp'))
				
				
				prev = node
				if s >= 0.0:
					inside = True
					node = node.left
					if node.value is not None:
						inside = node.value
						self.tree.itemconfig(node.item, fill="blue")
						node = None
				else:
					inside = False
					node = node.right
					if node.value is not None:
						inside = node.value
						self.tree.itemconfig(node.item, fill="red")
						node = None

#				print " "*k, inside, node

				if not node:
					x1, y1 = utils2D.lerp(prev.A, prev.B, 0.5)
					x2, y2 = P
					self.canv.create_line(x1, y1, x2, y2, tags=('edge', 'tmp'))
				k += 1

#			print "Inside: %s" % inside
			if inside:
				self.canv.itemconfig('P', outline="blue")
			else:
				self.canv.itemconfig('P', outline="red")
		#elihw


	def update(self):
		p = []
		self.canv.delete('tmp')
		r = 4
		for x, y in self.points:
			p.append(x)
			p.append(y)
			o = self.canv.create_oval(x-r, y-r, x+r, y+r)
			self.canv.itemconfig(o, fill="#ccc", tags=('tmp', 'P'))

		
		l = self.canv.create_polygon(*p)
		self.canv.itemconfig(l, tags=("tmp", "L"), fill="", outline="black")
		self.canv.tag_lower(l, ALL)
		

import Tkinter
import sys
from Tkconstants import *
from tkes import EventsSerializerTk as EventsSerializer, FunctionInterrupted

if __name__ == '__main__':
	root = Tkinter.Tk()
	app  = BSP_Demo(root)
	if len(sys.argv) > 1:
		tmp = map(float, sys.argv[1:])
		app.points = zip(tmp, tmp[1:])[::2]
		app.update()

	root.mainloop()

# vim: ts=4 sw=4 nowrap
