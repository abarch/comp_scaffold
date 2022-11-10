import numpy as np
import matplotlib.pyplot as plt
import csv

import pandas as pd

fontsize=9

def plot_task(phase, task_number, plot_title, plot_ind, fig, axs, legend = True):

    df1 = df[(df.phase == phase) & (df.task_number == task_number)]

    bpm = df1['bpm'].values[0]

    y = df1['Summed_right'] #you can also use df['column_name']
    y_hold = df1['note_hold_time_right']
    y_fix = y #-y_hold

    print('Summed right',y_fix.values.astype(np.float))
    axs[0,plot_ind].plot(y_fix.values.astype(np.float),marker = 'o', label = 'Summed')
    axs[0,plot_ind].set_title(plot_title+',bpm='+str(bpm), fontsize=fontsize)


    df1 = df[(df.phase == phase) & (df.task_number == task_number)]
    #y = df1['Summed_right'] #you can also use df['column_name']

    y = df1['pitch_right']  # you can also use df['column_name']
    print('pitch_right', y.values.astype(np.float))
    axs[0,plot_ind].plot(y.values.astype(np.float),marker = 'o', label='pitch')

    y = df1['timing_right'] #you can also use df['column_name']
    print('timing_right', y.values.astype(np.float))
    axs[0,plot_ind].plot( y.values.astype(np.float),marker = 'o', label = 'timing')

#    df1 = df[(df.phase == phase) & (df.task_number == task_number)]
#    y = df1['note_hold_time_right'] #you can also use df['column_name']
#    print('note_hold_time_right', y.values.astype(np.float))
#    axs[plot_ind].plot(y.values.astype(np.float), label = 'hold_time')

    df1 = df[(df.phase == phase) & (df.task_number == task_number)]
    y = df1['n_extra_notes_right'] #you can also use df['column_name']
    print('n_extra_notes_right', y.values.astype(np.float))
    axs[0,plot_ind].plot(y.values.astype(np.float),marker = 'o', label = 'extra notes')

    df1 = df[(df.phase == phase) & (df.task_number == task_number)]
    y = df1['n_missing_notes_right'] #you can also use df['column_name']
    print('n_missing_notes_right', y.values.astype(np.float))
    axs[0,plot_ind].plot(y.values.astype(np.float),marker = 'o', label = 'missing notes')

    y = df1['diff_rating']
    print('diff_rating', y.values.astype(np.float))
    axs[1, plot_ind].plot(y.values.astype(np.float), marker='o', label='diff')

    y = df1['perf_rating']
    print('perf_rating', y.values.astype(np.float))
    axs[1, plot_ind].plot(y.values.astype(np.float), marker='o', label='performance')

    if legend:
        axs[0,plot_ind].legend()
        axs[1, plot_ind].legend()

#axs[0, 1].plot(x, y, 'tab:orange')
# axs[0, 1].set_title('Axis [0, 1]')
# axs[1, 0].plot(x, -y, 'tab:green')
# axs[1, 0].set_title('Axis [1, 0]')
# axs[1, 1].plot(x, -y, 'tab:red')
# axs[1, 1].set_title('Axis [1, 1]')

# df = pd.read_csv('2022-05-18_error - 2022-05-18_error_fixed.csv')
#
# fig, axs = plt.subplots(1,5, sharey=True)
# fig.suptitle('calibration hazar')
# axs[0].set_ylim([0, 2])
# plot_task('calibration', 1, 'ex1', 0, fig, axs)
# plot_task('calibration', 2, 'ex2', 1, fig, axs, legend = False)
# plot_task('calibration', 3, 'ex3', 2, fig, axs, legend = False)
# plot_task('calibration', 4, 'ex4', 3, fig, axs, legend = False)
# plot_task('calibration', 5, 'ex5', 4, fig, axs, legend = False)
#
# fig, axs = plt.subplots(1,4, sharey=True)
# fig.suptitle('practice hazar')
# axs[0].set_ylim([0, 2])
#
# plot_task('practice', 1, 'ex1', 0, fig, axs, legend = False)
# plot_task('practice', 2, 'ex2', 1, fig, axs, legend = False)
# plot_task('practice', 3, 'ex3', 2, fig, axs, legend = False)
# plot_task('practice', 4, 'ex4', 3, fig, axs, legend = False)
#
# fig, axs = plt.subplots(1,4, sharey=True)
# axs[0].set_ylim([0, 2])
# fig.suptitle('retention hazar')
# plot_task('retention', 1, 'ex1', 0, fig, axs, legend = False)
# plot_task('retention', 2, 'ex2', 1, fig, axs, legend = False)
# plot_task('retention', 3, 'ex3', 2, fig, axs, legend = False)
# plot_task('retention', 4, 'ex4', 3, fig, axs, legend = False)
#
# #----------------------------------
# df = pd.read_csv('2022-05-11_error - 2022-05-11_error_fixed.csv')
#
# fig, axs = plt.subplots(1,5, sharey=True)
# fig.suptitle('calibration jason')
# axs[0].set_ylim([0, 2])
# plot_task('calibration', 1, 'ex1', 0, fig, axs)
# plot_task('calibration', 2, 'ex2', 1, fig, axs, legend = False)
# plot_task('calibration', 3, 'ex3', 2, fig, axs, legend = False)
# plot_task('calibration', 4, 'ex4', 3, fig, axs, legend = False)
# plot_task('calibration', 5, 'ex5', 4, fig, axs, legend = False)
#
# #-----------------
#
#
# df = pd.read_csv('2022-04-28_error - 2022-04-28_error_fixed.csv')
#
# fig, axs = plt.subplots(1,4, sharey=True)
# fig.suptitle('calibration maor')
# axs[0].set_ylim([0, 2])
# plot_task('calibration', 1, 'ex1', 0, fig, axs)
# plot_task('calibration', 2, 'ex2', 1, fig, axs, legend = False)
# plot_task('calibration', 3, 'ex3', 2, fig, axs, legend = False)
# plot_task('calibration', 4, 'ex4', 3, fig, axs, legend = False)
#
# fig, axs = plt.subplots(1,5, sharey=True)
# fig.suptitle('practice maor')
# # axs[0].set_ylim([0, 0.75])
#
# plot_task('practice', 1, 'ex1', 0, fig, axs, legend = False)
# plot_task('practice', 2, 'ex2', 1, fig, axs, legend = False)
# plot_task('practice', 3, 'ex3', 2, fig, axs, legend = False)
# plot_task('practice', 4, 'ex4', 3, fig, axs, legend = False)
# plot_task('practice', 5, 'ex4', 4, fig, axs, legend = False)


#############################
# Aviv pilot
# df = pd.read_csv('2022-07-28_error_fixed.csv')
# fig, axs = plt.subplots(1,4, sharey=True)
# fig.suptitle('calibration Aviv')
# axs[0].set_ylim([0, 2])
# plot_task('Calibration', 5, 'ex1', 0, fig, axs)
# plot_task('Calibration', 6, 'ex2', 1, fig, axs, legend = False)
# plot_task('Calibration', 7, 'ex3', 2, fig, axs, legend = False)
#
# fig, axs = plt.subplots(1,10, sharey=True)
# fig.suptitle('practice Aviv')
# # axs[0].set_ylim([0, 0.75])
#
# plot_task('Practice', 9, 'ex1', 0, fig, axs)
# plot_task('Test', 9, 'test1', 1, fig, axs, legend = False)
# plot_task('Practice', 10, 'ex2', 2, fig, axs, legend = False)
# plot_task('Test', 10, 'test2', 3, fig, axs, legend = False)
# plot_task('Practice', 11, 'ex3', 4, fig, axs, legend = False)
# plot_task('Test', 12, 'test3', 5, fig, axs, legend = False)
# plot_task('Practice', 13, 'ex4', 6, fig, axs, legend = False)
# plot_task('Test', 13, 'test4', 7, fig, axs, legend = False)
# plot_task('Practice', 14, 'ex5', 8, fig, axs, legend = False)
# plot_task('Test', 15, 'test5', 9, fig, axs, legend = False)
#
#
# fig, axs = plt.subplots(1,5, sharey=True)
# fig.suptitle('Retention Aviv')
# # axs[0].set_ylim([0, 0.75])
#
# plot_task('Retention', 16, 'ex1', 0, fig, axs)
# plot_task('Retention', 17, 'ex2', 1, fig, axs, legend = False)
# plot_task('Retention', 18, 'ex3', 2, fig, axs, legend = False)
# plot_task('Retention', 19, 'ex4', 3, fig, axs, legend = False)
# plot_task('Retention', 20, 'ex4', 4, fig, axs, legend = False)

#############
#
# Hila's Pilot
#
# df = pd.read_csv('2022-08-08_error_fixed.csv')
# fig, axs = plt.subplots(1,4, sharey=True)
# fig.suptitle('calibration Hila')
# axs[0].set_ylim([0, 2])
# plot_task('Calibration', 7, 'ex1', 0, fig, axs)
# plot_task('Calibration', 8, 'ex2', 1, fig, axs, legend = False)
# plot_task('Calibration', 10, 'ex3', 2, fig, axs, legend = False)
#
# fig, axs = plt.subplots(1,10, sharey=True)
# fig.suptitle('practice Hila')
# # axs[0].set_ylim([0, 0.75])
#
# plot_task('Practice', 18, 'ex1', 0, fig, axs)
# plot_task('Test', 19, 'test1', 1, fig, axs, legend = False)
# plot_task('Test', 20, 'trans', 2, fig, axs, legend = False)
#
# plot_task('Practice', 21, 'ex3', 4, fig, axs, legend = False)
# plot_task('Test', 22, 'test3', 5, fig, axs, legend = False)
# plot_task('Practice', 23, 'ex4', 6, fig, axs, legend = False)
# plot_task('Test', 23, 'test4', 7, fig, axs, legend = False)
# plot_task('Practice', 24, 'ex5', 8, fig, axs, legend = False)
# plot_task('Test', 25, 'test5', 9, fig, axs, legend = False)
#
#
# fig, axs = plt.subplots(1,5, sharey=True)
# fig.suptitle('Retention Hila')
# # axs[0].set_ylim([0, 0.75])
#
# plot_task('Retention', 26, 'ex1', 0, fig, axs)
# plot_task('Retention', 27, 'ex2', 1, fig, axs, legend = False)
# plot_task('Retention', 28, 'ex3', 2, fig, axs, legend = False)
# plot_task('Retention', 31, 'ex4', 3, fig, axs, legend = False)
# plot_task('None', 32, 'ex4', 4, fig, axs, legend = False)


#############
#
# Par. 1 's Pilot
#
# df = pd.read_csv('2022-08-17_error_fixed2.csv')
# df = df[(df.user_id == '1')]
# fig, axs = plt.subplots(2,4, sharey='row')
# fig.suptitle('calibration par.1', fontsize=10)
# axs[0,0].set_ylim([0, 0.75])
# axs[1,0].set_ylim([1, 7])
# plot_task('Calibration', 6, 'ex1', 0, fig, axs)
# plot_task('Calibration', 7, 'ex2', 1, fig, axs, legend = False)
# plot_task('Calibration', 8, 'ex3', 2, fig, axs, legend = False)
#
# fig, axs = plt.subplots(2,10, sharey='row')
# fig.suptitle('practice par.1')
# axs[0,0].set_ylim([0, 0.75])
# axs[1,0].set_ylim([1, 7])
#
# plot_task('Practice', 9, 'ex1', 0, fig, axs)
# plot_task('Test', 10, 'test1', 1, fig, axs, legend = False)
# plot_task('Test', 11, 'trans', 2, fig, axs, legend = False)
#
# plot_task('Practice', 12, 'ex3', 4, fig, axs, legend = False)
# plot_task('Test', 13, 'test3', 5, fig, axs, legend = False)
# plot_task('Practice', 14, 'ex4', 6, fig, axs, legend = False)
# plot_task('Test', 15, 'test4', 7, fig, axs, legend = False)
# plot_task('Practice', 16, 'ex5', 8, fig, axs, legend = False)
# plot_task('Test', 17, 'test5', 9, fig, axs, legend = False)
# axs[0,0].set_ylim([0, 0.75])
# axs[1,0].set_ylim([1, 7])
#
# fig, axs = plt.subplots(2,5, sharey='row')
# fig.suptitle('Retention par.1')
# # axs[0].set_ylim([0, 0.75])
#
# plot_task('Retention', 18, 'ex1', 0, fig, axs)
# plot_task('Retention', 19, 'ex2', 1, fig, axs, legend = False)
# plot_task('Retention', 20, 'ex3', 2, fig, axs, legend = False)
# plot_task('Retention', 21, 'ex4', 3, fig, axs, legend = False)
# plot_task('Retention', 22, 'ex5', 4, fig, axs, legend = False)
# axs[0,0].set_ylim([0, 0.5])
# axs[1,0].set_ylim([1, 7])


# Par. 2 's Pilot
#
# df = pd.read_csv('2022-08-17_error_fixed2.csv')
# df = df[(df.user_id == '2')]
# fig, axs = plt.subplots(2,4, sharey='row')
# fig.suptitle('calibration par.2', fontsize=10)
# axs[0,0].set_ylim([0, 0.75])
# axs[1,0].set_ylim([1, 7])
# plot_task('Calibration', 3, 'ex1', 0, fig, axs)
# plot_task('Calibration', 4, 'ex2', 1, fig, axs, legend = False)
# plot_task('Calibration', 5, 'ex3', 2, fig, axs, legend = False)
#
# fig, axs = plt.subplots(2,10, sharey='row')
# fig.suptitle('practice par.2')
# axs[0,0].set_ylim([0, 0.75])
# axs[1,0].set_ylim([1, 7])
#
# plot_task('Practice', 6, 'ex1', 0, fig, axs)
# plot_task('Test', 7, 'test1', 1, fig, axs, legend = False)
# plot_task('Test', 8, 'trans', 2, fig, axs, legend = False)
#
# plot_task('Practice', 9, 'ex3', 4, fig, axs, legend = False)
# plot_task('Test', 11, 'test3', 5, fig, axs, legend = False)
# plot_task('Practice', 12, 'ex4', 6, fig, axs, legend = False)
# plot_task('Test', 13, 'test4', 7, fig, axs, legend = False)
# plot_task('Practice', 14, 'ex5', 8, fig, axs, legend = False)
# plot_task('Test', 15, 'test5', 9, fig, axs, legend = False)
# axs[0,0].set_ylim([0, 0.75])
# axs[1,0].set_ylim([1, 7])
#
# fig, axs = plt.subplots(2,5, sharey='row')
# fig.suptitle('Retention par.2')
# # axs[0].set_ylim([0, 0.75])
#
# plot_task('Retention', 18, 'ex1', 0, fig, axs)
# plot_task('Retention', 19, 'ex2', 1, fig, axs, legend = False)
# plot_task('Retention', 20, 'ex3', 2, fig, axs, legend = False)
# plot_task('Retention', 21, 'ex4', 3, fig, axs, legend = False)
# plot_task('Retention', 22, 'ex5', 4, fig, axs, legend = False)
# axs[0,0].set_ylim([0, 0.5])
# axs[1,0].set_ylim([1, 7])
#

# Par. 3 's Pilot

tasks_num = [[6,7,8],[[9,10],11,[12,13],[14,15],[16,17]],[18,19,20,21,22],'par. 1','1']

#tasks_num = [[3,4,5],[[6,7],8,[9,11],[12,13],[14,15]],[18,19,20,21,22],'par. 2','2']

#tasks_num = [[3,4,5],[[6,7],8,[9,11],[12,12],[13,None]],[14,15,16,17,18],'par. 3','3']

#tasks_num = [[4,5,6],[[8,9],11,[13,14],[15,17],[18,19]],[21,22,24,25,26],'par. 4','4']

#tasks_num = [[4,5,6],[[7,8],9,[10,11],[12,13],[14,15]],[18,20,22,24,26],'par. 5','5']

#tasks_num = [[3,4,5],[[6,8],9,[10,10],[13,14],[16,17]],[18,19,20,21,22],'par. 6','6']

#tasks_num = [[4,5,7],[[8,8],9,[10,11],[12,12],[13,14]],[15,16,19,22,23],'par. 7','7']

#tasks_num = [[2,3,4],[[6,7],8,[9,10],[11,12],[14,15]],[17,20,21,22,24],'par. 8','8']

#tasks_num = [[3,4,5],[[7,8],9,[11,13],[15,16],[18,19]],[21,22,24,25,28],'par. 9','9']

#tasks_num = [[3,7,8],[[4,6],7,[8,9],[11,13],[15,16]],[18,20,22,25,27],'par. 10','10']

#tasks_num = [[2,3,4],[[5,6],7,[8,9],[11,12],[14,16]],[18,19,21,23,24],'par. 11','11']

#tasks_num = [[5,6,7],[[8,9],11,[12,13],[14,15],[16,19]],[22,[24 25]!!,26,28,29],'par. 12','12']

#tasks_num = [[8,9,10],[[11,12],13,[14,16],[17,18],[19,21]],[22,23,24,25,26],'par. 13','13']

#tasks_num = [[5,6,8],[[10,11],12,[13,14],[15,16],[17,18]],[20,21,22,23,24],'par. 14','14']

df = pd.read_csv('2022-08-17_error_fixed2.csv')
df = df[(df.user_id == tasks_num[4])]
fig, axs = plt.subplots(2,4, sharey='row')
fig.suptitle('Calibration ' + tasks_num[3], fontsize=10)
axs[0,0].set_ylim([0, 1.75])
axs[1,0].set_ylim([1, 7])
plot_task('Calibration', tasks_num[0][0], 'ex1', 0, fig, axs)
plot_task('Calibration', tasks_num[0][1], 'ex2', 1, fig, axs, legend = False)
plot_task('Calibration', tasks_num[0][2], 'ex3', 2, fig, axs, legend = False)

fig, axs = plt.subplots(2,10, sharey='row')
fig.suptitle('practice ' + tasks_num[3])
axs[0,0].set_ylim([0, 1.75])
axs[1,0].set_ylim([1, 7])

plot_task('Practice', tasks_num[1][0][0], 'ex1', 0, fig, axs)
plot_task('Test', tasks_num[1][0][1], 'test1', 1, fig, axs, legend = False)
plot_task('Test', tasks_num[1][1], 'trans', 2, fig, axs, legend = False)

plot_task('Practice', tasks_num[1][2][0], 'ex3', 4, fig, axs, legend = False)
plot_task('Test', tasks_num[1][2][1], 'test3', 5, fig, axs, legend = False)
plot_task('Practice', tasks_num[1][3][0], 'ex4', 6, fig, axs, legend = False)
plot_task('Test', tasks_num[1][3][1], 'test4', 7, fig, axs, legend = False)
plot_task('Practice', tasks_num[1][4][0], 'ex5', 8, fig, axs, legend = False)
try:
    plot_task('Test', tasks_num[1][4][1], 'test5', 9, fig, axs, legend = False)
except:
    print("missing data")
axs[0,0].set_ylim([0, 1.75])
axs[1,0].set_ylim([1, 7])

fig, axs = plt.subplots(2,5, sharey='row')
fig.suptitle('Retention ' + tasks_num[3])
# axs[0].set_ylim([0, 0.75])

plot_task('Retention', tasks_num[2][0], 'ex1', 0, fig, axs)
plot_task('Retention', tasks_num[2][1], 'ex2', 1, fig, axs, legend = False)
plot_task('Retention', tasks_num[2][2], 'ex3', 2, fig, axs, legend = False)
plot_task('Retention', tasks_num[2][3], 'ex4', 3, fig, axs, legend = False)
plot_task('Retention', tasks_num[2][4], 'ex5', 4, fig, axs, legend = False)
axs[0,0].set_ylim([0, 1.5])
axs[1,0].set_ylim([1, 7])


plt.show()



# Hide x labels and tick labels for top plots and y ticks for right plots.
for ax in axs.flat:
    ax.label_outer()


