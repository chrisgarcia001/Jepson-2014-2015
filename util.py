# --------------------------------------------------------------------------------------
# Author: cgarcia@umw.edu
# About: This file contains utility functions and classes used throughout the other 
#        code files.
# --------------------------------------------------------------------------------------

import calendar
import time
import random as rd
import math

# Build a dict list representation from user and interaction attribute lists.
def dict_list_representation(user_atts, inter_atts):
	dlrep = []
	headings = None
	rows = map(lambda (x, y): x + y, zip(user_atts, inter_atts))
	for row in rows:
		if headings == None:
			headings = map(lambda x: 'H' + str(x), range(1, len(row) + 1))
		dlrep.append(dict(zip(headings, row)))
	return dlrep

# Get the top n items in ascending order.
# Param items: the items
# Param n: the number of top items to return
# Param accessor_f: a function to access the comparison metric from each item.
def top_n(items, n, accessor_f = lambda x: x):
	top = []
	for item in items:
		if len(top) == 0 and n > 0:
			top.append(item)
		else:
			i = 0
			while i < len(top) and accessor_f(item) > accessor_f(top[i]):
				i += 1
			top.insert(i, item)
			if len(top) > n:
				del(top[0])
	top.reverse()
	return top
	
# For a given pattern and list of patterns, return the closest partial match from the list.	
# Param ifzeromatches: what to return if no partial matches.
# Param ignore_matches: A list of values - any present in a position in 2 patterns will not be counted as a match
# Param patlist_accessor: pat_list may be a list of objects which contain a pattern (rather than just the patterns).
#                         patlist_accessor will get the pattern out of an object.
def best_match(pat, pat_list, ifzeromatches=None, 
					ignore=[None], patlist_accessor=lambda x: x):
	em = lambda p1,p2: len(filter(lambda (x,y): not(y in ignore) and x != y, zip(p1, patlist_accessor(p2)))) == 0
	cm = lambda p1,p2: len(filter(lambda (x,y): x == y, zip(p1, patlist_accessor(p2))))
	ms = map(lambda p: (p, cm(pat, p)), filter(lambda p: em(pat, p), pat_list))
	if  len(ms) == 0:
		return ifzeromatches
	return top_n(ms, 1, lambda x:x[1])[0][0]
	
	
# Get the current time in seconds since the epoch.	
def curr_time():
	return calendar.timegm(time.gmtime())

# For a given value and list of cumulative-sum values, return the index
# corresponding to the smallest cumulative value >= given value.
# Param val: a value
# Param items: A list of numbers in ascending order. Value at position i corresponds to cumulative
#              weighted sum of all values from item 0,1,..i. 	
def cumulative_bin_search(val, items):
	min_ind = 0
	max_ind = len(items) - 1
	while max_ind  - min_ind > 1:
		midpt = min_ind + ((max_ind - min_ind) / 2)
		if val <= items[midpt]:
			max_ind = midpt
		else:
			min_ind = midpt
	if max_ind != min_ind and val <= items[min_ind]:
		return min_ind
	return max_ind

# For row-based data, split into random specified fractions.
def split_data(rows, *fracs):
	total = len(rows)
	curr_rows = list(rows)
	splits = []
	for f in fracs:
		rand_inds = rd.sample(range(len(curr_rows)), min(int(math.ceil(f * total)), len(curr_rows)))
		rem_inds = filter(lambda i: not(i in rand_inds), range(len(curr_rows)))
		splits.append(map(lambda i: curr_rows[i], rand_inds))
		curr_rows = map(lambda i: curr_rows[i], rem_inds)
	return tuple(splits)
	
	
# Return the distinct objects in a list.
def distinct(items):
	s = list(set(map(lambda x: str(x), items)))
	return map(lambda x: eval(x), s)

# For a list of lists, 	
def cartesian_prod(list_of_lists):
	if len(list_of_lists) == 1:
		return map(lambda x: [x], list_of_lists[0])
	rest = cartesian_prod(list_of_lists[1:])
	return reduce(lambda w, x: w + x, map(lambda y: map(lambda z: [y] + z, rest), list_of_lists[0]))

# For a list of tuples, reverses
def unzip(tuples):
	if (len(tuples) > 0):
		cols = []
		for i in range(len(tuples[0])):
			cols.append(map(lambda x: x[i], tuples))
		return cols
	return []

# Reads a CSV as a list of rows	
def read_csv(filename, include_headers = True, sep = ',', cleanf = lambda x: x, ignore_lines = None):
	fl = open(filename)
	txt = cleanf(fl.read())
	fl.close()
	start_pos = 0 if include_headers else 1
	lines = map(lambda y: y.strip(), txt.split("\n"))[start_pos:]
	lines = filter(lambda x: len(map(lambda y: not(y in ' ,'), x)) > 0, lines)
	if ignore_lines != None:
		lines = filter(lambda x: not(x.startswith(ignore_lines)), lines)
	return map(lambda x: x.split(sep), lines)
	
# Reads a CSV as an dict of args
def read_csv_args(filename, sep = ',', cleanf = lambda x: x, ignore_lines = None):
	lines = read_csv(filename, True, ',', cleanf, ignore_lines)
	return dict(map(lambda line: (line[0].strip(), line[1].strip()), lines))

# All params come in as strings. This will evaluate them into their 
# proper object forms. Multi-attribute values come in as tuples - these
# should be separated by ";" rather than "," since CSV files cannot
# contain commas as data. Min/Max ranges can also be specified as "min-max",
# and this will be evaluated into a tuple (min, max)
# Examples: parse_param_val("3") => 3
#           parse_param_val("2; 3; 4") => (2,3,4)
#           parse_param_val("5-10") => (5, 10)
def parse_param_val(string):
	if len(filter(lambda x: x == '-', string)) > 0:
		if string[len(string) - 1] != ')':
			string += ')'
		if string[0] != '(':
			string = '(' + string
	return eval(string.replace(' ', '').replace('-', ';').replace(';', ','))

# Parses all params in a param dict.
def parse_params(params):
	nd = {}
	for (k, v) in params.items():
		try:
			nd[k] = parse_param_val(v)
		except:
			nd[k] = v
	return nd

# A shorthand way to read a set of CSV params.
def read_params(csv_filename, sep = ',', cleanf = lambda x: x, ignore_lines = None):
	return parse_params(read_csv_args(csv_filename, sep, cleanf, ignore_lines))
	
	
# Write a text file	
def write_file(text, filename):
	f = open(filename, "w")
	f.write(text)
	f.close()

# Writes a matrix (2D list) to a CSV file.
def write_csv(matrix, filename, sep = ','):
	text = reduce(lambda x,y: x + "\n" + y, map(lambda row: sep.join(map(lambda z: str(z), row)), matrix))
	write_file(text, filename)
	
# This class is essentially a dict, but it 
# allows using arbitrary objects (like lists) as keys.
class Cache(object):
	def __init__(self, *args):
		self.h = {}
		
	def __setitem__(self, key, val):
		self.h[str(key)] = val
	
	def __getitem__(self, key):
		return self.h[str(key)]
			
	def has_key(self, key):
		return self.h.has_key(str(key))
		
	def items(self):
		its = self.h.items()
		itms = []
		for (k, v) in its:
			try:
				itms.append((eval(k), v))
			except:
				itms.append((k, v))
		return itms
	
	def keys(self):
		ks = []
		for k in self.h.keys():
			try:
				ks.append(eval(k))
			except:
				ks.append(k)
		return ks
		
	def values(self):
		return self.h.values()
		
		