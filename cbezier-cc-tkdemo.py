# -*- coding: iso-8859-2 -*-
#
# Bezier curves intersection -- tkinter demo
#
# Wojciech Muła, http://www.mula.w.pl
# 15.02.2007
#
# Public domain
# modules cbezier2D & utils2D are available on my site

from Tkinter import *
from math import hypot

from cbezier2D import adaptive_split, is_flat2, is_flat1, is_flat3
from utils2D   import len_sqrt

import cbezier2D

class Dummy: pass
def main():
	state = Dummy()
	state.point = None	# persistent state
	
	# control points
	default_points = [
		( 50.0, 100.0),
		(100.0, 50.0),
		(150.0, 50.0),
		(200.0, 100.0),
	]
	state.points1 = default_points[:]
	state.points2 = [(x+100.0, y+100.0) for x, y in default_points]

	##########################################################
	# Setup interface
	root  = Tk()

	# Variables
	
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
	show_dots.set(False)

	points_count = StringVar()

	# Widgets
	canv  = Canvas(root, bg="white")
	bezier_curve1  = canv.create_line(0, 0, 0, 0)
	bezier_curve2  = canv.create_line(0, 0, 0, 0)
	canv.itemconfig(bezier_curve1, fill="red")
	canv.itemconfig(bezier_curve2, fill="blue")
	control_line1  = canv.create_line(state.points1)
	control_line2  = canv.create_line(state.points2)
	
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
	c1 = Checkbutton(frame4, text="show verts", variable=show_dots)
	Label(frame4, text="Common").pack(anchor=W)
	e4.pack()
	c1.pack(anchor=W)
	Label(frame4, textvariable=points_count).pack(anchor=W)
	
	def reset():
		state.points1 = default_points[:]
		state.points2 = [(x+100.0, y+100.0) for x, y in default_points]
		update()

	Button(frame4, text="Reset curve", command=reset).pack()

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
		canv.coords(control_line1,
			state.points1[0][0], state.points1[0][1],
			state.points1[1][0], state.points1[1][1],
			state.points1[2][0], state.points1[2][1],
			state.points1[3][0], state.points1[3][1]
		)
		canv.coords(control_line2,
			state.points2[0][0], state.points2[0][1],
			state.points2[1][0], state.points2[1][1],
			state.points2[2][0], state.points2[2][1],
			state.points2[3][0], state.points2[3][1]
		)
		p1 = [bezier_curve1]
		p2 = [bezier_curve2]
		r = 1

		try:
			state.dmin = max(1.0, float( dmin.get() ))
		except ValueError:
			state.dmin = 3.0

		if method.get() == 1:
			try:
				state.d1 = abs(float( d1.get() ))
			except ValueError:
				state.d1 = 0.01
			is_flat = method1
				
		elif method.get() == 2:
			try:
				state.d2 = abs(float( d2.get() ))
			except ValueError:
				state.d2 = 0.1
			is_flat = method2
		else:
			try:
				state.d3 = abs(float( d3.get() ))
			except ValueError:
				state.d3 = 0.2
			is_flat = method3

		tmp1 = adaptive_split(state.points1, is_flat)
		tmp2 = adaptive_split(state.points2, is_flat)

		sd = show_dots.get()
		for t, (x, y) in tmp1:
			p1.append(x)
			p1.append(y)
			if sd:
				canv.create_oval(
					x-r, y-r, x+r, y+r,
					fill="red", outline="red",
					tags="tmp"
				)
		for t, (x, y) in tmp2:
			p2.append(x)
			p2.append(y)
			if sd:
				canv.create_oval(
					x-r, y-r, x+r, y+r,
					fill="blue", outline="blue",
					tags="tmp"
				)

		canv.coords(*p1)
		canv.coords(*p2)

		crosspoints = cbezier2D.cc_intersections(
				state.points1,
				state.points2,
				is_flat)

		r = 3
		for u, v, P in crosspoints:
			x, y = P
			canv.create_oval(x-r, y-r, x+r, y+r, fill="black", outline="black", tags="tmp")
			
			# x, y = cbezier2D.point(state.points2, v)
			# canv.create_oval(x-r, y-r, x+r, y+r, fill="red", outline="red", tags="tmp")
			
			# x, y = cbezier2D.point(state.points1, u)
			# canv.create_oval(x-r, y-r, x+r, y+r, fill="blue", outline="blue", tags="tmp")
			
			
		
		points_count.set("%d/%d verts\n%d crosspoint(s)" % (len(tmp1), len(tmp2), len(crosspoints)))
		

	##########################################################
	# Setup interface: handlers
	def nearest_point(x, y):

		def np(points):
			nearest_d = 1000.0**2
			nearest_i = None
			for i, (xi, yi) in enumerate(points):
				dx = xi - x
				dy = yi - y
				d  = dx*dx + dy*dy
				if d < nearest_d:
					nearest_i = i
					nearest_d = d

			return nearest_i, nearest_d

		i1, d1 = np(state.points1)
		i2, d2 = np(state.points2)
		if i1 is None and i2 is None:
			return None
		elif i1 is None:
			return (2, i2)
		elif i2 is None:
			return (1, i1)
		else:
			if d1 <= d2:
				return (1, i1)
			else:
				return (2, i2)


	def motion(event):
		x = canv.canvasx(event.x)
		y = canv.canvasy(event.y)

		np = nearest_point(x, y)
		
		canv.delete('cp')
		if np is not None:
			n, i = np
			if n == 1:
				x, y = state.points1[i]
			else:
				x, y = state.points2[i]

			r  = 3
			canv.create_oval(x-r, y-r, x+r, y+r, fill="blue", tags=("tmp", "cp"))

	def press(event):
		x = canv.canvasx(event.x)
		y = canv.canvasy(event.y)
		try:
			state.curve, state.point = nearest_point(x, y)
		except TypeError:
			state.curve = None
			state.point = None

	def release(event):
		state.curve = None
		state.point = None
	
	def drag(event):
		if state.curve is None:
			return

		x = canv.canvasx(event.x)
		y = canv.canvasy(event.y)

		if state.curve == 1:
			state.points1[state.point] = (x, y)
		else:
			state.points2[state.point] = (x, y)

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
# vim: tw=0 ts=4 sw=4 nowrap
