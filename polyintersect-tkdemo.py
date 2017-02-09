# -*- coding: iso-8859-2 -*-
# Wojciech Muła, http://0x80.pl/
# 5.12.2006
#
# Public domain
# $Date: 2007-03-01 18:28:32 $ $Revision: 1.2 $
"Tkinter + tkes demo of Sutherland-Hodgman algorithm"

import Tkinter

from Tkconstants import *
from tkes   import EventsSerializer, FunctionInterrupted

from polyintersect import intersection
from isconvex import isconvex

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
			self.status = "Pick first points, RBM/ESC - cancel"
			x1, y1 = self.get_point()
			poly   = self.canvas.create_polygon(x1, y1, x1, y1, tags='tmp', fill='', outline='red')
			index  = 2
		
			try:
				self.status = "Pick next point, double LBM/RBM - accept, ESC - cancel"
				xp, yp = x1, y1
				while True:
					for x2, y2 in self.trace_mouse():
						self.canvas.insert(poly, index, (x2, y2))
						self.canvas.dchars(poly, index+2)

					if x2 != xp and y2 != yp:
						self.canvas.insert(poly, 'end', (x2, y2))
						index += 2
					xp, yp = x2, y2

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
		self.status = "Pick polygon to delete"
		self.es.wait_event(LBM)
		try:
			item = self.canvas.find_withtag(CURRENT)[0]
			self.canvas.delete(item)
		except IndexError:
			pass

	def move_polygon(self):
		self.status = "Pick polygon to move"
		event = self.es.wait_event(LBM)
		try:
			canv   = self.canvas
			item   = canv.find_withtag(CURRENT)[0]
			xo, yo = event.x, event.y
			xp, yp = xo, yo
			x,  y  = xo, yo
			for _, event in self.es.report_events([MOTION], [LBM, RBM, LBM2]):
				x, y = event.x, event.y
				self.canvas.move(item, x-xp, y-yp)
				xp = x
				yp = y
				self.status = "moved: %d, %d;  LBM/RBM - accept, ESC - cancel" % (x-xo, y-yo)
		except IndexError:
			pass
		except FunctionInterrupted:
			self.canvas.move(item, xo-x, yo-y)
			raise FunctionInterrupted
	
	def clone_polygon(self):
		self.status = "Pick polygon to clone"
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
			def conv(points):
				for i in xrange(0, len(points), 2):
					yield points[i], points[i+1]

			self.status = "Pick first polygon"
			poly1 = self.select_polygon()
			self.canvas.itemconfigure(poly1, width=2, outline='red', tags='selected')
			p1 = [p for p in conv(self.canvas.coords(poly1))]
			convex1 = isconvex(p1)

			if convex1:	
				self.status = "Picked convex polygon, now pick any polygon, either convex or nonconvex"
			else:
				self.status = "Pick CONVEX polygon"

			poly2 = self.select_polygon()
			self.canvas.itemconfigure(poly2, width=2, outline='red', tags='selected')
			p2 = [p for p in conv(self.canvas.coords(poly2))]
			convex2 = isconvex(p2)
		
			if convex1:
				p = intersection(p2, p1)
			elif convex2:
				p = intersection(p1, p2)
			else:
				self.status = "You did not pick a convex polygon"
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

		self.__status = Tkinter.StringVar()
		self.__status.set("")
		label = Tkinter.Label(master, textvariable=self.__status)

		# pack
		label.pack(side=BOTTOM)
		self.canvas.pack(fill=BOTH, expand=1, side=RIGHT)
		menu.pack(fill=Y, side=LEFT)
	
	
	def set_status(self, text):
		self.__status.set(text)
	
	status = property(fset=set_status)


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

# vim: ts=4 sw=4 nowrap
