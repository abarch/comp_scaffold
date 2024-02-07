import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import time
from statistics import mean 
import json
from sklearn.model_selection import train_test_split
from matplotlib.patches import Patch
from gp_utility import GaussianProcess, PracticeMode, policy_test, policy_add_test
import GPy
from GPyOpt.methods import BayesianOptimization

gp = []
gp_list = []
policy_diff_list = []

def plot_best_policy(gp, tempo):
    

    # training_points = {
    #     0: [],  # pitch
    #     1: [],  # timing
    # }

    # for i, point in enumerate(gp.data_X):
    #     training_points[point[0]].append([point[3], point[5], gp.data_Y[i][0]])

    # for i in range(2):
    #     training_points[i] = np.array(training_points[i])

    density = 100
    best_mode = np.zeros((density, density))
    for i, error_pitch in enumerate(np.linspace(0, 1, density)):
        for j, error_timing in enumerate(np.linspace(0, 1, density)):
            best_pm = gp.get_best_practice_mode({
                #'pitch_left': 0,
                'pitch_right': error_pitch,
                #'timing_left': 0,
                'timing_right': error_timing
            }, bpm=tempo, epsilon=0)
            if best_pm == PracticeMode.IMP_PITCH:
                best_mode[i][j] = 0
            elif best_pm == PracticeMode.IMP_TIMING:
                best_mode[i][j] = 1
            else:
                best_mode[i][j] = 2

    plt.pcolormesh(np.linspace(0, 1, density), np.linspace(0, 1, density), best_mode)
    plt.title("GP's Estimate for best Practice Mode")
    plt.ylabel("error_pitch")
    plt.xlabel("error_timing")

    cmap = plt.cm.viridis
    custom_lines = [Patch(facecolor=cmap(0.)),
                 Patch(facecolor=cmap(1.))]
    plt.legend(custom_lines, ["IMP_PITCH", "IMP_TIMING"])
    plt.show()

def plot_best_policy(gp, tempo):
    

    # training_points = {
    #     0: [],  # pitch
    #     1: [],  # timing
    # }

    # for i, point in enumerate(gp.data_X):
    #     training_points[point[0]].append([point[3], point[5], gp.data_Y[i][0]])

    # for i in range(2):
    #     training_points[i] = np.array(training_points[i])

    density = 100
    best_mode = np.zeros((density, density))
    for i, error_pitch in enumerate(np.linspace(0, 1, density)):
        for j, error_timing in enumerate(np.linspace(0, 1, density)):
            best_pm = gp.get_best_practice_mode({
                #'pitch_left': 0,
                'pitch_right': error_pitch,
                #'timing_left': 0,
                'timing_right': error_timing
            }, bpm=tempo, epsilon=0)
            if best_pm == PracticeMode.IMP_PITCH:
                best_mode[i][j] = 0
            elif best_pm == PracticeMode.IMP_TIMING:
                best_mode[i][j] = 1
            else:
                best_mode[i][j] = 2

    plt.pcolormesh(np.linspace(0, 1, density), np.linspace(0, 1, density), best_mode)
    plt.title("GP's Estimate for best Practice Mode")
    plt.ylabel("error_pitch")
    plt.xlabel("error_timing")

    cmap = plt.cm.viridis
    custom_lines = [Patch(facecolor=cmap(0.)),
                 Patch(facecolor=cmap(1.))]
    plt.legend(custom_lines, ["IMP_PITCH", "IMP_TIMING"])
    plt.show()

def objective_function(x, kernel_type):
    #objective function for the optimization of the hyperparameters, getting the mean policy diff for the current hyperparameters
    if x.ndim > 1:
        x = x.flatten()
        
    # x is a list of hyperparameters
    a, mean_utility = x
    print (a, mean_utility)
    # Initialize a GP model with the given hyperparameters and kernel type
    # per calculation of the objective function we calculate the whole prediction of the gaussian process and compare it to the ground truth data. 
    global gp
    global gp_list
    global policy_diff_list

    gp = GaussianProcess()
    
    #gp.space.model_dimensionality
    if kernel_type == 'Matern52':
        kernel = GPy.kern.Matern52(input_dim=gp.space.model_dimensionality, ARD=True)
    elif kernel_type == 'RBF':
        kernel = GPy.kern.RBF(input_dim=gp.space.model_dimensionality, ARD=True)
    elif kernel_type == 'RatQuad':
        kernel = GPy.kern.RatQuad(input_dim=gp.space.model_dimensionality, ARD=True)
    elif kernel_type == 'Poly':
        kernel = GPy.kern.Poly(input_dim=gp.space.model_dimensionality, degree=1, variance=1.0, scale=1.0, offset=0.0, ARD=True)
    elif kernel_type == 'Exp':
        kernel = GPy.kern.Exponential(input_dim=gp.space.model_dimensionality, ARD=True)
    else:
        raise ValueError("Invalid kernel type")

    gp.update_model_with_kernel(kernel)

    # Calculate the utility using the expert data and the GP model
    recorded_points =  expert_data [[  #'error_before_left_timing',
     'error_before_right_timing',
       #'error_before_left_pitch', 
       'error_before_right_pitch',
       #'error_after_left_timing', 
        'error_after_right_timing',
       #'error_after_left_pitch', 
       'error_after_right_pitch', "practice_mode", "bpm"]]
    # policy_diff = policy_diff_for_single_gp(gp, recorded_points,a,mean_utility)
    #policy_diff_list.append(-policy_diff)
    #return -policy_diff

    policy_diff= policy_add_test(gp,recorded_points,a, mean_utility) #policy_diff_for_single_gp(gp, recorded_points,a, mean_utility)
    gp_list.append(gp)
    policy_diff_list.append(policy_diff)
    #plot_best_policy(gp, 70)
    return policy_diff

def plot_best_policy(gp, tempo):

    # training_points = {
    #     0: [],  # pitch
    #     1: [],  # timing
    # }

    # for i, point in enumerate(gp.data_X):
    #     training_points[point[0]].append([point[3], point[5], gp.data_Y[i][0]])

    # for i in range(2):
    #     training_points[i] = np.array(training_points[i])

    density = 100
    best_mode = np.zeros((density, density))
    for i, error_pitch in enumerate(np.linspace(0, 1, density)):
        for j, error_timing in enumerate(np.linspace(0, 1, density)):
            best_pm = gp.get_best_practice_mode({
                #'pitch_left': 0,
                'pitch_right': error_pitch,
                #'timing_left': 0,
                'timing_right': error_timing
            }, bpm=tempo, epsilon=0)
            if best_pm == PracticeMode.IMP_PITCH:
                best_mode[i][j] = 0
            elif best_pm == PracticeMode.IMP_TIMING:
                best_mode[i][j] = 1
            else:
                best_mode[i][j] = 2

    plt.pcolormesh(np.linspace(0, 1, density), np.linspace(0, 1, density), best_mode)
    plt.title("GP's Estimate for best Practice Mode")
    plt.ylabel("error_pitch")
    plt.xlabel("error_timing")

    cmap = plt.cm.viridis
    custom_lines = [Patch(facecolor=cmap(0.)),
                 Patch(facecolor=cmap(1.))]
    plt.legend(custom_lines, ["IMP_PITCH", "IMP_TIMING"])
    plt.show()

def optimal_gp_index(gauss_models, policy_diff, max_iter):
    #we choose the gp with the lowest mean policy diff
    l = gauss_models[-max_iter-4:]
    p = policy_diff[-max_iter-4:]
    best_model_index = np.argmin([np.mean(pd) for pd in p])
    print('Best model is at index:', best_model_index)
    best_model = l[best_model_index]
    return best_model

EXPERT_PATH = ['Avigail_expert_session.h5', 'Itai_expert_session.h5', 'Lali_expert_session.h5', 'elad_demo_session.h5', "Arbelle_expert_session.h5", "Danielle_expert_session.h5"]

combined_df = pd.DataFrame()  # Create an empty DataFrame to store the combined data

for path in EXPERT_PATH:
    try:
        data = pd.read_hdf(path)
        combined_df = pd.concat([combined_df, data])  # Concatenate the current file's data to the combined DataFrame
    except FileNotFoundError:
        print('File {} not found'.format(path))


expert_data =combined_df
type(expert_data)

# Sort the data by 'midi_filename' and 'username' columns
expert_data = expert_data.sort_values(by=['midi_filename', 'username'])

# Group the data by 'midi_filename' and 'username'
grouped_data = expert_data.groupby(['midi_filename', 'username'])

train_data = pd.DataFrame()
test_data = pd.DataFrame()

# Iterate over each group
for group_key, group_df in grouped_data:
    # Check the number of points in the group
    group_size = len(group_df)

    if group_size > 1:
        np.random.seed(42)
# Perform the train-test split with shuffle=False
        train_group, test_group = train_test_split(group_df, test_size=1, shuffle=True)
       

        # Append train group to train data
        train_data = pd.concat([train_data, train_group])

        # Append test group to test data
        test_data = pd.concat([test_data, test_group])
    else:
        # Add the whole group to the training data
        train_data = pd.concat([train_data, group_df])

# Randomly choose a third of the points in test and move them to train
test_size = len(test_data)
train_size = len(train_data)

# Reset the index of train and test data
train_data = train_data.reset_index(drop=True)
test_data = test_data.reset_index(drop=True)

whole_data = expert_data.copy()
# Asya -comment out 
expert_data = whole_data #train_data

import GPy
from GPyOpt.methods import BayesianOptimization


bounds = [{'name': 'a', 'type': 'continuous', 'domain': (-1, 1)},       
          {'name': 'mean_utility', 'type': 'continuous', 'domain': (-10,10)}]

# iterate over the bounds at least as many times. 
max_iter_index= 30

kernel_type = 'Matern52'

# object function includes the definition of the kernel type, not the kernel object.     
obj_func = lambda x: objective_function(x, kernel_type)

# set the bounds for the optimization process here! 
bo = BayesianOptimization(f=obj_func,     
                          domain=bounds,
                          acquisition_type='EI',
                          acquisition_jitter=0.05,
                          num_cores=10)

bo.run_optimization(max_iter=max_iter_index, verbosity=True)
gp=optimal_gp_index(gp_list, policy_diff_list, max_iter_index)

plot_best_policy(gp, 70)

#initialize the hyper parameters bound for different kernels
kernel_type = 'RatQuad'

# object function includes the definition of the kernel type, not the kernel object.     
obj_func = lambda x: objective_function(x, kernel_type)
    
# set the bounds for the optimization process here! 
bo = BayesianOptimization(f=obj_func,     
                          domain=bounds,
                          acquisition_type='EI',
                          acquisition_jitter=0.05,
                          num_cores=10)
    
bo.run_optimization(max_iter=max_iter_index, verbosity=True)
gp=optimal_gp_index(gp_list, policy_diff_list, max_iter_index)

hyperparameters = bo.x_opt
mean_policy_diff = bo.fx_opt

plot_best_policy(gp, 70)
print(hyperparameters)
print(mean_policy_diff)
