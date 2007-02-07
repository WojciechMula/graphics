# -*- coding: iso-8859-2 -*-
#
# Adaptive split (subdivide) of Bezier curve -- tkinter demo
#
# Three different methods are used to determine
# flattenes of Bezier curve
#
# Wojciech Muła, http://www.mula.w.pl
# 5-8.02.2007
#
# Public domain
# modules cbezier2D & utils2D are available on my site

from Tkinter import *
from math import hypot

from cbezier2D import adaptive_split, is_flat2, is_flat1, is_flat3
from utils2D import len_sqrt

class Dummy: pass
def main():
	# control points
	default_points = [
		( 50.0, 100.0),
		(100.0, 50.0),
		(150.0, 50.0),
		(200.0, 100.0),
	]
	points = default_points[:]

	##########################################################
	# Setup interface
	root  = Tk()

	# Variables
	state = Dummy()
	state.point = None	# persistent state
	
	method = IntVar()	# method (1-3) used to detrmin flatteness of Bcurve
	
	d1 = StringVar()	# method 1: min distance
	d2 = StringVar()	# method 2: min distance
	d3 = StringVar()	# method 3: min distance
	dmin = StringVar()	# all methods: min length of segment AD

	d1.set("0.001")
	d2.set("0.1")
	d3.set("0.2")
	dmin.set("3.0")

	# text displayed on status bar
	status = StringVar()
	status.set("Select entry to get short description")
	def set_status(string):
		def foo(*args):
			status.set(string)
		return foo
	unset_status = set_status(status.get())

	show_dots = BooleanVar() # show dots
	show_dots.set(True)

	# Widgets
	canv  = Canvas(root, bg="white")
	bezier_curve  = canv.create_line(0, 0, 0, 0)
	canv.itemconfig(bezier_curve, fill="red")
	control_line  = canv.create_line(points)
	
	frame = Frame(root, padx=3, pady=3) # main frame

	frame1 = Frame(frame, relief=RIDGE, bd=2, padx=5, pady=5)
	r1 = Radiobutton(frame1, text="method 1", value=1, variable=method)
	e1 = Entry(frame1, textvariable=d1)
	r1.pack(anchor=W)
	e1.pack()

	frame2 = Frame(frame, relief=RIDGE, bd=2, padx=5, pady=5)
	r2 = Radiobutton(frame2, text="method 2", value=2, variable=method)
	e2 = Entry(frame2, textvariable=d2)
	r2.pack(anchor=W)
	e2.pack()
	
	frame3 = Frame(frame, relief=RIDGE, bd=2, padx=5, pady=5)
	r3 = Radiobutton(frame3, text="method 3", value=3, variable=method)
	e3 = Entry(frame3, textvariable=d3)
	r3.pack(anchor=W)
	e3.pack()

	frame4 = Frame(frame, relief=RIDGE, bd=2, padx=5, pady=5)
	e4 = Entry(frame4, textvariable=dmin)
	c1 = Checkbutton(frame4, text="show_dots", variable=show_dots)
	Label(frame4, text="Common").pack(anchor=W)
	e4.pack()
	c1.pack(anchor=W)

	# Pack widgets

	frame1.pack(side=TOP)
	frame2.pack(side=TOP)
	frame3.pack(side=TOP)
	frame4.pack(side=TOP)

	Label(root, textvariable=status).pack(side=BOTTOM)
	frame.pack(side=LEFT, fill=Y)
	canv. pack(side=LEFT, fill=BOTH, expand=1)

	
	
	##########################################################
	# Main functions
	def method1(A, B, C, D):
		flat, l_AD = is_flat1((A, B, C, D), state.d1)
		return flat or l_AD < state.dmin

	def method2(A, B, C, D):
		l_AD = len_sqrt(A, D)
		return is_flat2((A, B, C, D), state.d2) or l_AD < state.dmin
	
	def method3(A, B, C, D):
		flat, l_AD, d1, d2 = is_flat3((A, B, C, D), d=state.d3)

		return flat or l_AD < state.dmin

	def update(*args):
		canv.delete('tmp')
		canv.coords(control_line,
			points[0][0], points[0][1],
			points[1][0], points[1][1],
			points[2][0], points[2][1],
			points[3][0], points[3][1]
		)
		p = [bezier_curve]
		r = 2

		try:
			state.dmin = max(1.0, float( dmin.get() ))
		except ValueError:
			state.dmin = 3.0

		if method.get() == 1:
			try:
				state.d1 = abs(float( d1.get() ))
			except ValueError:
				state.d1 = 0.01
				
			tmp = adaptive_split(points, method1)
		elif method.get() == 2:
			try:
				state.d2 = abs(float( d2.get() ))
			except ValueError:
				state.d2 = 0.1

			tmp = adaptive_split(points, method2)
		else:
			try:
				state.d3 = abs(float( d3.get() ))
			except ValueError:
				state.d3 = 0.2
			tmp = adaptive_split(points, method3)

		sd = show_dots.get()
		for t, (x, y) in tmp:
			p.append(x)
			p.append(y)
			if sd:
				canv.create_oval(
					x-r, y-r, x+r, y+r,
					fill="red", outline="red",
					tags="tmp"
				)

		canv.coords(*p)
		

	##########################################################
	# Setup interface: handlers
	def nearest_point(x, y):
		nearest_d = 100.0**2
		nearest_i = None
		for i, (xi, yi) in enumerate(points):
			dx = xi - x
			dy = yi - y
			d  = dx*dx + dy*dy
			if d < nearest_d:
				nearest_i = i
				nearest_d = d

		return nearest_i


	def motion(event):
		x = canv.canvasx(event.x)
		y = canv.canvasy(event.y)

		i = nearest_point(x, y)
		
		canv.delete('cp')
		if i is not None:
			x, y = points[i]
			r    = 3
			canv.create_oval(x-r, y-r, x+r, y+r, fill="blue", tags=("tmp", "cp"))

	def press(event):
		x = canv.canvasx(event.x)
		y = canv.canvasy(event.y)
		state.point = nearest_point(x, y)

	def release(event):
		state.point = None
	
	def drag(event):
		if state.point is None:
			return

		x = canv.canvasx(event.x)
		y = canv.canvasy(event.y)

		points[state.point] = (x, y)
		update()


	##########################################################
	# Setup interface: bind events
	canv.bind('<Motion>',		motion)
	canv.bind('<ButtonPress-1>',	press)
	canv.bind('<ButtonRelease-1>',	release)
	canv.bind('<B1-Motion>',	drag)
	e1.bind('<Return>', update)
	e2.bind('<Return>', update)
	e3.bind('<Return>', update)
	e4.bind('<Return>', update)

	method.trace_variable('w', update)
	method.set(1)
	show_dots.trace_variable('w', update)

	e1.bind('<FocusIn>', set_status("(|AB| + |BC| + |CD|) / |AD| <= 1 + value"))
	e2.bind('<FocusIn>', set_status("Manhattan distance of |B - 0.5(A+C)| and |C - 0.5(B+D)| are less then value"))
	e3.bind('<FocusIn>', set_status("Distances of B and C from segment AD are less then value"))
	e4.bind('<FocusIn>', set_status("Guard: minimum length of segment AD"))
	e1.bind('<FocusOut>', unset_status)
	e2.bind('<FocusOut>', unset_status)
	e3.bind('<FocusOut>', unset_status)
	e4.bind('<FocusOut>', unset_status)

	root.mainloop()

if __name__ == '__main__':
	main()

# eof
# vim: tw=0 nowrap
