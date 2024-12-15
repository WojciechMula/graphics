# -*- coding: iso-8859-2 -*-
#
# Author	: Wojciech Muła, wojciech_mula@poczta.onet.pl
# License	: BSD

__changelog__ = '''
8.10.2006
	- moved center_leafs outside TreeLayout2
	- simplified TreeLayout
5.10.2006
	- simplified TreeLayout2
4.10.2006
	- cleaning the code (moved demo code to the other file)
   9.2006
	- initial work
'''

def TreeLayout(node, x, space):
	assert node != None

	if node.childNodes:
		for child in node.childNodes:
			x = TreeLayout(child, x, space)

		node.cx = (node.firstChild.cx + node.lastChild.cx)/2
		return max(x, node.maxx())
	else:
		node.setminx(x + space)
		return node.maxx()


def TreeLayout2(node, space):
	if not node:	# empty tree
		return

	class Dummy: pass

	d = Dummy()
	d.levels = []

	def fill_rows(node, level):

		# add node to node's list assigned to certain level
		if len(d.levels) >= level+1:
			d.levels[level].append(node)

		else: # this level is visited first time
			d.levels.append([])
			d.levels[level] = [node]
	
		# each node has info about it position in d.levels table
		node.index = len(d.levels[level])-1
		node.level = level

		# place new node at end of the row
		if node.index > 0:
			prevnode = d.levels[node.level][node.index-1]
			node.setminx(prevnode.maxx() + space)
		else:
			node.setminx(0)	# first node

		# process node's children
		for child in node.childNodes:
			fill_rows(child, level+1)

	def do_layout():
		
		def translate_child(node, dx):
			for child in node.childNodes:
				translate_tree(child, dx)

		def translate_tree(node, dx):
			node.cx += dx
			for child in node.childNodes:
				translate_tree(child, dx)

		for row in reversed(d.levels[:-1]):
			for parent in row:
				if not parent.hasChildNodes():	# skip leafs
					continue
			
				# calucate desired center of node
				cx     = (parent.firstChild.cx + parent.lastChild.cx)/2
				dx     = cx - parent.cx
				if cx > parent.cx:
					# move dx units right nodes at parent level, starting
					# from the parent node
					row1 = d.levels[parent.level]
					for i in xrange(parent.index, len(row1)):
						row1[i].cx += dx
				elif cx < parent.cx:
					# move -dx units right subtrees of parent
					# and it's neightbours on right
					row1 = d.levels[parent.level]
					for i in xrange(parent.index, len(row1)):
						translate_child(row1[i], -dx)
					
	fill_rows(node, 0)
	do_layout()
#fed
	
def center_leafs(node):
	last = None
	for i, child in enumerate(node.childNodes):
		if child.hasChildNodes():
			if last == None:
				last = i
			else:
				j = last
				n = i - j
				if n > 1:
					n = float(n)
					a = node.childNodes[j].cx
					b = node.childNodes[i].cx
					for k in xrange(j+1, i):
						node.childNodes[k].cx = a + ((k-j)/n)*(b-a)
				last = i

	for child in node.childNodes:
		center_leafs(child)

# eof
# vim: ts=4 sw=4
