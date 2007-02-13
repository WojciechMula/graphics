import itertools
import string

import utils2D
import aabb2D


class BSP_node(object):
	def __init__(self, A, B, leaf):
		self.eq = utils2D.line_equation(A, B)
		self.A  = A
		self.B  = B
		self.left  = None
		self.right = None
		self.leaf  = leaf

	def side(self, (x, y)):
		a, b, c = self.eq
		return a*x + b*y + c


def build_BSP(points):
	n = len(points)
	edges = []
	for i in xrange(n):
		e = BSP_node(points[i], points[(i + 1) % n], None)
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
						e1 = BSP_node(e.A, C, None)
						e2 = BSP_node(C, e.B, None)
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
			root.left = BSP_node((0.0, 0.0), (1.0, 0.0), True)

		root.right = make_tree(l2)
		if root.right is None:
			root.right = BSP_node((0.0, 0.0), (1.0, 0.0), False)

		return root
	
	return make_tree(edges)

def BSP_classify_point(root, P):
	assert root is not None

	node = root
	while node:
		inside = node.leaf

		if node.side(P) >= 0.0:
			node   = node.left
		else:
			node   = node.right

	return inside

######################################################################

def BinaryTreeLayout(root, space, x=0.0):
	if root is None:
		return x
	
	root.width = 20
	
	x = BinaryTreeLayout(root.left,  space, x)
	x = BinaryTreeLayout(root.right, space, x+space)

	if root.left and root.right:
		root.cx = (root.left.cx + root.right.cx)/2
	elif root.left:
		root.cx = roo.left.cx
	elif root.right:
		root.cx = roo.right.cx
	else:
		root.cx    = x
		return root.cx + root.width/2

	return x
	

######################################################################

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



class BSP_Demo(object):
	def __init__(self, root):
		self.root = root
		
		f1 = Tkinter.Frame(root)
		self.canv = Tkinter.Canvas(f1, bg="white")
		self.tree = Tkinter.Canvas(f1, bg="#bbb")
		self.es = EventsSerializer('ABORT', {self.canv: (CLICK1, CLICK2, MOTION)})

		self.show_labels = Tkinter.BooleanVar()
		self.mark_edges  = Tkinter.BooleanVar()
		self.show_lines  = Tkinter.BooleanVar()

		self.show_labels.set(True)
		self.mark_edges. set(True)
		self.show_lines. set(True)

		self.random_points()

		def set_function(fun):
			def aux(): self.es.set_function(fun)
			return aux
		
		f = Tkinter.Frame(root)
		i = Tkinter.IntVar(root)
		i.set(0)
		Tkinter.Radiobutton(f, text="Split edge",   variable=i, value=1, command=set_function(self.split_edge)).pack(anchor='w')
		Tkinter.Radiobutton(f, text="Delete point", variable=i, value=2, command=set_function(self.delete_point)).pack(anchor='w')
		Tkinter.Radiobutton(f, text="Move point",   variable=i, value=3, command=set_function(self.move_point)).pack(anchor='w')
		Tkinter.Radiobutton(f, text="Chec point",   variable=i, value=4, command=set_function(self.check_point)).pack(anchor='w')
		Tkinter.Button(f, text="Flip normals",  command=self.flip_normals).pack(fill='x')
		Tkinter.Button(f, text="Random points", command=self.random_points).pack(fill='x')
		Tkinter.Button(f, text="Print", command=self.print_points).pack(fill='x')

		Tkinter.Checkbutton(f, text="Highl. edges", variable=self.mark_edges).pack(anchor='w')
		Tkinter.Checkbutton(f, text="Show labels",  variable=self.show_labels).pack(anchor='w')
		Tkinter.Checkbutton(f, text="Show lines",   variable=self.show_lines).pack(anchor='w')

		f.pack(side=LEFT, anchor='n')
		f1.pack(side=LEFT)
		self.canv.pack(side=TOP, fill='x', expand=1)
		self.tree.pack(side=TOP, fill='x', expand=1)


	def print_points(self):
		"prints on stdout polygon's vertices"
		for x, y in self.points:
			print x, y,
		print
	
	def flip_normals(self):
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
		#while


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
		root = build_BSP(self.points)
		
		BinaryTreeLayout(root, 10.0)
		def prepare(node, level, names):
			if node is None:
				return

			if node.leaf is True:
				node.name = 'in'
			elif node.leaf is False:
				node.name = 'out'
			else:
				node.name = names.next()

			node.cy = level*40
			w       = node.width/2

			node.item = self.tree.create_rectangle(node.cx - w, node.cy - w, node.cx + w, node.cy + w, fill="white", tags=('name', node.name))
			self.tree.create_text(node.cx, node.cy, text=node.name)

			node.edge = self.canv.create_line(node.A[0], node.A[1], node.B[0], node.B[1], state="hidden", tags=("tmp", "edge"), width=2)
			a, b, c = node.eq
			x, y = utils2D.add(
					utils2D.lerp(node.A, node.B, 0.5),	# edge center
					utils2D.set_length((a, b), 10.0)	# normal
			)
			node.label = self.canv.create_text(x, y, text=node.name, state="hidden", tags=("tmp"))
			
			prepare(node.left, level+1, names)
			prepare(node.right, level+1, names)
			
			if node.left:
				self.tree.create_line(node.cx, node.cy, node.left.cx, node.left.cy, tags='line')
			if node.right:
				self.tree.create_line(node.cx, node.cy, node.right.cx, node.right.cy, tags='line')
		#def


		self.tree.delete('all')
		self.canv.delete('tmp')
		prepare(root, 0, names)
		self.tree.tag_lower('line', 'all')
		x1,y1, x2,y2 = self.tree.bbox('all')
		see(self.tree, ((x1+x2)/2, (y1+y2)/2))


		while True:
			P = self.click()

			# remove all temporary objects
			self.canv.delete('del')
			self.canv.itemconfig('tmp', state="hidden")
		
			# unmark tree view
			self.tree.itemconfig('name', fill="white")
			
			node   = root
			inside = None
			while True:
				s = node.side(P)

				if self.show_lines.get():
					A1 = utils2D.lerp(node.A, node.B, 20.0)
					B1 = utils2D.lerp(node.B, node.A, 20.0)
					self.canv.create_line(A1[0], A1[1], B1[0], B1[1], tags='del', dash=5)
					
				if self.show_labels.get():
					self.canv.itemconfig(node.label, state="")

				inside = node.leaf
				if inside is not None:
					break

				if s >= 0.0:
					self.tree.itemconfig(node.item, fill="blue")
					if self.mark_edges.get():
						self.canv.itemconfig(node.edge, fill="blue", state="")

					node = node.left
				else:
					self.tree.itemconfig(node.item, fill="red")
					if self.mark_edges.get():
						self.canv.itemconfig(node.edge, fill="red", state="")

					node = node.right

			if inside:
				self.tree.itemconfig(node.item, fill="blue")
				self.canv.itemconfig('P', outline="blue")
			else:
				self.tree.itemconfig(node.item, fill="red")
				self.canv.itemconfig('P', outline="red")
		#while


	def update(self):
		p = []
		self.canv.delete('all')
		r = 4
		for x, y in self.points:
			p.append(x)
			p.append(y)
			o = self.canv.create_oval(x-r, y-r, x+r, y+r)
			self.canv.itemconfig(o, fill="#ccc", tags='P')

		
		l = self.canv.create_polygon(*p)
		self.canv.itemconfig(l, tags="L", fill="", outline="black")
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
