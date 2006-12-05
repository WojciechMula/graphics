import Tkinter

from Tkconstants import *
from tkes   import EventsSerializer, FunctionInterrupted

from polyintersect import intersection

ABORT  = "abort"
LBM    = '<Button-1>'
LBM2   = '<Double-Button-1>'
RBM    = '<Button-3>'
MOTION = '<Motion>'
class Stop(Exception): pass

class SutherlandHodgmanDemo(object):
	def __init__(self, master):
		self.create_ui(master)
		self.r = 3
		self.points = {}

		bindings = [LBM, LBM2, RBM, MOTION, (ABORT, '<Escape>')]
		self.es = EventsSerializer(ABORT, {self.canvas: bindings})
		self.function.set('new')
	
	def get_point(self):
		event = self.es.wait_event(LBM)
		return (self.canvas.canvasx(event.x),
		        self.canvas.canvasx(event.y))
	
	def trace_mouse(self):
		cx = self.canvas.canvasx
		cy = self.canvas.canvasy
		rep = self.es.report_events([MOTION], [LBM], {RBM: Stop, LBM2: Stop})
		for name, event in rep:
			yield cx(event.x), cy(event.y)
	
	def select_polygon(self):
		while True:
			self.es.wait_event(LBM)
			try:
				item = self.canvas.find_withtag(CURRENT)[0]
				if 'selected' not in self.canvas.gettags(item):
					return item
			except IndexError:
				pass

	def new_polygon(self):
		try:
			x1, y1 = self.get_point()
			poly   = self.canvas.create_polygon(x1, y1, x1, y1, tags='tmp', fill='', outline='red')
			index  = 2
		
			try:
				while True:
					for x2, y2 in self.trace_mouse():
						self.canvas.insert(poly, index, (x2, y2))
						self.canvas.dchars(poly, index+2)
					
					self.canvas.insert(poly, 'end', (x2, y2))
					index += 2

			except Stop:
				if index/2 < 3:
					raise FunctionInterrupted

			self.canvas.dtag(poly, 'tmp')
			self.canvas.itemconfigure(poly, outline='black', activeoutline='blue')
				
		except FunctionInterrupted:
			self.canvas.delete('tmp')
			raise FunctionInterrupted

		self.canvas.delete('tmp')
	
	
	def del_polygon(self):
		self.es.wait_event(LBM)
		try:
			item = self.canvas.find_withtag(CURRENT)[0]
			self.canvas.delete(item)
		except IndexError:
			pass

	def move_polygon(self):
		event = self.es.wait_event(LBM)
		try:
			canv   = self.canvas
			item   = canv.find_withtag(CURRENT)[0]
			xo, yo = event.x, event.y
			for _, event in self.es.report_events([MOTION], [LBM, RBM, LBM2]):
				x, y = event.x, event.y
				self.canvas.move(item, x-xo, y-yo)
				xo = x
				yo = y
		except IndexError:
			pass
	
	def clone_polygon(self):
		event = self.es.wait_event(LBM)
		try:
			canv   = self.canvas
			item   = canv.find_withtag(CURRENT)[0]
			coords = canv.coords(item)

			conf   = canv.itemconfigure(item)
			for key, (v1, v2, v3, v4, v5) in conf.iteritems():
				conf[key] = v5

			item   = canv.create_polygon(*coords, **conf)

			xo, yo = event.x, event.y
			for _, event in self.es.report_events([MOTION], [LBM, RBM, LBM2]):
				x, y = event.x, event.y
				self.canvas.move(item, x-xo, y-yo)
				xo = x
				yo = y
		except IndexError:
			pass


	def demo(self):
		if len(self.canvas.find_withtag(ALL)) < 2:
			return
		try:
			poly1 = self.select_polygon()
			self.canvas.itemconfigure(poly1, width=2, outline='red', tags='selected')
			
			poly2 = self.select_polygon()
			self.canvas.itemconfigure(poly2, width=2, outline='red', tags='selected')

			def conv(points):
				for i in xrange(0, len(points), 2):
					yield points[i], points[i+1]

			p1 = [p for p in conv(self.canvas.coords(poly1))]
			p2 = [p for p in conv(self.canvas.coords(poly2))]
		
			import utils2D
			if utils2D.isconvex(p1):
				p = intersection(p2, p1)
			elif utils2D.isconvex(p2):
				p = intersection(p1, p2)
			else:
				print "none convex"
				# p1 nor p2 is not convex
				raise FunctionInterrupted

			def flatten(points):
				for x, y in points:
					yield x
					yield y
			 
			if p:
				poly = self.canvas.create_polygon(*flatten(p))
				self.canvas.itemconfigure(
					poly,
					fill	= '',
					outline	= 'green',
					activeoutline ='blue'
				)
			else:
				print "empty"

		except FunctionInterrupted:
			pass
		
		self.canvas.itemconfigure('selected', outline='black', width=1, tags='')

	def create_ui(self, master):
		self.canvas = Tkinter.Canvas(master, bg='white')
		self.canvas.focus_set()

		self.function = Tkinter.StringVar()
		self.function.trace_variable('w', self.set_function)
		menu = Tkinter.Frame(root, bg="#aaa")
		def rb(text, value):
			widget = Tkinter.Radiobutton(
						menu, text=text,
						value=value, variable=self.function,
						indicatoron=0, anchor=W, selectcolor="lightgray",
						padx=4, pady=4)
			widget.pack(fill=X)
			return widget

		rb('new polygon',			'new')
		rb('delete polygon',		'del')
		rb('move polygon',			'move')
		rb('clone polygon',			'clone')
		rb('Sutherland-Hodgman',	'and')

		self.lookup = {
			'new'	: self.new_polygon,
			'del'	: self.del_polygon,
			'move'	: self.move_polygon,
			'clone'	: self.clone_polygon,
			'and'	: self.demo,
		}

		# pack
		self.canvas.pack(fill=BOTH, expand=1, side=RIGHT)
		menu.pack(fill=Y, side=LEFT)


	def set_function(self, *ignored):
		try:
			funname = self.function.get()
			self.es.set_function(self.lookup[funname])
		except KeyError:
			print "error"
			self.es.unset_function()


if __name__ == '__main__':
	root = Tkinter.Tk()
	app  = SutherlandHodgmanDemo(root)
	root.mainloop()

# vim: ts=4 sw=4
