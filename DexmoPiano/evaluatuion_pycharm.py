import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from task_generation.gaussian_process import GaussianProcess, PracticeMode



data_dir = './output/data/'
data = pd.concat([pd.read_hdf(data_dir + filename) for filename in os.listdir(data_dir)], axis=0, ignore_index=True)
print(data.tail(10))
