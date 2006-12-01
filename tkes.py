"""
Tkinter Events Serializer
=========================

author: Wojciech Mula
        wojciech_mula@poczta.onet.pl

license: BSD

$Id: tkes.py,v 1.4 2006-12-01 16:54:15 wojtek Exp $
"""

import Tkinter

__all__ = ['FunctionInterrupted', 'EventsSerializer']

class FunctionInterrupted(Exception): pass

class EventsSerializer(object):
	def __init__(self, abort_event, autobind=None):
		self.__queue = []
		self.__fun   = None
		self.__args  = None
		self.__abort = abort_event

		if autobind is not None:

			def create_handler(self, name):
				def handler(event):
					self.add_event(name, event)
				return handler

			for widget, events_list in autobind.iteritems():
				for item in events_list:
					try:
						name, tkevent  = item
					except TypeError:
						name = tkevent = item
					widget.bind(tkevent, create_handler(self, name))
		
		self.__root = Tkinter._default_root
		self.__flag = Tkinter.BooleanVar()
		self.__root.wait_visibility()

		# save old WM_DELETE_WINDOW handler, we will call it on exit
		self.__delete_command = self.__root.protocol('WM_DELETE_WINDOW')
		self.__root.protocol('WM_DELETE_WINDOW', self.__delete)

	def __delete(self):
		self.unset_function()
		self.__root.tk.call(self.__delete_command)
	
	def __worker(self):
		"Function that run and manage other functions"
		fun  = self.__fun
		args = self.__args
		if fun:
			try:
				# run function
				fun(*args)
			except FunctionInterrupted:
				pass
			self.__root.after_idle(self.__worker)
	
	def add_event(self, name, event):
		"If any function is running insert new event into events queue."
		if self.__fun is not None:
			self.__queue.insert(0, (name, event))
			self.__flag.set(True)
	
	def get_event(self):
		"Get next event from queue. Wait if queue is empty."
		while not self.__queue:
			self.__root.wait_variable(self.__flag)
	
		name, event = self.__queue.pop()
		if name == self.__abort:
			raise FunctionInterrupted
		else:
			return name, event

	def set_function(self, fun=None, args=()):
		"""
		Set new function to execute inside thread.
		Function that is currently running is interrupted.
		"""
		if fun is self.__fun:
			return

		self.interrupt()
			
		if fun is None:	# unset function
			self.__fun  = None
			self.__args = ()
		else:
			if self.__fun is None:
				self.__fun  = fun
				self.__args = args
				self.__root.after_idle(self.__worker)
			else:
				self.__fun  = fun
				self.__args = args

	def unset_function(self):
		"""Interrupt function executed inside thread and
		wait for new function."""
		self.interrupt()
		self.set_function(None)
	
	def interrupt(self):
		"Interrupt function executed inside thread"
		if self.__fun:
			# empty queue and send ABORT event
			self.__queue = [(self.__abort, None)]
			self.__flag.set(False)

	def wait_events(self, watch, exceptions={}):
		"""
		Wait for one of events that names are
		listed in 'watch'.

		If event is listed in 'exception' dictionary
		then suitable exception is raised.

		If event of name 'abort_event' apper exception
		FunctionInterrupted is raised.

		All other events are ignored.
		
		Example:
			
			name, event = wait_events(
							[CLICK_1, PRESS_ENTER],
							{CLICK_2: ReenterValue}
			)

			Function will return if event CLICK_1 or PRESS_ENTER occur.
			Function will raise exception ReenterValue if CLICK_2 occur.
		"""
		while True:
			name, data = self.get_event()
			if name in watch:
				return name, data
			elif name in exceptions:
				raise exceptions[name]


	def wait_event(self, event, exceptions={}):
		"Wait for single event. See description of 'wait_events'."
		name, data = self.wait_events([event], exceptions)
		return data
	
	def report_events(self, watch, breakon, exceptions={}):
		"""
		Generator yields all events listed in 'watch' list.
		Generator returns if any event from 'breakon' list
		occured.

		If event of name 'abort_event' apper exception
		FunctionInterrupted is raised.

		If event is listed in 'exception' dictionary
		then suitable exception is raised.

		If event of name 'abort_event' apper exception
		FunctionInterrupted is raised.

		All other events are ignored.
		
		Example:
		
			# print current coordinates of mouse, break
			# when user press mouse button 1.
			for name, event in wait_events([MOVED], [CLICK1]):
				print event.x, event.y
		"""
		while True:
			name, event = self.get_event()
			
			if name in watch:
				yield name, event
			elif name in exceptions:
				raise exceptions[name]
			elif name in breakon:
				break

	def report_event(self, event, breakon, exceptions={}):
		for item in report_events([event], breakon, exceptions):
			yield item

#######################################################################
# Example: simple drawing program -- user can draw basic shapes
# and delete them

import Tkinter
import math
class Application:

	def __init__(self, root):
		self.root = root
		self.create_widgets()

		# we write one event handler
		self.canvas.bind('<Motion>', self.motion_event)

		# three other will be registered by EventsSerializer instance
		autobindevents = (
			('CLICK1', "<Button-1>"),
			('CLICK2', "<Button-3>"),
			('ABORT',  "<Escape>"),
		)

		self.es   = EventsSerializer('ABORT', 
			{self.canvas: autobindevents}
		)

		# trigger action setting function
		self.action.set(self.action.get())


	def motion_event(self, event):
		x = int(self.canvas.canvasx(event.x))
		y = int(self.canvas.canvasy(event.y))
		self.mousepos.set("x=%d, y=%d" % (x, y))
		self.es.add_event('MOTION', event)

	# Interaction functions helper
	def get_point(self):
		"Return point after click (event CLICK2 acts like ABORT)"
		event = self.es.wait_event('CLICK1', {'CLICK2': FunctionInterrupted})
		return (self.canvas.canvasx(event.x),
		        self.canvas.canvasy(event.y))

	def track_mouse(self):
		"Report mouse position (event CLICK2 is ignored)"
		for name, event in self.es.report_events(['MOTION'], ['CLICK1']):
			yield (self.canvas.canvasx(event.x),
		           self.canvas.canvasy(event.y))

	def mark_rectangle(self, dash=''):
		"Interactive rectangle drawing --- returns rect corners"
		try:
			x1, y1 = self.get_point()
			x2, y2 = x1, y1
			rect   = self.canvas.create_rectangle(x1, y1, x2, y2, dash=dash)
			for x2, y2 in self.track_mouse():
				self.canvas.coords(rect, x1, y1, x2, y2)

			self.canvas.delete(rect)
			return (x1, y1, x2, y2)
				
		except FunctionInterrupted:
			# in case of interrupt we have to clean up (remove
			# rectangle, if any)
			try:
				self.canvas.delete(rect)
			except UnboundLocalError:
				pass
			# because this function may be used inside other,
			# this exception must propagate
			raise FunctionInterrupted

	
	def mark_segment(self, x1, y1, dash=''):
		"""Interactive segment drawing --- returns line endpoints

		Raises ValueError on CLICK2 event.
		"""
		try:
			x2, y2 = x1, y1
			line   = self.canvas.create_line(x1, y1, x2, y2, dash=dash)

			cx = self.canvas.canvasx
			cy = self.canvas.canvasy
			for name, event in self.es.report_events(['MOTION'], ['CLICK1'], {'CLICK2': ValueError}):
				x2, y2 = cx(event.x), cy(event.y)
				self.canvas.coords(line, x1, y1, x2, y2)

			self.canvas.delete(line)
			return (x2, y2)
				
		except (FunctionInterrupted, ValueError), exc:
			try:
				self.canvas.delete(line)
			except UnboundLocalError:
				pass
			raise exc

	# Interactive function
	def draw_rectangle(self):
		x1, y1, x2, y2 = self.mark_rectangle()
		self.canvas.create_rectangle(x1, y1, x2, y2, activeoutline='red')
		self.update_scrollregion()
	
	def draw_circle(self):
		try:
			# get center
			r      = 0.0
			xo, yo = self.get_point()
			item   = self.canvas.create_oval(xo, yo, xo, yo, dash=5)

			for x, y in self.track_mouse():
				r = math.hypot(x-xo, y-yo)
				self.canvas.coords(item, xo-r, yo-r, xo+r, yo+r)

			self.canvas.itemconfigure(item, dash='', activeoutline='red')
			self.update_scrollregion()
		except FunctionInterrupted:
			try:
				self.canvas.delete(item)
			except UnboundLocalError:
				pass
	
	def draw_ellipse(self):
		try:
			# get center
			rx     = 0.0
			ry     = 0.0
			xo, yo = self.get_point()
			item   = self.canvas.create_oval(xo, yo, xo, yo, dash=5)

			for x, y in self.track_mouse():
				rx = abs(x-xo)
				ry = abs(y-yo)
				self.canvas.coords(item, xo-rx, yo-ry, xo+rx, yo+ry)

			self.canvas.itemconfigure(item, dash='', activeoutline='red')
			self.update_scrollregion()
		except FunctionInterrupted:
			try:
				self.canvas.delete(item)
			except UnboundLocalError:
				pass

	def draw_line(self):
		x1, y1 = self.get_point()
		try:
			x2, y2 = self.mark_segment(x1, y1, dash=5)
			self.canvas.create_line(x1, y1, x2, y2, activefill='red')
			self.update_scrollregion()
		except ValueError:
			pass
	

	def draw_polyline(self):
		try:
			x1, y1 = self.get_point()
			item   = self.canvas.create_line(x1, y1, x1, y1)
			xp, yp = self.mark_segment(x1, y1, dash=5)
			points = [item, x1, y1, xp, yp]
			self.canvas.coords(*points)

			while True:
				try:
					xn, yn = self.mark_segment(xp, yp, dash=5)
				except ValueError:
					break
				points.append(xn)
				points.append(yn)
				self.canvas.coords(*points)
				xp = xn
				yp = yn

			self.canvas.itemconfigure(item, activefill="red")
			self.update_scrollregion()

		except FunctionInterrupted:
			try:
				self.canvas.delete(item)
			except UnboundLocalError:
				pass

	def delete_item(self):
		while True:
			x, y = self.get_point()
			try:
				item = self.canvas.find_withtag(Tkinter.CURRENT)[0]
				self.canvas.delete(item)
				self.update_scrollregion()
			except IndexError:
				continue
	
	def delete_items_in_rect(self):
		while True:
			x1, y1, x2, y2 = self.mark_rectangle(dash=5)
			items = self.canvas.find_enclosed(x1, y1, x2, y2)
			if items:
				for item in items:
					self.canvas.delete(item)
				self.update_scrollregion()
	
	# Others
	def set_action(self, *args):
		what = self.action.get()

		if   what == 'rect':	fun = self.draw_rectangle
		elif what == 'circ':	fun = self.draw_circle
		elif what == 'ell':		fun = self.draw_ellipse
		elif what == 'line':	fun = self.draw_line
		elif what == 'poly':	fun = self.draw_polyline
		elif what == 'del':		fun = self.delete_item
		elif what == 'delrect':	fun = self.delete_items_in_rect

		self.es.set_function(fun)
	
	def create_widgets(self):

		# create scrollable canvas
		draw = Tkinter.Frame(self.root)
		self.canvas = Tkinter.Canvas(draw, bg="white")
		self.sx     = Tkinter.Scrollbar(draw, orient=Tkinter.HORIZONTAL)
		self.sy     = Tkinter.Scrollbar(draw)
		self.canvas['xscrollcommand'] = self.sx.set
		self.canvas['yscrollcommand'] = self.sy.set
		self.sx['command'] = self.canvas.xview
		self.sy['command'] = self.canvas.yview

		self.sy.pack(side=Tkinter.RIGHT,  fill=Tkinter.Y)
		self.sx.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
		self.canvas.pack(side=Tkinter.RIGHT, fill=Tkinter.BOTH, expand=1)
		self.canvas.focus_set()

		
		# create menu
		menu = Tkinter.Frame(self.root, bg="#aaa")
		def rb(text, value):
			widget = Tkinter.Radiobutton(
				menu, text=text,
				value=value, variable=self.action,
				indicatoron=0, anchor=Tkinter.W)
			widget.pack(fill=Tkinter.X)
		
		self.action = Tkinter.StringVar()
		self.action.set('rect')
		self.action.trace_variable('w', self.set_action)

		rb('Draw rect',     'rect')
		rb('Draw circle',   'circ')
		rb('Draw ellipse',  'ell')
		rb('Draw line',     'line')
		rb('Draw polyline', 'poly')
		rb('Delete item',   'del')
		rb('Delete items in rect', 'delrect')

		self.mousepos = Tkinter.StringVar()
		self.mousepos.set("")
		label = Tkinter.Label(textvariable=self.mousepos)
		label.pack(fill=Tkinter.X)

		menu.pack(side=Tkinter.LEFT, fill=Tkinter.Y)
		draw.pack(side=Tkinter.LEFT, fill=Tkinter.BOTH, expand=1)
	
	def update_scrollregion(self):
		try:
			x1, y1, x2, y2 = self.canvas.bbox(Tkinter.ALL)
			self.canvas.configure(scrollregion=(x1-10, y1-10, x2+10, y2+10))
		except TypeError:
			# raised when canvas is empty
			pass

if __name__ == '__main__':
	root = Tkinter.Tk()
	app  = Application(root)
	root.mainloop()

# vim: ts=4 sw=4 nowrap noexpandtab
