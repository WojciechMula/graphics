from Tkinter import *
from random  import random

class Node:
	pass

def random_tree(h_max, h):
	if h == h_max:
		return None
	
	node = Node()
	if random() > 0.2:
		node.left = random_tree(h_max, h+1)
	else:
		node.left = None
	if random() > 0.2:
		node.right = random_tree(h_max, h+1)
	else:
		node.right = None
	
	return node


def get_x(h, h_max, S, p):
	d   = h_max - h
	x_s = (2**d - 1)*S
	S_d = (2**(d+1))*S
	return x_s + p*S_d


def do_layout(node, h, h_max, S, p):
	if node is None:
		return
	
	x = get_x(h, h_max, S, p)
	x1 = get_x(h+1, h_max, S, 2*p)
	x2 = get_x(h+1, h_max, S, 2*p+1)
	
	y = h*40 + 100

	canv.create_oval(x-r, y-r, x+r, y+r, fill="white")
		
	

	if node.left:
		item = canv.create_line(x, y, x1, y + 40)
		canv.tag_lower(item, ALL)

		do_layout(node.left, h+1, h_max, S, 2*p)
	
	if node.right:

		item = canv.create_line(x, y, x2, y + 40)
		canv.tag_lower(item, ALL)
		do_layout(node.right, h+1, h_max, S, 2*p+1)


if __name__ == '__main__':
	root = Tk()
	canv = Canvas()
	canv.pack(fill=BOTH, expand=1)

	r 	= 7 	# node radius
	h_max	= 6
	tree	= random_tree(h_max, 0)

	do_layout(tree, 0, h_max, r/2.0 + 1.0, 0)

	# move drawing to left-upper corner
	x1, y1, x2, y2 = canv.bbox(ALL)
	canv.scan_mark(int(0), int(0))
	canv.scan_dragto(int(-x1), int(-y1), 1)

	root.mainloop()

# eof
