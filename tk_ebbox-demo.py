# wm. 30.11.2006

import Tkinter

from math     import hypot
from tkes     import *
from tk_ebbox import *

ABORT  = 0
CLICK  = 1
MOTION = 2

def set_coords(canvas, tagOrId, points):
	canvas.tk.call(canvas._w, 'coords', tagOrId, *points)

class DemoApp:
	def __init__(self, root):

		self.create_ui(root)
		self.points = [(10.0, 10.0), (100.0, 50.0), (200.0, 20.0)]
		
		bindings = [
			(CLICK,  '<Button-1>'),
			(CLICK,  '<Button-3>'),
			(MOTION, '<Motion>'),
			(ABORT,  '<Escape>'),
		]
		self.es = EventsSerializer(ABORT, {self.canvas: bindings})
		
		self.closed.set(False)
		self.show_bbox.set(True)
		self.show_ebbox.set(True)
		self.function.set('move')
		self.update_view()
	
	def create_ui(self, root):

		# variables
		self.function = Tkinter.StringVar()
		self.function.trace_variable('w', self.function_changed)

		self.closed = Tkinter.BooleanVar()
		self.closed.trace_variable('w', self.closed_changed)

		self.show_bbox  = Tkinter.BooleanVar()
		self.show_ebbox = Tkinter.BooleanVar()
		self.show_bbox.trace_variable('w', self.show_bbox_changed)
		self.show_ebbox.trace_variable('w', self.show_bbox_changed)

		# menu
		menu = Tkinter.Frame(root, bg="#aaa")
		def rb(text, value):
			widget = Tkinter.Radiobutton(
						menu, text=text,
						value=value, variable=self.function,
						indicatoron=0, anchor=Tkinter.W, selectcolor="lightgray",
						padx=4, pady=4)
			widget.pack(fill=Tkinter.X)

		rb('add   point',  'add')
		rb('delete point', 'del')
		rb('move point',   'move')
		self.lookup = {
			'add': self.add_vertex,
			'del': self.del_vertex,
			'move': self.move_vertex,
		}

		widget = Tkinter.Checkbutton(menu, text='Closed', variable=self.closed, anchor=Tkinter.W)
		widget.pack(fill=Tkinter.X)
		widget = Tkinter.Checkbutton(menu, text='Show bbox', variable=self.show_bbox, anchor=Tkinter.W)
		widget.pack(fill=Tkinter.X)
		widget = Tkinter.Checkbutton(menu, text='Show exact bbox', variable=self.show_ebbox, anchor=Tkinter.W)
		widget.pack(fill=Tkinter.X)

		# drawing area
		da   = Tkinter.Frame(root)
		self.canvas = Tkinter.Canvas(da, bg='white')

		self.canvas.pack(fill=Tkinter.BOTH, expand=1)
		
		# canvas items
		self.line   = self.canvas.create_line(0, 0, 0, 0, state='hidden', tags='line', fill='blue')
		self.line_s = self.canvas.create_line(0, 0, 0, 0, state='hidden', tags='line', smooth=1)
		self.poly   = self.canvas.create_polygon(0, 0, 0, 0, state='hidden', tags='poly', fill='', outline='blue')
		self.poly_s = self.canvas.create_polygon(0, 0, 0, 0, state='hidden', tags='poly', fill='', outline='black', smooth=1)
		self.bbox   = self.canvas.create_rectangle(0, 0, 0, 0, state='hidden', tags='bbox', dash=5, outline='#aaa')
		self.ebbox  = self.canvas.create_rectangle(0, 0, 0, 0, state='hidden', tags='bbox', dash=5, outline='red')

		# pack frames
		menu.pack(side=Tkinter.RIGHT, fill=Tkinter.Y)
		da  .pack(side=Tkinter.RIGHT, fill=Tkinter.BOTH, expand=1)

	def function_changed(self, *ignored):
		funname = self.function.get()
		try:
			fun = self.lookup[funname]
			self.es.set_function(fun)
		except KeyError:
			self.es.unset_function()

	def closed_changed(self, *ignored):
		if self.closed.get():
			self.canvas.itemconfig('line', state='hidden')
			self.canvas.itemconfig('poly', state='normal')
		else:
			self.canvas.itemconfig('poly', state='hidden')
			self.canvas.itemconfig('line', state='normal')

		self.update_view()
			

	def show_bbox_changed(self, *ignored):
		def state(boolvar):
			if boolvar.get():
				return 'norma'
			else:
				return 'hidden'
		
		self.canvas.itemconfig(self.bbox,  state=state(self.show_bbox))
		self.canvas.itemconfig(self.ebbox, state=state(self.show_ebbox))

	def update_view(self):
		flatten = []
		for x, y in self.points:
			flatten.append(x)
			flatten.append(y)

		for item in [self.line, self.line_s, self.poly, self.poly_s]:
			set_coords(self.canvas, item, flatten)

		try:
			if self.closed.get():
				x1, y1, x2, y2 = self.canvas.bbox(self.poly_s)
				self.canvas.coords(self.bbox, x1, y1, x2, y2)
				
				x1, y1, x2, y2 = exact_polygon_bbox(self.points)
				self.canvas.coords(self.ebbox, x1, y1, x2, y2)
			else:
				x1, y1, x2, y2 = self.canvas.bbox(self.line_s)
				self.canvas.coords(self.bbox, x1, y1, x2, y2)
				
				x1, y1, x2, y2 = exact_line_bbox(self.points)
				self.canvas.coords(self.ebbox, x1, y1, x2, y2)
		except TypeError:
			pass


	def pick_point(self):
		event = self.es.wait_event(CLICK)
		return (self.canvas.canvasx(event.x),
		        self.canvas.canvasy(event.y))
	
	def pick_vertex(self):
		while True:
			x, y   = self.pick_point()
			index  = self.canvas.index(self.poly, "@%r,%r" % (x, y))/2
			xi, yi = self.points[index]
			if hypot(x-xi, y-yi) < 20.0:
				return index

	def add_vertex(self):
		self.points.append( self.pick_point() )
		self.update_view()
	
	def del_vertex(self):
		if len(self.points) < 3:
			return
		
		self.points.pop( self.pick_vertex() )
		self.update_view()
	
	def move_vertex(self):
		index = self.pick_vertex()

		cx = self.canvas.canvasx
		cy = self.canvas.canvasy

		for name, event in self.es.report_events([MOTION], [CLICK]):
			self.points[index] = x, y = cx(event.x), cy(event.y)
			self.update_view()

import _tkinter
if __name__ == '__main__':
	root = Tkinter.Tk()
	root.wm_title("Tkinter Demo - exact bbox of smoothed lines/polylines")
	app  = DemoApp(root)
	root.mainloop()

# vim: ts=4 sw=4 nowrap noexpandtab
