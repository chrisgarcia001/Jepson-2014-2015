# --------------------------------------------------------------------------------------
# Author: cgarcia@umw.edu
# About: This file provides a reference implementation of the nearest-neighbor 
#        interaction design algorithm.
# --------------------------------------------------------------------------------------

import util as ut
import random as rd

# -------------------- UTIL FUNCTIONS/SIMILARITY MEASURES ---------

# A very simple similarity measure: count of number of attribute 
# values in common between v1 and v2.	
def match_count(v1, v2):
	return len(filter(lambda (x, y): x == y, zip(v1, v2)))
	
# Aggregates (attribute, similarity) tuples using specified weighting function.
# Normalized att tuples are list in format [(att. value, similarity score)].
# weight_f is function of form f: similarity -> R+
# Returns: a dict of form {att_val: total_weight}
def weighted_agg(normalized_att_tuples, weight_f = lambda s: 1):
	h = {}
	for (av, s) in normalized_att_tuples:
		if not(h.has_key(av)):
			h[av] = 0
		h[av] += weight_f(s)
	return h

# -------------------- Attribute Selectors and Selector Builders -	
# Each attribute selector takes a list of positive and negative 
# normalized attribute values and returns a single attribute value.
# An attribute selector builder constructs such a function.

# Builds a weighted mode selector on the positive attributes only, 
# using the specified weighting function. 
def build_weighted_mode_selector(weight_f = lambda x: 1):
	return lambda pos, neg: ut.top_n(weighted_agg(pos, weight_f).items(), 1, lambda (a, v): v)[0][0]	

# Builds a weighted maximum positive proportion selector, 
# using the specified weighting function. 
def build_weighted_max_pos_proportion_selector(weight_f = lambda x: 1):
	def wps(pos, neg):
		pv = weighted_agg(pos, weight_f)
		nv = weighted_agg(neg, weight_f)
		f = lambda key: float(pv[key]) / float(pv[key]) + float(nv[key]) if key in nv.keys() else 1.0
		return map(lambda x: (x, f(x)), pv.keys())
	return lambda p, n: ut.top_n(wps(p, n), 1, lambda (a, v): v)[0]

	
# -------------------- OPTIMIZER CLASS ----------------------------
class KNNOptimizer(object):
	def __init__(self):
		self.data = [] # Aggregation of [(user, [pos msgs] [neg msgs]),..}
		self.similarity_f = None
		self.num_msg_attributes = 0
		self.cache = ut.Cache()
	
	# A data row is a (user, msg, response) tuple
	def set_data_rows(self, data_rows):
		self.cache = ut.Cache()
		data = ut.Cache()
		for (u, m, r) in data_rows:
			if not(data.has_key(u)):
				data[u] = (u, [], [])
			_, pos, neg = data[u]
			if r == 1:
				pos.append(m)
			else:
				neg.append(m)
		self.data = data.values()
		if len(data_rows) > 0:
			self.num_msg_attributes = len(data_rows[0][1])
	
	# Set the distance calculation function.
	# A similarity_f is a function f : user X user -> R+
	def set_similarity_f(self, similarity_f):
		self.similarity_f = similarity_f
	
	# Param neighbors: a list of tuples of form: [([message], similarity)]
	# Returns: set of parsed messages of form [(av1, similarity), (av2, similarity)...]
	def normalize(self, neighbors):
		rows = []
		for (msgs, sim) in neighbors:
			for msg in msgs:
				rows.append(map(lambda av: (av, sim), msg))
		return rows
			
	# Finds the k-nearest-neighbours for a given user, k, and response class.
	# Returns parsed knn-tuples: ([pos. parsed message], [neg. parsed message])
	# where a parsed message is of form [(av1, similarity), (av2, similarity)...]
	def knn(self, user, k):
		if not(self.cache.has_key(user)):
			nbs = map(lambda (u, p, n): (u, p, n, self.similarity_f(user, u)), self.data)
			nn = ut.top_n(nbs, k, lambda (u,p,n,s): s)
			pos = self.normalize(map(lambda (u,p,n,s): (p,s), nn))
			neg = self.normalize(map(lambda (u,p,n,s): (n,s), nn))
			self.cache[user] = (pos, neg)
		return self.cache[user]
	
	# Constructs the optimal message for the user given k and the attribute 
	# selector function. The attribute selector function is of form
	# f: <positive normalized att. tuples> X <neg. normalized att tuples> -> att value
	def optimize(self, user, k, att_selector_f):
		pos, neg = self.knn(user, k)
		if len(pos) == 0:
			u1, p1, n1 = rd.sample(filter(lambda (u2, p2, n2): len(p2) > 0, self.data), 1)[0]
			return rd.sample(p1, 1)[0]
		msg = []
		for i in range(self.num_msg_attributes):
			msg.append(att_selector_f(map(lambda x: x[i], pos), map(lambda x: x[i], neg)))
		return msg
	
	# Using the specified calibration data and response function,
	# returns the best k in range [min_k, max_k].
	# Calibration data is a set of users
	# att_selector is function of form f: <positive normalized att. tuples> X <neg. normalized att tuples> -> att value
	# A response function is of form f: user X message -> {0 | 1}
	def find_best_k(self, calibration_data, min_k, max_k, att_selector_f, response_f):
		k = min_k
		best_k = min_k
		best_resp_rate = 0.0
		while k <= max_k:
			get_response = lambda u: response_f(u, self.optimize(u, k, att_selector_f))
			resp_rate = float(sum(map(get_response, calibration_data))) / float(len(calibration_data))
			if resp_rate > best_resp_rate:
				best_k = k
				best_resp_rate = resp_rate
			k += 1
		return best_k
		
	
