import Tkinter
import tkSimpleDialog

from Tkconstants import *
from tkes        import EventsSerializerTk as EventsSerializer, FunctionInterrupted
from tree_layout import TreeLayout2, TreeLayout

class Node(object):
	def __init__(self):
		self.parentNode  = None
		self.childNodes  = []

	def hasChildNodes(self):
		return bool(self.childNodes)
	
	def _get_lastChild(self):
		try:
			return self.childNodes[-1]
		except IndexError:
			return None
	
	def _get_firstChild(self):
		try:
			return self.childNodes[0]
		except IndexError:
			return None
	
	firstChild = property(_get_firstChild)
	lastChild  = property(_get_lastChild)
	
	def appendChild(self, node):
		if node.parentNode:
			raise ValueError("Node already binded to the tree")
		node.parentNode = self
		self.childNodes.append(node)
	
	def insertChild(self, node, newnode):
		try:
			index = self.childNodes.index(node)
		except IndexError:
			pass

		self.childNodes.insert(index, newnode)
		newnode.parentNode = self

	def removeChild(self, node):
		try:
			index = self.childNodes.index(node)
		except IndexError:
			pass

		node.parentNode = None
		self.childNodes.pop(index)
		return node
	
	def replaceChild(self, node, newnode):
		try:
			index = self.childNodes.index(node)
		except IndexError:
			pass

		node	.parentNode = None
		newnode	.parentNode = self
		self.childNodes[index] = newnode
		return node


class Shape(Node):
	def __init__(self, canvas, id, text, bg='white'):
		Node.__init__(self)
		self.cx      = 0
		self.cy      = 0
		self.id      = 'node%d' % id
		self.canvas  = canvas
		self.text    = canvas.create_text(0, 0, text=text, tags=self.id)
		self.__title = text
	
	def __get_title(self):
		return self.__title

	def __set_title(self, title):
		self.__title = title
		self.canvas.itemconfigure(self.text, text=title)
		self.update_view()
	
	title = property(__get_title, __set_title)
	
	def setminx(self, minx):
		self.cx = minx + self.width/2
	
	def maxx(self):
		return self.cx + self.width/2
	
	def destroy(self):
		self.canvas.delete(self.id)


class Rectangle(Shape):
	def __init__(self, canvas, id, text, bg='white'):
		Node.__init__(self)
		Shape.__init__(self, canvas, id, text, bg=bg)
		self.shape  = canvas.create_rectangle(
			0, 0,
			100, 100,
			fill=bg,
			tags=self.id
		)

		self.update_view()
	
	def update_view(self):
		self.canvas.coords(self.text, self.cx, self.cy)
		self.canvas.tag_raise(self.text, self.shape)
		x1, y1, x2, y2 = self.canvas.bbox(self.text)
		m = 5
		self.canvas.coords(self.shape, x1-m, y1-m, x2+m, y2+m)
		self.width  = x2-x1 + 2*m
		self.height = y2-y1 + 2*m
		
		self.canvas.delete('%s && tmp' % self.id)
		xo = self.cx
		yo = self.cy
		for child in self.childNodes:
			l = self.canvas.create_line(xo, yo, child.cx, child.cy, tags=(self.id, 'tmp'), state='disabled')
		self.canvas.tag_lower('%s && tmp' % self.id, 'all')


class RoundedRect(Shape):
	def __init__(self, canvas, id, text, bg='white'):
		Node.__init__(self)
		Shape.__init__(self, canvas, id, text, bg=bg)
		self.m = 8

		def arc(start):
			return canvas.create_arc(
				0, 0, 0, 0,
				start	= start,
				extent	= 90,
				fill	= bg,
				outline	= '',
				tags	= self.id
			)

		self.corner1f = arc(90)
		self.corner2f = arc(0)
		self.corner3f = arc(270)
		self.corner4f = arc(180)
		
		def arc(start):
			return canvas.create_arc(
				0, 0, 0, 0,
				start	= start,
				extent	= 90,
				style	= ARC,
				tags	= self.id
			)
		self.corner1 = arc(90)
		self.corner2 = arc(0)
		self.corner3 = arc(270)
		self.corner4 = arc(180)
		
		self.rect1 = canvas.create_rectangle(0, 0, 100, 100, fill=bg, outline='', tags=self.id)
		self.rect2 = canvas.create_rectangle(0, 0, 100, 100, fill=bg, outline='', tags=self.id)
		
		self.line1 = canvas.create_line(0, 0, 100, 100, tags=self.id)
		self.line2 = canvas.create_line(0, 0, 100, 100, tags=self.id)
		self.line3 = canvas.create_line(0, 0, 100, 100, tags=self.id)
		self.line4 = canvas.create_line(0, 0, 100, 100, tags=self.id)

		self.update_view()
	
	def update_view(self):
		self.canvas.coords(self.text, self.cx, self.cy)
		self.canvas.tag_raise(self.text, self.line4)
		x1, y1, x2, y2 = self.canvas.bbox(self.text)
		m = self.m

		coords = self.canvas.coords

		coords(self.rect1, x1-m, y1, x2+m, y2)
		coords(self.rect2, x1, y1-m, x2, y2+m)

		coords(self.line1, x1, y1-m, x2, y1-m)
		coords(self.line2, x1, y2+m, x2, y2+m)
		coords(self.line3, x1-m, y1, x1-m, y2)
		coords(self.line4, x2+m, y1, x2+m, y2)

		coords(self.corner1, x1-m, y1-m, x1+m, y1+m)
		coords(self.corner2, x2-m, y1-m, x2+m, y1+m)
		coords(self.corner3, x2-m, y2-m, x2+m, y2+m)
		coords(self.corner4, x1-m, y2-m, x1+m, y2+m)
		coords(self.corner1f, x1-m, y1-m, x1+m, y1+m)
		coords(self.corner2f, x2-m, y1-m, x2+m, y1+m)
		coords(self.corner3f, x2-m, y2-m, x2+m, y2+m)
		coords(self.corner4f, x1-m, y2-m, x1+m, y2+m)
		self.width  = x2-x1 + 2*m
		self.height = y2-y1 + 2*m
		
		self.canvas.delete('%s && tmp' % self.id)
		xo = self.cx
		yo = self.cy
		for child in self.childNodes:
			l = self.canvas.create_line(xo, yo, child.cx, child.cy, tags=(self.id, 'tmp'), state='disabled')
		self.canvas.tag_lower('%s && tmp' % self.id, 'all')
	

class Circle(Shape):
	def __init__(self, canvas, id, text, bg='white'):
		Node.__init__(self)
		Shape.__init__(self, canvas, id, text, bg=bg)
		self.shape  = canvas.create_oval(0, 0, 100, 100, fill=bg, tags=self.id)

		self.update_view()
	
	def update_view(self):
		self.canvas.coords(self.text, self.cx, self.cy)
		self.canvas.tag_raise(self.text, self.shape)
		x1, y1, x2, y2 = self.canvas.bbox(self.text)
		m = 5
		r = 0.75*max(x2-x1, y2-y1)
		self.canvas.coords(self.shape, self.cx-r, self.cy-r, self.cx+r, self.cy+r)
		self.width  = 2*r
		self.height = 2*r
		
		self.canvas.delete('%s && tmp' % self.id)
		xo = self.cx
		yo = self.cy
		for child in self.childNodes:
			l = self.canvas.create_line(xo, yo, child.cx, child.cy, tags=(self.id, 'tmp'), state='disabled')
		self.canvas.tag_lower('%s && tmp' % self.id, 'all')
	

CLICK    = '<Button-1>'

class TreeLayoutDemo(object):
	def __init__(self, master):
		self.create_ui(master)
		self.space = 5.0
		self.root  = None
		self.nodes = {}
		self.nodes_serial = 0

		self.es  = EventsSerializer(0, {self.canvas: [CLICK]})
		self.function.set('append')
	
	def update(self, *ignored):
		if self.root is None:
			return
		
		if self.method.get():
			TreeLayout2(self.root, self.space)
		else:
			TreeLayout(self.root, 0.0, self.space)
	
		for node in self.nodes.itervalues():
			node.update_view()
		
		canv = self.canvas
		canv.delete('tmp')

		canv['scrollregion'] = x1, y1, x2, y2 = canv.bbox(ALL)

		w = canv.winfo_width()
		h = canv.winfo_height()
		if x2-x1 < w and y2-y1 < h:
			dx = -x1 + (w - (x2-x1))/2
			dy = -y1 + (h - (y2-y1))/2
		else:
			dx = dy = 0

		for node in self.nodes.itervalues():
			node.cx += dx
			node.cy += dy

		for node in self.nodes.itervalues():
			node.update_view()


	def pick_node(self, raiseexception=True):
		event = self.es.wait_event(CLICK)
		try:
			item = self.canvas.find_withtag(CURRENT)[0]
			id   = self.canvas.gettags(item)[0]
			return self.nodes[id]
		except IndexError:
			if raiseexception:
				raise FunctionInterrupted
			else:
				return None


	def new_node(self, text=None):
		shape  = self.shape.get()
		if   shape == 'rect':	Class = Rectangle
		elif shape == 'circ':	Class = Circle
		elif shape == 'rrect':	Class = RoundedRect
		else:
			raise ValueError('unknown shape')
		
		id  = self.nodes_serial
		if text is None:
			text = ('node%d' % id)

		new = Class(
					self.canvas,
					id,
					text=text,
					bg=self.background.color
		)
		self.nodes[new.id] = new
		self.nodes_serial += 1
		return new


	def append_child(self):
		node = self.pick_node(False)
		if node is None:
			if self.root is None:
				self.root = self.new_node()
				self.update()
			return

		new    = self.new_node()
		new.cy = node.cy + 50

		node.appendChild(new)
		self.update()


	def delete_subtree(self):
		if self.root is None:
			return

		node = self.pick_node()
		if node.parentNode is None:
			self.root = None

		queue = [node]
		while queue:
			node = queue.pop()
			queue.extend(node.childNodes)
			self.nodes.pop(node.id)

			if node.parentNode:
				node.parentNode.removeChild(node)
			node.destroy()

		self.update()

	
	def insert_child(self):
		node = self.pick_node()
		if node.parentNode is None: # root
			return

		new    = self.new_node()
		new.cy = node.cy
		node.parentNode.insertChild(node, new)
		self.update()


	def update_node(self):
		node = self.pick_node()
		new  = self.new_node(node.title)

		new.cx = node.cx
		new.cy = node.cy
		self.nodes[new.id] = new
		self.nodes_serial += 1

		while node.firstChild:
			new.appendChild(
				node.removeChild(node.firstChild)
			)

		if node.parentNode:
			node.parentNode.replaceChild(node, new)
			node.destroy()
		else: # root
			self.root.destroy()
			self.root = new

		self.nodes.pop(node.id)

		self.update()
	
	
	def change_title(self):
		node = self.pick_node()
		text = tkSimpleDialog.askstring(
			"New title", "", initialvalue=node.title
		)
		node.title = text
		self.update()
	
	
	def create_ui(self, master):
		# create menu
		menu  = Tkinter.Frame(master, padx=3, pady=3)
		
		self.function = Tkinter.StringVar()
		self.function.trace_variable('w', self.set_function)

		def rb(text, value):
			widget = Tkinter.Radiobutton(
				menu,
				text		= text,
				variable	= self.function,
				value		= value,
				indicatoron	= 0,
				selectcolor	= 'lightgray'
			).pack(fill=X)

		rb('Append child',		'append')
		rb('Insert node',		'insert')
		rb('Delete subtree',	'delete')
		rb('Update',			'update')
		rb('Set title',			'title')

		self.fun_lookup = {
			'append'	: self.append_child,
			'insert'	: self.insert_child,
			'delete'	: self.delete_subtree,
			'update'	: self.update_node,
			'title'		: self.change_title,
		}

		# tree layout method chooser
		frame1 = Tkinter.Frame(menu, relief=RIDGE, bd=2, padx=3, pady=3)
		
		self.method = Tkinter.IntVar()
		self.method.trace_variable('w', self.update)

		Tkinter.Label(
			frame1,
			text='Layout method:',
			anchor=W,
		).pack(fill=X)
		
		Tkinter.Radiobutton(
			frame1,
			text="simple",
			value=0,
			variable=self.method,
			anchor=W
		).pack(fill=X)
		
		Tkinter.Radiobutton(
			frame1,
			text="advanced",
			value=1,
			variable=self.method,
			anchor=W
		).pack(fill=X)

		# shape of node
		frame2 = Tkinter.Frame(menu, relief=RIDGE, bd=2, padx=3, pady=3)
		self.shape = Tkinter.StringVar()
		self.shape.set('rect')
		
		Tkinter.Radiobutton(
			frame2,
			text="rectangle",
			value='rect',
			variable=self.shape,
			anchor=W
		).pack(fill=X)
		
		Tkinter.Radiobutton(
			frame2,
			text="circle",
			value='circ',
			variable=self.shape,
			anchor=W
		).pack(fill=X)
		
		Tkinter.Radiobutton(
			frame2,
			text="rounded rect",
			value='rrect',
			variable=self.shape,
			anchor=W
		).pack(fill=X)

		# background color
		try:
			from tkcolorpicker import ColorPicker
			frame3 = Tkinter.Frame(menu, relief=RIDGE, bd=2, padx=3, pady=3)
			self.background = ColorPicker(100, 100, frame3)
			self.background.pack()
		except ImportError:
			class ColorPicker: pass
			self.background = ColorPicker()
			self.background.color = "white"

		# SVG
		try:
			import canvasvg
			def save():
				self.canvas.itemconfigure(ALL, width=0.4)
				canvasvg.saveall('test.svg', self.canvas)


			Tkinter.Button(menu, text="SVG export", command=save).pack(fill=X)
		except ImportError:
			print "Module canvas2svg not available"

		# pack menu	
		frame1.pack(fill=X)
		frame2.pack(fill=X)
		try:
			frame3.pack(fill=X)
		except UnboundLocalError:
			pass
		menu.pack(side=LEFT, fill=Y)

		# create scrollable canvas
		frame = Tkinter.Frame(master)
		self.canvas = Tkinter.Canvas(frame, bg="#ccc")

		sx = Tkinter.Scrollbar(frame, orient=HORIZONTAL)
		sy = Tkinter.Scrollbar(frame)

		self.canvas['xscrollcommand'] = sx.set
		self.canvas['yscrollcommand'] = sy.set
		sx['command'] = self.canvas.xview
		sy['command'] = self.canvas.yview

		sx.pack(fill=X, side=BOTTOM)
		self.canvas.pack(side=LEFT, fill=BOTH, expand=1)
		sy.pack(fill=Y, side=RIGHT)

		self.canvas.pack(fill=BOTH, expand=1)
		
		frame.pack(side=RIGHT, fill=BOTH, expand=1)

	
	def set_function(self, *ignored):
		try:
			funname = self.function.get()
			self.es.set_function(self.fun_lookup[funname])
		except KeyError:
			self.es.unset_function()
		

if __name__ == '__main__':
	root = Tkinter.Tk()
	app  = TreeLayoutDemo(root)
	root.mainloop()

# vim: ts=4 sw=4
