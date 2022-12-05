import numpy as np
import matplotlib.pyplot as plt
import csv

import pandas as pd
all_participants = [
[[6,7,8],[[9,10],11,[12,13],[14,15],[16,17]],[18,19,20,21,22],'par. 1','1', [0,2,3,4]],
[[3,4,5],[[6,7],8,[9,11],[12,13],[14,15]],[18,19,20,21,22],'par. 2','2', [4,0,2,3]],
[[3,4,5],[[6,7],8,[9,11],[12,12],[13,None]],[14,15,16,17,18],'par. 3','3', [3,4,0,2]],
[[4,5,6],[[8,9],11,[13,14],[15,17],[18,19]],[21,22,24,25,26],'par. 4','4', [2,3,4,0]],
[[4,5,6],[[7,8],9,[10,11],[12,13],[14,15]],[18,20,22,24,26],'par. 5','5', [0,2,3,4]],
[[3,4,5],[[6,8],9,[10,10],[13,14],[16,17]],[18,19,20,21,22],'par. 6','6', [4,0,2,3]],
[[4,5,7],[[8,8],9,[10,11],[12,12],[13,14]],[15,16,19,22,23],'par. 7','7', [3,4,0,2]],
[[2,3,4],[[6,7],8,[9,10],[11,12],[14,15]],[17,20,21,22,24],'par. 8','8', [2,3,4,0]],
[[3,4,5],[[7,8],9,[11,13],[15,16],[18,19]],[21,22,24,25,28],'par. 9','9', [0,2,3,4]],
[[3,7,8],[[4,6],7,[8,9],[11,13],[15,16]],[18,20,22,25,27],'par. 10','10', [4,0,2,3]],
[[2,3,4],[[5,6],7,[8,9],[11,12],[14,16]],[18,19,21,23,24],'par. 11','11', [3,4,0,2]],
[[5,6,7],[[8,9],11,[12,13],[14,15],[16,19]],[22,[24,25],'!!',26,28,29],'par. 12','12', [2,3,4,0]],
[[8,9,10],[[11,12],13,[14,16],[17,18],[19,21]],[22,23,24,25,26],'par. 13','13',[0,2,3,4]],
[[5,6,8],[[10,11],12,[13,14],[15,16],[17,18]],[20,21,22,23,24],'par. 14','14', [4,0,2,3]],
[[3,4,6],[[7,8],9,[10,12],[13,14],[15,16]],[17,18,19,20,21],'par. 15','15', [3,4,0,2]],
[[7,8,9],[[10,11],12,[13,14],[15,16],[17,18]],[20,21,22,23,24],'par. 16','16', [2,3,4,0]],
[[5,6,7],[[8,9],10,[11,12],[13,14],[15,16]],[18,19,20,21,22],'par. 17','17', [0,2,3,4]],
[[3,4,5],[[7,9],10,[11,12],[13,17],[18,19]],[21,22,23,24,25],'par. 18','18', [4,0,2,3]],
[[4,5,6],[[7,8],9,[10,11],[12,13],[14,16]],[18,19,20,21,22],'par. 19','19', [3,4,0,2]]
]

def calcAggreg(all_participants):

    df = pd.read_csv('all_participants.csv')

    diff_tempo1 = []
    diff_tempo2 = []
    diff_tempo3 = []
    diff_tempo4 = []
    avg_diff_tempo1 = 0
    avg_diff_tempo2 = 0
    avg_diff_tempo3 = 0
    avg_diff_no_tempo = 0

    for par in all_participants:
        df_user = df[(df.user_id == par[4])]

        no_tempo_test = par[1][par[5][0]][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == no_tempo_test)]
        y = df_task['diff_rating']
        print(y)
        diff_tempo1.append(y.values.astype(np.float)[0])

        slow_tempo_test = par[1][par[5][1]][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == slow_tempo_test)]
        y = df_task['diff_rating']
        print(y)
        diff_tempo2.append(y.values.astype(np.float)[0])

        med_tempo_test = par[1][par[5][2]][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == med_tempo_test)]
        y = df_task['diff_rating']
        print(y)
        diff_tempo3.append(y.values.astype(np.float)[0])

        high_tempo_test = par[1][par[5][3]][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == high_tempo_test)]
        y = df_task['diff_rating']
        print(y)
        diff_tempo4.append(y.values.astype(np.float)[0])

        #print(par[1][par[5][0]][1])

    return diff_tempo1, diff_tempo2, diff_tempo3, diff_tempo4

def calcAggregByVar(all_participants, variable):

    df = pd.read_csv('all_participants.csv')

    var_no_tempo = []
    var_tempo_slow =[]
    var_tempo_med = []
    var_tempo_high = []
    # diff_tempo2 = []
    # diff_tempo3 = []
    # diff_tempo4 = []
    avg_diff_tempo1 = 0
    avg_diff_tempo2 = 0
    avg_diff_tempo3 = 0
    avg_diff_no_tempo = 0

    for par in all_participants:
        df_user = df[(df.user_id == par[4])]

        no_tempo_test = par[1][par[5][0]][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == no_tempo_test)]
        y = df_task[variable]
        print(y)
        var_no_tempo.append(y.values.astype(np.float)[0])

        slow_tempo_test = par[1][par[5][1]][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == slow_tempo_test)]
        y = df_task[variable]
        print(y)
        var_tempo_slow.append(y.values.astype(np.float)[0])

        med_tempo_test = par[1][par[5][2]][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == med_tempo_test)]
        y = df_task[variable]
        print(y)
        var_tempo_med.append(y.values.astype(np.float)[0])

        high_tempo_test = par[1][par[5][3]][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == high_tempo_test)]
        y = df_task[variable]
        print(y)
        var_tempo_high.append(y.values.astype(np.float)[0])

        #print(par[1][par[5][0]][1])

    return var_no_tempo, var_tempo_slow, var_tempo_med, var_tempo_high
some_participants_indexes = [4,5,8,10,12,13,14,15,16,17,18]
some_participants = [all_participants[index] for index in [4,5,8,10,12,13,14,15,16,17,18]]
diff_tempo1, diff_tempo2, diff_tempo3, diff_tempo4 = calcAggreg(some_participants)
print(diff_tempo3)
print(diff_tempo4)
print(np.mean(diff_tempo1))
print(np.mean(diff_tempo2))
print(np.mean(diff_tempo3))
print(np.mean(diff_tempo4))
diff_tempo1, diff_tempo2, diff_tempo3, diff_tempo4 = calcAggregByVar(some_participants, 'Summed_right')
print(np.mean(diff_tempo1))
print(np.mean(diff_tempo2))
print(np.mean(diff_tempo3))
print(np.mean(diff_tempo4))

diff_no_tempo_test, diff_tempo_slow_test, diff_tempo_med_test, diff_tempo_high_test = calcAggregByVar(some_participants, 'diff_rating')
perf_no_tempo_test, perf_tempo_slow_test, perf_tempo_med_test, perf_tempo_high_test = calcAggregByVar(some_participants, 'perf_rating')
err_no_tempo_test, err_tempo_slow_test, err_tempo_med_test, err_tempo_high_test = calcAggregByVar(some_participants, 'Summed_right')

df_par = pd.DataFrame({'id':some_participants_indexes,
                       'diff_no_tempo_test':diff_no_tempo_test,
                       'perf_no_tempo_test':perf_no_tempo_test,
                       'err_no_tempo_test':err_no_tempo_test,
                       'diff_tempo_slow_test':diff_tempo_slow_test,
                       'perf_tempo_slow_test':perf_tempo_slow_test,
                       'err_tempo_slow_test':err_tempo_slow_test,
                       'diff_tempo_med_test':diff_tempo_med_test,
                       'perf_tempo_med_test':perf_tempo_med_test,
                       'err_tempo_med_test':err_tempo_med_test,
                       'diff_tempo_high_test':diff_tempo_high_test,
                       'perf_tempo_high_test':perf_tempo_high_test,
                       'err_tempo_high_test':err_tempo_high_test})

df_par.to_csv('participants_proc.csv')

df = pd.read_csv('all_participants.csv')
df_filter = df[(df['diff_rating']!='None') & (df['perf_rating']!='None')]
df_1= df_filter['diff_rating'].astype('int')
df_2 = df_filter['perf_rating'].astype('int')

#df['diff_rating'] = df[df['diff_rating']!='None']['diff_rating'].astype('int')

hist = df_1.hist(bins=100)
plt.figure()
plt.hist2d(df_1, df_2)

#df.plot(x='diff_rating', y='perf_rating', marker='o')

plt.show()