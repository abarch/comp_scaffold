#optimizing the GP hyper parameters to align with expert
import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from task_generation.gaussian_process import GaussianProcess, PracticeMode
EXPERT_PATH = "D:\Elad\comp_scaffold\DexmoPiano\output\data\data_expert_demo.h5"
DATA_PATH = "D:\Elad\comp_scaffold\DexmoPiano\output\data\data.h5"
def get_binary_policy(data):
    #get the data and adds a binary policy collumn
    policy_binary = pd.get_dummies(data["practice_mode"],dtype=int)
    policy_binary = policy_binary["IMP_PITCH"]
    #WE ASSIGN 1 TO PITCH AND 0 TO TIMING
    policy_binary = policy_binary.rename("binary_policy")
    data = pd.concat((data, policy_binary), axis=1)
    return data
def calc_loss(policy_diff):
    #calculate the losss as defined on the policy diff
    sum = policy_diff.sum()
    med = policy_diff.mean()#cant use median because somtimes 0. what to use?
    T = len(policy_diff)
    return sum/(med*T)
def get_policy_loss(expert_file, curr_gp_data_file):
    #gets h5 files of expert and data and return policy loss between them
    data = pd.read_hdf(curr_gp_data_file, axis=0)
    #slicing is just for now. to make sure that the data is the same size as expert. it will be like this in the GP data
    gp_data = data[:11]
    expert_data = pd.read_hdf(expert_file, axis=0)
    expert_data = get_binary_policy(expert_data)
    gp_data = get_binary_policy(gp_data)
    policy_diff = gp_data["binary_policy"] - expert_data["binary_policy"]
    policy_diff = policy_diff.abs()
    policy_loss =calc_loss(policy_diff)
    return policy_loss


loss = get_policy_loss(EXPERT_PATH, DATA_PATH)
print(loss)

