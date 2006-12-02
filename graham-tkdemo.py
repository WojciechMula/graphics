import Tkinter

from Tkconstants import *
from tkes   import EventsSerializer, FunctionInterrupted
from graham import convex_hull

ABORT  = "abort"
LBM    = '<Button-1>'
RBM    = '<Button-3>'

class GrahamDemo(object):
	def __init__(self, master):
		self.create_ui(master)
		self.canvas.focus_set()
		self.canvas.bind('<Control-Shift-C>', self.clear_all)
		self.r = 3
		self.points = {}

		bindings = [LBM, RBM, (ABORT, '<Escape>')]
		self.es = EventsSerializer(ABORT, {self.canvas: bindings})
		self.es.set_function(self.adddel_points)
		
	def adddel_points(self):
		cx = self.canvas.canvasx
		cy = self.canvas.canvasy
		while True:
			name, event = self.es.wait_events([LBM, RBM])
			x, y = cx(event.x), cy(event.y)
			if name == LBM:
				r    = self.r
				item = self.canvas.create_oval(x-r, y-r, x+r, y+r, fill='white', activefill='red')
				self.points[item] = (x, y)
				self.changed()
			else: # RBM
				try:
					item = self.canvas.find_withtag(CURRENT)[0]
					self.canvas.delete(item)
					self.points.pop(item)
					self.changed()
				except IndexError:
					pass
		#end
	
	def clear_all(self, event):
		for item in self.points:
			self.canvas.delete(item)
		self.points = {}
		self.changed()
		
	def demo(self):
		self.canvas.delete('chull')
		if len(self.points) < 3:
			return

		points = []
		for x, y, index in convex_hull(self.points.values()):
			points.append(x)
			points.append(y)

		r = self.r*3
		x = points[0]
		y = points[1]
		self.canvas.create_oval(x-r, y-r, x+r, y+r, tags='chull')
		
		x = points[-2]
		y = points[-1]
		self.canvas.create_oval(x-r, y-r, x+r, y+r, tags='chull', outline='red')

		l = self.canvas.create_polygon(*points)
		self.canvas.itemconfigure(l, tags='chull', fill='', outline='blue', state='disabled')
		self.canvas.tag_lower(l, ALL)
	
	changed = demo

	def create_ui(self, master):
		self.canvas = Tkinter.Canvas(master, bg='white')
		self.canvas.pack(fill=BOTH, expand=1)

if __name__ == '__main__':
	root = Tkinter.Tk()
	app  = GrahamDemo(root)
	root.mainloop()

# vim ts=4 sw=4
