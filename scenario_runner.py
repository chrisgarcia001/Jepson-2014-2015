# --------------------------------------------------------------------------------------
# Author: cgarcia@umw.edu
# About: This file runs a scenario based on the parameters in the specified parameter 
#        file. To see some example parameter files, look in the "params" folder.
# --------------------------------------------------------------------------------------

from os import sys
from data_gen import *
from knn import *
import random as rd
import util as ut
import scenario_util as su

params = None
try:
	params = ut.read_params(sys.argv[1], ignore_lines = '#')
except:
	params = ut.read_params(sys.argv[1], ignore_lines = '#')

# Get params when possible from the set of params, otherwise
# return the specified default.	
def p(param_name, default):
	try:
		return params[param_name]
	except:
		return default
		
# Main parameters.
num_trials = p('num_trials', 5)
baseline = p('baseline_prob', 0.02)
num_user_atts, min_user_att_levels, max_user_att_levels = p('user_attribute_spec', (4, 2, 4))
num_msg_atts, min_msg_att_levels, max_msg_att_levels = p('msg_attribute_spec', (4, 2, 4))
num_propensity_groups = p('num_propensity_groups', 5)
min_group_user_atts, max_group_user_atts = p('minmax_user_propensity_attrs_involved', (3, 4))
min_group_msg_atts, max_group_msg_atts = p('minmax_msg_propensity_attrs_involved', (2, 4))
min_group_pos_prob, max_group_pos_prob = p('minmax_propensity_group_response_prob', (0.2, 0.85))
num_users = p('num_users', 1000)
num_test_messages = p('num_test_messages', 100)
output_file = p('output_file', None)

# Initializer function
def trial_init(recdr, logr):
	logr.log('Initializing new trial...', 'standard')
	b = DataGenerator()
	b.set_baseline_response_prob(baseline)
	b.add_random_user_attrs(num_user_atts, min_user_att_levels, max_user_att_levels) 
	b.add_random_inter_attrs(num_msg_atts, min_msg_att_levels, max_msg_att_levels) 
	templates = b.set_random_propensities(num_propensity_groups, 
							  min_group_user_atts, max_group_user_atts, 
							  min_group_msg_atts, max_group_msg_atts,
							  min_group_pos_prob, max_group_pos_prob)
	# -> Returns: a pair (user templates, interaction templates)
	logr.log('Generating data...', 'standard')
	messages = b.gen_random_inters(num_test_messages)
	users = b.gen_random_users(num_users)
	rows = ut.unzip(b.gen_random_rows_from(users, messages))
	logr.log('Number of rows: ' + str(len(rows)), 'standard')
	# Split data into train, calibration, and test.
	train, calibrate, test = ut.split_data(rows, 0.5, 0.25, 0.25)
	calibration_users = map(lambda (u, m, r): u, calibrate)
	test_users = map(lambda (u, m, r): u, test)
	controls = su.build_std_control_solvers(calibrate, b, messages, 15)
	treatments = su.build_std_knn_optims(train, calibrate, b, recorder, 1, 15)
	solvers = controls + treatments
	return (train, test_users, b, solvers)

logger = su.BasicLogger()
recorder = su.ScenarioRecorder()
	
su.run_trials(trial_init, su.standard_analyzer_f, num_trials, recorder, logger)
if output_file != None:
	logger.write(output_file)
