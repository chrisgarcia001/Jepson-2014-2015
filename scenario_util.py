# --------------------------------------------------------------------------------------
# Author: cgarcia@umw.edu
# About: This file contains utility functions and classes used specifically in
#        running scenarios and generating result reports
# --------------------------------------------------------------------------------------

import util as ut
from scipy import stats
import math
from knn import *

#-------------------------- STATISTICAL FUNCTIONS ------------------------

# Performs 2-sample proportion test of form:
# H0: p1 = p2, H1: p1 != p2
# Sample 1 and sample 2 are lists of 0's and 1'sample
# Returns a p-value
def proportion_test(sample_1, sample_2):
	n1 = float(len(sample_1))
	n2 = float(len(sample_2))
	p1 = float(sum(sample_1)) / n1
	p2 = float(sum(sample_2)) / n2
	z = (p1 - p2) / math.sqrt(((p1 * (1.0 - p1)) / n1) + ((p2 * (1.0 - p2)) / n2))
	return stats.norm().cdf(1.0 - z)

# Get simple mean of the values.	
def mean(vals):
	return float(sum(vals)) / float(len(vals))

#-------------------------- UTILITY CLASSES ------------------------------
# This is a basic logger which prints output to the command line and
# writes the log file to the specified output file.
class BasicLogger(object):
	def __init__(self):
		self.lines = []
	
	def log(self, line, level='standard'):
		if level.lower() == 'report':
			self.lines.append(str(line))
		print(line)
		
	def write(self, output_file):
		ut.write_file("\n".join(self.lines), output_file)

# This is a simple class to record and accumulate artifacts
# generated in a scenario
class ScenarioRecorder(object):
	def __init__(self):
		self.records = {}
	
	# Add a new value to the specified key's value list
	def add(self, key, val):
		if not(self.records.has_key(key)):
			self.records[key] = []
		self.records[key].append(val)
	
	# Set a key's value
	def set(self, key, val):
		self.records[key] = val
	
	# Get whatever is corresponding to the key
	def get(self, key):
		if self.records.has_key(key):
			return self.records[key]
		return 'NA'
	
	# If the key holds a list of lists, join them all together into
	# into one master list before returning.
	def get_flatten(self, key):
		try:
			return reduce(lambda x, y: x + y, self.records[key])
		except:
			return get(key)
	
	# Get the keys for this recorder. If a prefix is specified,
	# Get keys which start with the prefix.
	def keys(self, prefix = None):
		if not(prefix == None):
			return filter(lambda x: x.startswith(prefix), self.records.keys())
		return self.records.keys()

#-------------------------- UTILITY FUNCTIONS ----------------------------		
# A solver is a function f: user -> msg
# Each element in solvers is a (solver, solver name) pair
def execute_trial(train_data, test_users, data_gen, solvers, recorder,
					trial_name = None, measures_per_user = 1,
					logger = None):
	results = []
	if trial_name == None:
		trial_name = ''
	else:
		trial_name = ': ' + trial_name
	logger_f = logger.log if logger != None else lambda x, y: None
	logger_f = logger.log
	logger_f('Executing comparison trial' + str(trial_name), 'standard')
	for (f, solver_name) in solvers:
		logger_f("  Starting solver: " + solver_name, 'standard')
		start_time = ut.curr_time()
		msgs = map(f, test_users)
		elapsed = ut.curr_time() - start_time
		resps = []
		for i in range(measures_per_user):
			resps += data_gen.gen_responses(test_users, msgs)
		correct_frac = float(sum(resps)) / float(measures_per_user * len(resps))
		results.append((solver_name, correct_frac, elapsed, resps))
		add = lambda att, val: recorder.add(solver_name + '.' + str(att), val)
		add('correct_frac', correct_frac)
		add('responses', resps)
		recorder.add('elapsed_time', elapsed)
		logger_f("  Results (correct%, elapsed time): " + str((correct_frac, elapsed)), 'standard')
		

# A trial_initializer_f is a function which takes a recorder and logger as input and returns a tuple:
# (train_data, test_users, data_generator, [(solver_f, name)])
# An analyzer_f is a procedure which takes these args (in order):
#    1) a recorder
#    2) a logger, 
#    3) a list solver names with the following convention:
#      Control solvers start with control_ and treatment solvers start with solver_
def run_trials(trial_initializer_f, analyzer_f, num_trials, recorder, logger):
	recorder.set('num_trials', num_trials)
	main_start_time = ut.curr_time()
	for t in range(1, num_trials + 1):
		trial_start = ut.curr_time()
		logger.log('Starting new trial, initializing...', 'standard')
		train_data, test_users, data_generator, solvers = trial_initializer_f(recorder, logger)
		logger.log('  Time initializing: ' + str(ut.curr_time() - trial_start) + ' sec.', 'standard')
		execute_trial(train_data, test_users, data_generator, solvers, recorder, 
					  trial_name = 'Trial ' + str(t), logger = logger)
	main_elapsed = ut.curr_time() - main_start_time
	recorder.set('main.elapsed_time', main_elapsed)
	analyzer_f(recorder, logger, map(lambda (x, y): y, solvers))	
		
# For a list of test users and test messages, return the n best-performing.
# Used for a control case to compare other algorithms to.	
# **NOTE: param msgs can be either 1) an integer, or 2) a list of pre-made messages
#         If it is an integer, the specified number of random messages will be generated.
def n_best_messages(users, data_gen, msgs, n):
	if type(msgs) == type(0):
		msgs = data_gen.gen_random_inters(msgs)
	rows = zip(*data_gen.gen_crossprod_rows(users, msgs))
	mcount = lambda m: sum(map(lambda x: x[2], filter(lambda y: y[1] == m, rows)))
	pos_count = lambda y: sum(map(lambda x: x[2], filter(lambda z: y == z[1], tups)))
	results = map(lambda msg: (msg, mcount(msg)), msgs)
	return map(lambda (msg, _): msg, ut.top_n(results, n, lambda y: y[1]))
	
# Build (solver, name) pairs for each of the 3 standard controls
# which can go into execute_trial.	
# **NOTE: param msgs can be either 1) an integer, or 2) a list of pre-made messages
#         If it is an integer, the specified number of random messages will be generated.
def build_std_control_solvers(calibration_users, data_gen, msgs = 100, top_n = 15):
	b = data_gen
	if(type(msgs)) == type(0):
		msgs = n_best_messages(calibration_users, b, msgs, msgs)
	best_msgs = n_best_messages(calibration_users, b, msgs, top_n)
	# Control 1: select a random message each time
	ctrl_1 = lambda u: rd.sample(msgs, 1)[0] 
	# Control 2: Always give the best performing out of the 100
	ctrl_2 = lambda u: best_msgs[0] 
	# Control 3: randomly select one of the top 15 messages for each user
	ctrl_3 = lambda u: rd.sample(best_msgs, 1)[0] 
	solvers = [(ctrl_1, 'control_1'),
				(ctrl_2, 'control_2'),
				(ctrl_3, 'control_3')]
	return solvers
	
# Builds all KNN solvers in (solver, name) pairs, which can go
# which can go into execute_trial.	
def build_all_knn_optims(train_data, calibration_users, data_gen, recorder, 
						 min_k = 1, max_k = 15):
	b = data_gen
	op = KNNOptimizer()
	op.set_data_rows(train_data)
	op.set_similarity_f(match_count)
	asf_1 = build_weighted_mode_selector(lambda x: 1)
	asf_2 = build_weighted_mode_selector(lambda x: 10**x)
	asf_3 = build_weighted_max_pos_proportion_selector(lambda x: 1)
	asf_4 = build_weighted_max_pos_proportion_selector(lambda x: 10**x)
	response_f = lambda u, m: b.gen_response(u, m)
	k1 = op.find_best_k(calibration_users, min_k, max_k, asf_1, response_f)
	k2 = op.find_best_k(calibration_users, min_k, max_k, asf_2, response_f)
	k3 = op.find_best_k(calibration_users, min_k, max_k, asf_3, response_f)
	k4 = op.find_best_k(calibration_users, min_k, max_k, asf_4, response_f)
	recorder.add('solver_1.k', k1)
	recorder.add('solver_2.k', k2)
	recorder.add('solver_3.k', k3)
	recorder.add('solver_4.k', k4)
	print('k1, k2: ' + str((k1, k2)))
	f_1 = lambda u: op.optimize(u, k1, asf_1)
	f_2 = lambda u: op.optimize(u, k2, asf_2)
	f_3 = lambda u: op.optimize(u, k3, asf_3)
	f_4 = lambda u: op.optimize(u, k4, asf_4)
	solvers = [(f_1, 'solver_1'),
			   (f_2, 'solver_2'),
			   (f_3, 'solver_3'),
			   (f_4, 'solver_4')
			  ]
	return solvers

# Builds standard (mode-based) KNN solvers in (solver, name) pairs, which can go
# which can go into execute_trial.	
def build_std_knn_optims(train_data, calibration_users, data_gen, recorder, 
						 min_k = 1, max_k = 15):
	b = data_gen
	op = KNNOptimizer()
	op.set_data_rows(train_data)
	op.set_similarity_f(match_count)
	asf_1 = build_weighted_mode_selector(lambda x: 1)
	asf_2 = build_weighted_mode_selector(lambda x: 10**x)
	response_f = lambda u, m: b.gen_response(u, m)
	k1 = op.find_best_k(calibration_users, min_k, max_k, asf_1, response_f)
	k2 = op.find_best_k(calibration_users, min_k, max_k, asf_2, response_f)
	recorder.add('solver_1.k', k1)
	recorder.add('solver_2.k', k2)
	print('k1, k2: ' + str((k1, k2)))
	f_1 = lambda u: op.optimize(u, k1, asf_1)
	f_2 = lambda u: op.optimize(u, k2, asf_2)
	solvers = [(f_1, 'solver_1'),
			   (f_2, 'solver_2')
			  ]
	return solvers
	
def standard_analyzer_f(recdr, logr, solver_names):
	log = lambda *x: logr.log(' '.join(map(lambda y: str(y), x)), 'report')
	key = lambda x, y = None: str(x) + '.' + (y) if y != None else str(x)
	get = lambda prefix, att = None: recdr.get(key(prefix, att))
	fget = lambda prefix, att = None: recdr.get_flatten(key(prefix, att))
	pt = lambda s1, s2: proportion_test(fget(s1), fget(s2))
	ctrls = filter(lambda x: x.startswith('control'), solver_names)
	tmts = filter(lambda x: x.startswith('solver'), solver_names)
	all = ctrls + tmts
	log('-------------------- RESULTS ------------------------')
	log('Number of trials: ', get('num_trials'))
	for s in tmts:
		log(s + ' avg. k: ', mean(get(s, 'k')))
	for s in ctrls:
		log(s + ' avg. success %: ', mean(get(s, 'correct_frac')), 
			', (min, max) success %: ', (min(get(s, 'correct_frac')), max(get(s, 'correct_frac'))))
	for s in tmts:
		log(s + ' avg. success %: ', mean(get(s, 'correct_frac')), 
			', (min, max) success %: ', (min(get(s, 'correct_frac')), max(get(s, 'correct_frac'))))
	for c in ctrls:
		for s in tmts:
			log(s + ' vs. ' + c + ' (p-val): ', pt(s + '.responses', c + '.responses'))
	for i in range(len(tmts) - 1):
		for j in range(1, len(tmts)):
			log(tmts[i] + ' vs. ' + tmts[j] + ' (p-val): ', 
			    pt(tmts[i] + '.responses', tmts[j] + '.responses'))
			log(tmts[j] + ' vs. ' + tmts[i] + ' (p-val): ', 
			    pt(tmts[j] + '.responses', tmts[i] + '.responses'))
	for s in tmts:
		for c in ctrls:
			log('Avg ' + s + '/ ' + c + ' ratio: ', max(get(s, 'correct_frac')) / max(get(c, 'correct_frac')))
	log('-------------------- TOTAL ELAPSED TIME: ', get('main', 'elapsed_time'), ' sec.')
	
	
	