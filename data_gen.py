# --------------------------------------------------------------------------------------
# Author: cgarcia@umw.edu
# About: This file provides data generation capabilities and simulated responses
#        for use in executing scenarios.
# --------------------------------------------------------------------------------------

import random as rd
import util as ut

class DataGenerator(object):
	def __init__(self):
		self.baseline_response_prob = 0.1
		self.user_attrs = [] # A list of (name, [levels])
		self.inter_attrs = [] # A list of (name, [levels])
		self.propensities = [] # A list of ([uatt1_val, uatt2_val,...iatt1_val, iatt2_val..], probability)
		self.prevs = [] # A list of ([uatt1_val, uatt2_val...uattn_val], frequency)
	
	# Set the baseline response probability.
	def set_baseline_response_prob(self, prob):
		self.baseline_response_prob = prob
	
	# An attribute has a name and list of levels.
	def add_user_attr(self, name, levels):
		self.user_attrs.append((name, levels))
	
	# Same as above. It is assumed that user and interaction
	# attributes have unique names.
	def add_inter_attr(self, name, levels):
		self.inter_attrs.append((name, levels))
		
	# Generates and adds a set of random user attributes.
	def add_random_user_attrs(self, ncats, min_levels, max_levels, nconts=0, min_min=0, max_min=0, min_max=0, max_max=0):
		atts = self.gen_random_attrs('UA_', ncats, min_levels, max_levels, 
										nconts, min_min, max_min, min_max, max_max)
		for (name, levels) in atts:
			self.add_user_attr(name, levels)
	
	# Generates and adds a set of random interaction/message attributes.
	def add_random_inter_attrs(self, ncats, min_levels, max_levels, nconts=0, min_min=0, max_min=0, min_max=0, max_max=0):
		atts = self.gen_random_attrs('IA_', ncats, min_levels, max_levels, 
										nconts, min_min, max_min, min_max, max_max)
		for (name, levels) in atts:
			self.add_inter_attr(name, levels)
	
	# The propensity for a given user X and interaction Y is the probability
	# that X responds given Y. This function allows specification of specific
	# attribute patterns to respond. A combined pattern is a dict of user and/or 
	# interactions with specific values. Default propensities are baseline
	def set_propensity(self, combined_pattern, prob):
		attnames = self.allatt_names()
		arr_pattern = map(lambda x: None, range(len(attnames)))
		i = 0
		for att in attnames:
			for (attr, val) in combined_pattern.items():
				if att == attr:
					arr_pattern[i] = val
			i += 1
		self.propensities.append((arr_pattern, prob))
	
	# Set propensity for a specific user/inter pair.
	def set_user_inter_propensity(self, user_template, inter_template, prob):
		self.set_propensity(dict(user_template.items() + inter_template.items()), prob)
	
	# Add n random propensities for min/max numbers of user/interaction attributes with prob in specified range.
	# Returns: a pair (user templates, interaction templates)
	def set_random_propensities(self, n, min_user_atts, max_user_atts, min_inter_atts, max_inter_atts, min_prob, max_prob):
		uatts = []
		iatts = []
		for reps in range(n):
			prop = {}
			uprop = {}
			iprop = {}
			u = rd.sample(self.user_attrs, rd.randint(min_user_atts, min_user_atts))
			i = rd.sample(self.inter_attrs, rd.randint(min_inter_atts, max_inter_atts))
			for (att, levels) in u:
				if type(levels) == type([]):
					prop[att] = rd.sample(levels, 1)[0]
				else:
					(low, hi) = levels
					prop[att] = uniform(low, hi)
				uprop[att] = prop[att]
			for (att, levels) in i:
				if type(levels) == type([]):
					prop[att] = rd.sample(levels, 1)[0]
				else:
					(low, hi) = levels
					prop[att] = uniform(low, hi)
				iprop[att] = prop[att]
			uatts.append(uprop)
			iatts.append(iprop)
			self.set_propensity(prop, rd.uniform(min_prob, max_prob))
		return (uatts, iatts)
	
	# The prevalence for a specific set of user attributes/values is its
	# frequency in the data set of that combination. Default propensities
	# are evenly distribution. A user pattern is a dict of specific 
	# user attribute/value pairs.
	def set_prevalence(self, user_pattern, freq):
		attnames = self.uatt_names()
		arr_pattern = map(lambda x: None, range(attnames))
		i = 0
		for att in attnames:
			for (attr, val) in user_pattern.items():
				if att == attr:
					arr_pattern[i] = val
			i += 1
		self.prevs.append((arr_pattern, freq))
		
	# Returns 0 or 1 stochastically based on the user and interaction pattern.
	def gen_response(self, user, inter):
		match = ut.best_match(user + inter, self.propensities, ignore=[None], patlist_accessor=lambda x: x[0])
		if match != None:
			(pat, prob) = match
			return 1 if rd.uniform(0, 1) <= prob else 0
		return 1 if rd.uniform(0, 1) <= self.baseline_response_prob else 0
	
	# Generate responses for multiple user/interaction pairs.
	def gen_responses(self, user_list, inter_list):
		return map(lambda (x, y): self.gen_response(x, y), zip(user_list, inter_list))
	
	# A template is a dict of attribute/value pairs. Builds a random interaction
	# from the template by randomly assigning values to unspecified attribute.
	def gen_random_user_from_template(self, template):
		return self.gen_random_entity_from_template(template, self.user_attrs)
	
	# A template is a dict of attribute/value pairs. Builds a random interaction
	# from the template by randomly assigning values to unspecified attribute.
	def gen_random_inter_from_template(self, template):
		return self.gen_random_entity_from_template(template, self.inter_attrs)
	
	def gen_random_users_from_template(self, template, n):
		return map(lambda x: self.gen_random_user_from_template(template), range(n))
		
	def gen_random_inters_from_template(self, template, n):
		return map(lambda x: self.gen_random_inter_from_template(template), range(n))
	
	# Returns a list of user attribute values in ordered array form.
	# Each item in templates is a (dict, replicates) pair.
	def gen_random_users(self, n, templates = []):
		return self.gen_random_entities(self.user_attrs, n, templates)
	
	# Returns a list of interaction attribute values in ordered array form.
	# Each item in templates is a (dict, replicates) pair.
	def gen_random_inters(self, n, templates = []):
		return self.gen_random_entities(self.inter_attrs, n, templates)
	
	# Returns list of (user patterns, inter patterns, resp), each in array form.
	# Generates based on specified distributions.
	def gen_random_rows(self, n, user_templates = [], inter_templates = []):
		ul = self.gen_random_users(n, user_templates) 
		il = self.gen_random_inters(n, inter_templates)
		rd.shuffle(ul)
		rd.shuffle(il)
		return (ul, il, self.gen_responses(ul, il)) 
	
	def gen_random_rows_from_template(self, user_temp, inter_temp, n):
		ul = self.gen_random_users_from_template(user_temp, n) 
		il = self.gen_random_inters_from_template(inter_temp, n) 
		return (ul, il, self.gen_responses(ul, il))
	
	def gen_random_rows_from(self, users, inters):
		ul = users
		il = map(lambda x: rd.sample(inters, 1)[0], users)
		return (ul, il, self.gen_responses(ul, il))
	
	# For a set of users and inters, generate a set of rows from the cartesian product of these. 
	# Returns list of (user patterns, inter patterns, resp), each in array form.
	def gen_crossprod_rows(self, users, inters):
		all_users = []
		all_inters = []
		for u in users:
			for i in inters:
				all_users.append(u)
				all_inters.append(i)
		responses = self.gen_responses(all_users, all_inters)
		return (all_users, all_inters, responses)
	
	# Return the exhaustive list of unique user combinations.
	def unique_users(self):
		return ut.cartesian_prod(map(lambda (n, levs): levs, self.user_attrs)) 
		
	# Return the exhaustive list of unique interaction combinations.
	def unique_inters(self):
		return ut.cartesian_prod(map(lambda (n, levs): levs, self.inter_attrs))
	
	# ------------------------ INTERNAL UTILITY FUNCTIONS ---------------------------------
	def uatt_names(self):
		return map(lambda x: x[0], self.user_attrs)
	
	def iatt_names(self):
		return map(lambda x: x[0], self.inter_attrs)
		
	def allatt_names(self):
		return map(lambda x: x[0], self.user_attrs + self.inter_attrs)
	
	def gen_random_attrs(self, name_prefix, ncats, min_levels, max_levels, nconts=0, min_min=0, max_min=0, min_max=0, max_max=0):
		attrs = []
		i = 1
		for j in range(ncats):
			levels = map(lambda x: 'L_' + str(x), range(1, rd.randint(min_levels, max_levels) + 1))
			attrs.append((name_prefix + str(i), levels))
			i += 1
		for j in range(nconts):
			mmin = rd.uniform(min_min, max_min)
			mmax = rd.uniform(min_max, max_max)
			attrs.append((name_prefix + str(i), (mmin, mmax)))
			i += 1
		return attrs
	
	def gen_random_entity_from_template(self, template, attrs):
		rnum = lambda (att, range): rd.uniform(range[0], range[1])
		rcat = lambda (att, levels): rd.sample(levels, 1)[0]
		rdec = lambda (att, levs): rcat((att, levs)) if type(levs) == type([]) else rnum((att, levs))
		f = lambda (att, levs): template[att] if template.has_key(att) else rdec((att, levs))
		return map(f, attrs)
	
	# template is a dict. attrs is a set of (name, levels). 
	# entity is ordered list of corresponding attr values.
	def matches_template(self, template, attrs, entity):
		for ((name, levels), val) in zip(attrs, entity):
			if template.has_key(name) and template[name] != val:
				return False
		return True
	
	# Each item in templates is a (dict, replicates) pair.
	def gen_random_entities(self, attrs, n, templates = []):
		rows = []
		for (template, num_reps) in templates:
			rows += map(lambda x: self.gen_random_entity_from_template(template, attrs), range(num_reps))
		n = n - len(rows)
		i = 0
		nm = lambda e: len(filter(lambda x: x == True, map(lambda y: self.matches_template(y, attrs, e), map(lambda z: z[0], templates)))) == 0
		while i < n:
			curr = []
			for (name, levels) in attrs:
				if type(levels) == type([]):
					curr.append(rd.sample(levels, 1)[0])
				else:
					curr.append(rd.uniform(levels[0], levels[1]))
			if nm(curr):
				rows.append(curr)
				i += 1
		return rows
		
	
		
	
		
	