import os
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from task_generation.gaussian_process import GaussianProcess, PracticeMode



data_dir = './output/data/'
#data = pd.concat([pd.read_hdf(data_dir + filename) for filename in os.listdir(data_dir)], axis=0, ignore_index=True)
data = pd.read_hdf(data_dir + 'data_expert_demo_4.h5')
print(data.tail(10))
#2. Initialize Gaussian Process
gp = GaussianProcess()
#3. Choose utility measure
def error_diff_to_utility(error_pre, error_post):
    diff_timing = (error_pre["timing_left"] + error_pre["timing_right"]) - (
            error_post["timing_left"] + error_post["timing_right"])
    diff_pitch = (error_pre["pitch_left"] + error_pre["pitch_right"]) - (
            error_post["pitch_left"] + error_post["pitch_right"])

    return (diff_timing + diff_pitch) / 2

#4.Train Model with datapoints
for index, d in tqdm(data.iterrows()):
    error = {'error_pre': {'timing_left': d['error_before_left_timing'],
                           'timing_right': d['error_before_right_timing'],
                           'pitch_left': d['error_before_left_pitch'],
                           'pitch_right': d['error_before_right_pitch']},
             'error_post': {'timing_left': d['error_after_left_timing'],
                            'timing_right': d['error_after_right_timing'],
                            'pitch_left': d['error_after_left_pitch'],
                            'pitch_right': d['error_after_right_pitch']}}
    # calculate utility from error_pre and error_post
    utility = error_diff_to_utility(error['error_pre'], error['error_post'])
    practice_mode = None
    if d['practice_mode'] == 'IMP_TIMING':
        practice_mode = PracticeMode.IMP_TIMING
    elif d['practice_mode'] == 'IMP_PITCH':
        practice_mode = PracticeMode.IMP_PITCH

    # add data-point to GP
    gp.add_data_point(error['error_pre'], d['bpm'], practice_mode, utility)
    gp.update_model()


#plot data


# Different functions used to deliver a utility value to the plot_utility function -------------------------------------

# returns the utility estimate of a gaussian process for a specific practice mode
def _utility_gp(bpm, practice_mode, error_pre):
    return gp.get_estimate(error_pre, bpm, practice_mode)

# wrapper function to abstract arguments gaussian process and practice mode
def utility_gp(bpm, practice_mode):
    return lambda error_pre: _utility_gp(bpm, practice_mode, error_pre)[0]

def plot_utility(utility_function, density=50, title="Utility", data_points=None):
    plot_data = []
    for i, error_pitch in enumerate(np.linspace(0, 1, density)):
        for j, error_timing in enumerate(np.linspace(0, 1, density)):
            error_pre = {
                'pitch_left': 0,
                'pitch_right': error_pitch,
                'timing_left': 0,
                'timing_right': error_timing
            }
            utility = utility_function(error_pre)

            plot_data.append([error_pitch, error_timing, utility])

    plot_data = np.array(plot_data)

    fig = plt.figure(figsize=(10, 7))
    ax = plt.axes(projection="3d")

    ax.scatter3D(plot_data[:, 0], plot_data[:, 1], plot_data[:, 2], s=8)

    if data_points is not None:
        ax.scatter3D(data_points[:, 0], data_points[:, 1], data_points[:, 2], color="red", alpha=0.6)

    ax.set_title(title)
    ax.set_xlabel('error_pitch')
    ax.set_ylabel('error_timing')
    ax.set_zlabel('utility')
    ax.set_zlim(0, 0.5)

    plt.show()

    #5.1
users = list(set(data["username"]))
midi_name = list(set(data["midi_filename"]))

figure, axis = plt.subplots(1, 3, figsize=(15, 5))

axis[0].scatter(data['error_before_right_pitch'], data['error_before_right_timing'], label=None, c='gray')
axis[0].set_title('training datapoints')
axis[0].set_xlabel('pitch_error')
axis[0].set_ylabel('timing_error')

for index, u in enumerate(users):
    axis[1].scatter(data.loc[data["username"] == u]['error_before_right_pitch'],
                    data.loc[data["username"] == u]['error_before_right_timing'], label=u)
axis[1].set_title('training datapoints by username')
axis[1].set_xlabel('pitch_error')
axis[1].set_ylabel('timing_error')
axis[1].legend()

for i, m in enumerate(midi_name):
    axis[2].scatter(data.loc[data["midi_filename"] == m]['error_before_right_pitch'],
                    data.loc[data["midi_filename"] == m]['error_before_right_timing'], label=m)
axis[2].set_title('training datapoints by music piece')
axis[2].set_xlabel('pitch_error')
axis[2].set_ylabel('timing_error')
axis[2].legend()
figure.suptitle("Training datapoints", fontsize=16)
plt.tight_layout()
plt.show()


#5.2. Policy

training_points = {
    0: [],  # pitch
    1: [],  # timing
}

for i, point in enumerate(gp.data_X):
    training_points[point[0]].append([point[3], point[5], gp.data_Y[i][0]])

for i in range(2):
    training_points[i] = np.array(training_points[i])

density = 100
best_mode = np.zeros((density, density))
for i, error_pitch in enumerate(np.linspace(0, 1, density)):
    for j, error_timing in enumerate(np.linspace(0, 1, density)):
        best_pm = gp.get_best_practice_mode({
            'pitch_left': 0,
            'pitch_right': error_pitch,
            'timing_left': 0,
            'timing_right': error_timing
        }, bpm=60, epsilon=0)
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
