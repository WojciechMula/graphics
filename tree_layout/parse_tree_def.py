# -*- coding: iso-8859-2 -*-
#
# Author	: Wojciech Muła, wojciech_mula@poczta.onet.pl
# License	: BSD

__changelog__ = '''

11.10.2006
	- attribute 'name' isn't removed
 6.10.2006
 	- replaced functions tree_walk & callback with single
	  functions del_name_attr
27.09.2006:	
	- comments
	- order of creating, cloning and binding doesn't matter
'''

import re
import csv

# Syntax:
#
# 1. node = shape space params   # define new node
# 2. node1 = node2               # clone node
# 3. node1 -> node2 | node3 | .. # makes node2, node3, ... child nodes of node1
# regexps:

re_node_name	= re.compile("^[a-zA-Z][_a-zA-Z0-9]*$")
re_shape		= re.compile("^([a-z][_a-z0-9]+)\s+(.+)")

# a. empty lines are ignored
# b. lines starting with '#' are comments and they are ignored
# c. one node named root_name (param of fun) have to be defined
# d. case matters

sample = '''
	root	= circle "",  10
	A	= circle "A", 10
	B	= rectangle "B", 150, 20
	C	= circle "C", 10
	root -> A | B | C
	
	A_1   = circle "a", 8
	A_2   = A_1
	A_3   = rectangle "", 90, 25
	A    -> A_1 | A_2 | A_3
	
	C_2   = circle "c", 8
	C_1   = rectangle "", 90, 25
	C    -> C_1 | C_2
	
	da = circle "", 5
	db = da
	dc = da
	dd = da
	de = da
	df = da
	dg = da
	
	A_1 -> da | db | dc | dd
	A_3 -> de | df
	
	C_1 -> dg
'''

def parse_tree_def(string, root_name='root'):

	class Node:
		def __init__(self, classname, parameters, name):
			self.parentNode = None
			self.childNodes = []
			self.classname	= classname		# shape kind
			self.parameters = parameters	# additional params
			self.name       = name			# name

		def hasChildNodes(self):
			return len(self.childNodes) > 0

		def appendChild(self, node):
			if node.parentNode:
				raise ValueError("Node %s already binded to the tree" % node.name)
			else:
				self.childNodes.append(node)
				node.parentNode = self

	
	nodes	= {}
	clone	= []	# list of clone node actions
	bind	= []	# list of bind child actions

	# first pass (parse) - define nodes, and remember which nodes
	# have to be cloned or binded
	for line in string.splitlines():
		line = line.strip()
		if not line:			# ignore empty lines
			continue
		elif line[0] == '#':	# ignore comments
			continue

		pos_eq  = line.find('=')
		pos_arr = line.find('->')
		if pos_eq > -1:
			i = pos_eq
			L = line[:i].rstrip()
			R = line[i+1:].lstrip()

			m1 = re_node_name.match(L)
			m2 = re_node_name.match(R)
			m3 = re_shape.match(R)
			if m1 and m2:	# node1 = node2 (rule 2)
				node1_name = L
				node2_name = R
				if node1_name in nodes:
					raise KeyError("Node %s already defined" % node1_name)
				else:
					# query 'clone node' action
					clone.append( (node1_name, node2_name) )

			elif m1 and m3:	# node2 = shape ... (rule 1)
				node_name = L
				if node_name in nodes:
					raise KeyError("Node %s already defined" % node_name)
				else:
					reader    = csv.reader([m3.group(2)])
					classname = m3.group(1)
					params    = list(reader)[0]
					params    = tuple(p.strip() for p in params)

					nodes[node_name] = Node(classname, params, node_name)
			else:
				raise ValueError("Syntax Error: '%s'" % line)

		elif pos_arr > -1:
			i = pos_arr
			L = line[:i].rstrip()
			R = line[i+2:].split('|')

			parent_name = L
			for name in R:
				name  = name.strip()
				# query 'bind node' action
				bind.append( (parent_name, name) )
				
		else:
			raise ValueError("Syntax error: '%s'" % line)
	
	# second pass (clone nodes)
	for node1_name, node2_name in clone:
		try:
			node = nodes[node2_name]
			nodes[node1_name] = Node(node.classname, node.parameters, node1_name)
		except KeyError:
			raise KeyError("Can't clone: node %s not defined" % node2_name)
	
	if root_name not in nodes:
		raise KeyError("You have to define root node called '%s'" % root_name)

	# third pass ("connect the dots")
	for parent_name, child_name in bind:
		try:
			parent = nodes[parent_name]
		except KeyError:
			raise KeyError("Parent node %s not defined" % parent_name)
		try:
			child = nodes[child_name]
		except KeyError:
			raise KeyError("Child node %s not defined" % child_name)

		parent.appendChild(child)
	
	# fourth pass (check for unconnected nodes)
	for node in nodes.itervalues():
		if node.parentNode == None and len(node.childNodes) == 0:
			raise ValueError("Node %s doesn't belong to the tree" % node.name)

	# return root of our tree
	return nodes[root_name]
#fed

# vim: ts=4 sw=4
