from math    import hypot, sin, cos, pi
from random  import randint, random

from utils2D import set_length, add, sub

def hook_force((x1, y1), (x2, y2), l=50.0):
	return -hypot(x1-x2, y1-y2)

def culomb_force((x1, y1), (x2, y2), k=1000):
	r = max(hypot(x1-x2, y1-y2), 0.01)
	return k/(r*r)


A = 'a'
B = 'b'
C = 'c'
D = 'd'
E = 'e'
F = 'f'
G = 'g'
H = 'h'
I = 'i'
J = 'j'
K = 'k'
L = 'l'
graph = {
	A: [B, E, F],
	B: [A, C, E, F],
	C: [B, D, E],
	D: [C, G],
	E: [A, B, C, F],
	F: [A, B, E],
	G: [D]
}

graph3 = {
	A: [B, E, F],
	B: [A, C, E, F],
	C: [B, D],
	D: [C, G],
	E: [A, B, C, F],
	F: [A, B, E],
	G: [D, F]
}

graph2 = {
	A: [B, E, C, F],
	B: [A, E, D, G],
	C: [A, E, F],
	D: [B, H, E],
	E: [C, B, G, H, D],
	F: [A, C, B],
	G: [E, D, B],
	H: [E, D],
	I: [G, J, D],
	J: [I, K, A],
	K: [L, J, A],
	L: [K, A, B, E],
}

graph4 = {
	A: [B],
	B: [C],
	C: [D],
	D: [E],
	E: [F],
	F: [G],
	G: [H],
	H: [I],
	I: [J],
	J: [K],
	K: [L],
	L: [A],
}       

graph5 = {
	A: [B, C, E],
	B: [C],
	C: [D, L],
	D: [E],
	E: [F, A],
	F: [G],
	G: [H],
	H: [I, L],
	I: [J, L, F],
	J: [K],
	K: [L],
	L: [A],
}

graph6 = {
	A: [B],
	B: [C],
	C: [D, E],
	D: [C],
	E: [F],
	F: [G],
	G: [H],
	H: [I],
	I: [J,K],
	J: [I],
	K: [L],
	L: [K]
}

def fix_graph(graph):
	for node1, connected in graph.iteritems():
		for node2 in connected:
			if node1 not in graph[node2]:
				graph[node2].append(node1)
	return graph

fix_graph(graph)
fix_graph(graph2)
fix_graph(graph3)
fix_graph(graph4)
fix_graph(graph5)

def run(graph):
	position = {}
	velocity = {}
	items    = {}
	r = 5
	n  = len(graph)
	da = 2*pi/n
	for i, node in enumerate(graph):
		x, y = float(randint(-6000, 6000)), float(randint(-6000, 6000))
		x, y = float(randint(-60, 60)), float(randint(-60, 60))
		position[node] = x, y
		velocity[node] = (0.01, 0.0)
	
	def avg():
		dx = 0.0
		dy = 0.0
		for x, y in velocity.itervalues():
			dx += abs(x)
			dy += abs(y)

		return dx*dx + dy*dy

	avg_prev = avg()*10.0
	br.set(True)
	file = open('series', 'w')
	iters = 0
	totiters = 0

	fr = friction.get()/100.0
	mul = 1.0
	while br.get():
		avg_curr = avg()
		info.set("avg = %0.12f, mul=%f" % (avg_curr, mul))
		file.write("%0.12f\n" % avg_curr)
		if avg_curr < 0.001 and False:
			#print "avg_curr = %f, iters = %d" % (avg_curr, totiters)
			info.set("%s, iterations = %d" % (info.get(), totiters))
			break

		if abs(avg_curr-avg_prev) < 0.00001 and avg_curr > 1.0 and False:
			print "abs(avg_curr-avg_prev) =", abs(avg_curr-avg_prev)
			for node in graph:
				position[node] = float(randint(-600, 600)), float(randint(-600, 600))
			iters = 0

		if avg_curr > 1e3:
			mul *= 0.95

		if iters > 3000:
			print "too many iterations"
			for node in graph:
				position[node] = float(randint(-6000, 6000)), float(randint(-6000, 6000))
			iters = 0

		avg_prev = avg_curr
		iters += 1
		totiters += 1

		fc = forcec.get()
		for node1 in graph:
			Fx, Fy = velocity[node1]
			Fx *= fr
			Fy *= fr
			for node2 in graph:
				if node1 == node2: continue

				f      = culomb_force(position[node1], position[node2], fc)
				fx, fy = set_length(sub(position[node1], position[node2]), f)

				Fx += fx
				Fy += fy
			
			velocity[node1] = (Fx, Fy)

		l  = length.get()
		fc = force.get()
		for node1 in graph:
			Fx, Fy = velocity[node1]
			for node2 in graph[node1]:
				f      = hook_force(position[node1], position[node2], l)*fc*mul
				fx, fy = set_length(sub(position[node1], position[node2]), f)

				Fx += fx
				Fy += fy

			velocity[node1] = (Fx, Fy)

		for node in graph:
			x,  y  = position[node]
			Fx, Fy = velocity[node]
			x += Fx
			y += Fy
			position[node] = (x, y)
		


		canv.delete(ALL)
		for node in graph:
			x, y = position[node]
			items[node] = canv.create_oval(x-r, y-r, x+r, y+r, fill="green")

		for node in graph:
			x, y = position[node]
			for node2 in graph[node]:
				xi, yi = position[node2]
				canv.create_line(x, y, xi, yi, tags='line')
			
			canv.coords(items[node], x-r, y-r, x+r, y+r)

		for node in graph:
			canv.tag_raise(items[node], ALL)

		see(canv, ALL)
		canv.update()

	file.close()
	br.set(True)
		

if __name__ == '__main__':
	def see(canvas, item):
		x1, y1, x2, y2 = canvas.bbox(item)
		cx = (x1+x2)/2
		cy = (y1+y2)/2

		xo = canvas.canvasx(0)
		yo = canvas.canvasy(0)
		w  = canvas.winfo_width()
		h  = canvas.winfo_height()
		
		canvas.scan_mark(int(cx), int(cy))
		canvas.scan_dragto(int(xo + w/2), int(yo + h/2), 1)
	
	from Tkinter import *

	root = Tk()
	canv = Canvas(root, bg='white')
	br = BooleanVar()
	br.set(True)
	frame = Frame(root)
	frame.pack(side=BOTTOM)
	Button(frame, text="Graph 1", command=lambda: run(graph)).pack(side=LEFT)
	Button(frame, text="Graph 2", command=lambda: run(graph2)).pack(side=LEFT)
	Button(frame, text="Graph 3", command=lambda: run(graph3)).pack(side=LEFT)
	Button(frame, text="Graph 4", command=lambda: run(graph4)).pack(side=LEFT)
	Button(frame, text="Graph 5", command=lambda: run(graph5)).pack(side=LEFT)
	Button(text="Stop", command=lambda: br.set(False)).pack(side=BOTTOM)
	info = StringVar()
	info.set("hello!")
	
	friction = DoubleVar(root)
	friction.set(0.7)
	Scale(root, variable=friction, digits=3, from_=0.0, to=1.0, resolution=0.001, orient=HORIZONTAL, length=500, label="friction").pack(side=BOTTOM)

	length = DoubleVar(root)
	length.set(50.0)
#	Scale(root, variable=length, digits=3, from_=1.0, to=150.0, resolution=0.5, orient=HORIZONTAL, length=500, label="spring length").pack(side=BOTTOM)

	force = DoubleVar(root)
	force.set(0.01)
	Scale(root, variable=force, digits=3, from_=0.0, to=1.0, resolution=0.001, orient=HORIZONTAL, length=500, label="Hook force coef").pack(side=BOTTOM)
	
	forcec = DoubleVar(root)
	forcec.set(10000)
	Scale(root, variable=forcec, digits=3, from_=1.0, to=100000.0, orient=HORIZONTAL, resolution=1000, length=500, label="Culomb force coef").pack(side=BOTTOM)
	
	Label(textvariable=info).pack(side=TOP, fill=X)
	
	
	canv.pack(fill=BOTH, expand=1)
	root.focus_set()
	root.bind('<Escape>', lambda _: root.quit())
	root.mainloop()

# vim: ts=4 sw=4
