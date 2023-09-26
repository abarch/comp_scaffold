import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from task_generation.gaussian_process import GaussianProcess, PracticeMode



data_dir = './output/data/'
#data = h5py.File('./output/data/data.h5', 'r')
data_expert =pd.read_hdf('./output/data/data_expert.h5')

with pd.option_context('display.max_rows', None, 'display.max_columns', None):
    print(data_expert)