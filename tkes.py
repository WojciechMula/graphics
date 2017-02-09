"""
Tkinter Events Serializer
=========================

author: Wojciech Mula
        wojciech_mula@poczta.onet.pl
		http://0x80.pl/

license: BSD

$Id: tkes.py,v 1.8 2007-03-01 18:29:46 wojtek Exp $
"""

import Tkinter

__all__ = [
	'FunctionInterrupted',
	'EventsSerializer',
	'EventsSerializerTk',
	'EventsSerializerThreads',
]

class FunctionInterrupted(Exception): pass
class ApplicationDestroyed(Exception): pass

class EventsSerializerTk(object):
	"Tk-based events serializer"
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
					except ValueError:
						name = tkevent = item

					if name is None:
						raise ValueError("Event name cannot be None")

					widget.bind(tkevent, create_handler(self, name))
		
		self.__root = Tkinter._default_root
		self.__flag = Tkinter.BooleanVar()
		self.__root.wait_visibility()

		# save old WM_DELETE_WINDOW handler, we will call it on exit
		self.__delete_command = self.__root.protocol('WM_DELETE_WINDOW')
		self.__root.protocol('WM_DELETE_WINDOW', self.__delete)

	def __delete(self):
		self.__queue = [(None, None)]
		self.__flag.set(False)
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
			except ApplicationDestroyed:
				return
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
		elif name is None:
			raise ApplicationDestroyed
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



class EventsSerializerThreads(object):
	"threads-based events serializer"
	def __init__(self, abort_event, autobind=None):
		self.__queue = Queue.Queue()
		self.__lock  = thread.allocate_lock()
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
					except ValueError:
						name = tkevent = item

					if name is None:
						raise ValueError("Event name cannot be None")

					widget.bind(tkevent, create_handler(self, name))

		self.__lock.acquire()
		thread.start_new_thread(self.__thread, ())
	
	def __thread(self):
		"Worker"
		while True:
			# wait for function
			self.__lock.acquire()	
			fun  = self.__fun
			args = self.__args
			self.__lock.release()
			if fun:
				try:
					# run function
					fun(*args)
				except FunctionInterrupted:
					pass
				except ApplicationDestroyed:
					return
	
	def add_event(self, name, event):
		"If any function is running insert new event into events queu."
		if self.__fun is not None:
			self.__queue.put((name, event))
	
	def get_event(self):
		"Get next event from queue. Wait if queue is empty."
		name, event = self.__queue.get()
		if name == self.__abort:
			raise FunctionInterrupted
		elif name is None:
			raise ApplicationDestroyed
		else:
			return name, event

	def set_function(self, fun=None, args=()):
		"""
		Set new function to execute inside thread.
		Function that is currently run is interrupted.
		"""

		if fun is self.__fun:
			return

		self.interrupt()
			
		if fun is None:	# unset function
			self.__lock.acquire() # halt thread
			self.__fun  = None
			self.__args = ()
		else:
			if not self.__lock.locked():
				self.__lock.acquire()

			self.__fun  = fun
			self.__args = args
			self.__lock.release()
	
	def unset_function(self):
		"""Interrupt function executed inside thread and
		wait for new function (set_function)"""
		self.interrupt()
		self.set_function(None)
	
	def interrupt(self):
		"Interrupt function executed inside thread"
		if self.__fun:
			# empty queue
			try:
				while True:
					self.__queue.get_nowait()
			except Queue.Empty:
				pass

			# send event
			self.__queue.put((self.__abort, None))

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


try:
	import Queue
	import thread
except ImportError:
	EventsSerializer = EventsSerializerTk
else:
	EventsSerializer = EventsSerializerThreads

