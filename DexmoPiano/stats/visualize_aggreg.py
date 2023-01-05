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
[[4,5,6],[[7,8],9,[10,11],[12,13],[14,16]],[18,19,20,21,22],'par. 19','19', [3,4,0,2]],
[[5,6,7],[[8,8],9,[11,12],[13,14],[16,18]],[20,21,22,23,24],'par. 20','20', [0,2,3,4]],
[[3,4,5],[[6,7],8,[9,10],[11,12],[13,14]],[18,19,20,21,22],'par. 21','21', [4,0,2,3]],
[[3,4,5],[[6,7],8,[9,11],[12,13],[14,15]],[17,19,20,21,22],'par. 22','22', [3,4,0,2]],
[[2,3,6],[[8,9],10,[11,12],[13,14],[15,18]],[21,22,23,25,26],'par. 23','23', [2,3,4,0]],
[[2,3,4],[[6,8],9,[11,12],[13,14],[15,16]],[18,19,21,22,23],'par. 24','24', [0,2,3,4]],
[[3,4,5],[[6,7],8,[10,11],[12,13],[14,17]],[19,20,21,22,23],'par. 25','25', [4,0,2,3]],
[[3,4,5],[[6,7],8,[9,10],[12,13],[16,17]],[19,20,21,22,24],'par. 26','26', [3,4,0,2]],
[[3,4,5],[[6,7],8,[9,10],[11,13],[15,16]],[18,19,20,21,22],'par. 27','27', [2,3,4,0]],
[[2,3,4],[[5,6],7,[8,9],[11,12],[13,14]],[16,17,18,20,21],'par. 28','28', [0,2,3,4]],
[[4,5,6],[[2,3],4,[6,7],[8,9],[10,11]],[13,14,15,16,17],'par. 29','29', [4,0,2,3]],

]

def calcShortTable(all_participants):
    df = pd.read_csv('all_participants.csv')

    user_id = []
    tempo = []
    order = []
    diff = []
    complexity = []
    prac1_err = []
    prac1_diff = []
    prac1_perf = []
    prac2_err = []
    prac2_diff = []
    prac2_perf = []
    prac3_err = []
    prac3_diff = []
    prac3_perf = []
    prac4_err = []
    prac4_diff = []
    prac4_perf = []
    prac5_err = []
    prac5_diff = []
    prac5_perf = []
    test_err = []
    test_diff = []
    test_perf = []
    ret1_err = []
    ret1_diff = []
    ret1_perf = []
    ret2_err = []
    ret2_diff = []
    ret2_perf = []
    ret3_err = []
    ret3_diff = []
    ret3_perf = []

    for par in all_participants:
        df_user = df[(df.user_id == par[4])]
        ret = par[2][0]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == ret)]
        y = df_task['bpm']
        bpm = int(y.values[0])
        prac_indexes = [0,2,3,4]
        for k in [0, 1, 2, 3]:
            user_id.append(par[4])
            order.append(k) # first practice
            diff.append(par[5][k])
            tempo.append(bpm)
            tempo1_task = par[1][prac_indexes[k]][0]
            df_task = df_user[(df_user.phase == 'Practice') & (df_user.task_number == tempo1_task)]
            y = df_task['Summed_right']
            prac1_err.append(y.values[0].astype(float))
            prac2_err.append(y.values[1].astype(float))
            prac3_err.append(y.values[2].astype(float))
            prac4_err.append(y.values[3].astype(float))
#            prac5_err.append(y.values[4].astype(float))
            y = df_task['diff_rating']
            prac1_diff.append(int(y.values[0]))
            prac2_diff.append(int(y.values[1]))
            prac3_diff.append(int(y.values[2]))
            prac4_diff.append(int(y.values[3]))
#            prac5_diff.append(int(y.values[4]))
            y = df_task['perf_rating']
            prac1_perf.append(int(y.values[0]))
            prac2_perf.append(int(y.values[1]))
            prac3_perf.append(int(y.values[2]))
            prac4_perf.append(int(y.values[3]))
#            prac5_perf.append(int(y.values[4]))

            tempo1_test = par[1][prac_indexes[k]][1]
            df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == tempo1_test)]
            y = df_task['Summed_right']
            test_err.append(y.values[0].astype(float))
            y = df_task['diff_rating']
            test_diff.append(int(y.values[0]))
            y = df_task['perf_rating']
            test_perf.append(int(y.values[0]))

            task_retention = par[2][prac_indexes[k]]
            df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == task_retention)]
            y = df_task['Summed_right']
            ret1_err.append(y.values[0].astype(float))
            ret2_err.append(y.values[1].astype(float))
#            ret3_err.append(y.values[2].astype(float))
            y = df_task['diff_rating']
            ret1_diff.append(int(y.values[0]))
            ret2_diff.append(int(y.values[1]))
#            ret3_diff.append(int(y.values[2]))
            y = df_task['perf_rating']
            ret1_perf.append(int(y.values[0]))
            ret2_perf.append(int(y.values[1]))
 #           ret3_perf.append(int(y.values[2]))

    df_par = pd.DataFrame({'id': user_id,
                           'mid_tempo': tempo,
                           'order': order,
                           'diff': diff,
                         #  'complexity': complexity,
                           'prac1_diff': prac1_diff,
                           'prac1_perf': prac1_perf,
                           'prac1_err': prac1_err,
                           'prac2_diff': prac2_diff,
                           'prac2_perf': prac2_perf,
                           'prac2_err': prac2_err,
                           'prac3_diff': prac3_diff,
                           'prac3_perf': prac3_perf,
                           'prac3_err': prac3_err,
                           'prac4_diff': prac4_diff,
                           'prac4_perf': prac4_perf,
                           'prac4_err': prac4_err,
  #                         'prac5_diff': prac5_diff,
   #                        'prac5_perf': prac5_perf,
    #                       'prac5_err': prac5_err,
                           'test_diff': test_diff,
                           'test_err':  test_err,
                           'test_perf': test_perf,
                           'ret1_diff': ret1_diff,
                           'ret1_err': ret1_err,
                           'ret1_perf': ret1_perf,
                           'ret2_diff': ret2_diff,
                           'ret2_err': ret2_err,
                           'ret2_perf': ret2_perf
    #                       'ret3_diff': ret3_diff,
     #                      'ret3_err': ret3_err,
      #                     'ret3_perf': ret3_perf



                           })

    df_par.to_csv('participants_short.csv')


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

def calcAggregTestByVar(all_participants, variable):

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

def calcAggregTestByVarOrdered(all_participants, variable):

    df = pd.read_csv('all_participants.csv')

    var_tempo1 = []
    var_tempo2 =[]
    var_tempo3 = []
    var_tempo4 = []
    # diff_tempo2 = []
    # diff_tempo3 = []
    # diff_tempo4 = []
    avg_diff_tempo1 = 0
    avg_diff_tempo2 = 0
    avg_diff_tempo3 = 0
    avg_diff_no_tempo = 0

    for par in all_participants:
        df_user = df[(df.user_id == par[4])]

        tempo1_test = par[1][0][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == tempo1_test)]
        y = df_task[variable]
        print(y)
        var_tempo1.append(y.values.astype(np.float)[0])

        tempo2_test = par[1][2][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == tempo2_test)]
        y = df_task[variable]
        print(y)
        var_tempo2.append(y.values.astype(np.float)[0])

        tempo3_test = par[1][3][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == tempo3_test)]
        y = df_task[variable]
        print(y)
        var_tempo3.append(y.values.astype(np.float)[0])

        tempo4_test = par[1][4][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == tempo4_test)]
        y = df_task[variable]
        print(y)
        var_tempo4.append(y.values.astype(np.float)[0])

        #print(par[1][par[5][0]][1])

    return var_tempo1, var_tempo2, var_tempo3, var_tempo4

def calcAggregRetenByVar(all_participants, variable):

    df = pd.read_csv('all_participants.csv')

    var_no_tempo = []
    var_tempo_slow =[]
    var_tempo_med = []
    var_tempo_high = []
    var_trans = []

    # diff_tempo2 = []
    # diff_tempo3 = []
    # diff_tempo4 = []
    avg_diff_tempo1 = 0
    avg_diff_tempo2 = 0
    avg_diff_tempo3 = 0
    avg_diff_no_tempo = 0

    for par in all_participants:
        df_user = df[(df.user_id == par[4])]

        no_tempo_test = par[2][par[5][0]]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == no_tempo_test)]
        y = df_task[variable]
        print(y)
        var_no_tempo.append(np.mean(y.values.astype(float)))

        slow_tempo_test = par[2][par[5][1]]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == slow_tempo_test)]
        y = df_task[variable]
        print(y)
        var_tempo_slow.append(np.mean(y.values.astype(float)))

        med_tempo_test = par[2][par[5][2]]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == med_tempo_test)]
        y = df_task[variable]
        print(y)
        var_tempo_med.append(np.mean(y.values.astype(float)))

        high_tempo_test = par[2][par[5][3]]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == high_tempo_test)]
        y = df_task[variable]
        print(y)
        var_tempo_high.append(np.mean(y.values.astype(float)))

        transfer_test = par[2][1]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == transfer_test)]
        y = df_task[variable]
        print(y)
        var_trans.append(np.mean(y.values.astype(float)))

        #print(par[1][par[5][0]][1])

    return var_no_tempo, var_tempo_slow, var_tempo_med, var_tempo_high, var_trans

def calcAggregRetenByVarOrdered(all_participants, variable):

    df = pd.read_csv('all_participants.csv')

    var_tempo1 = []
    var_tempo2 =[]
    var_tempo3 = []
    var_tempo4 = []
    var_trans = []

    # diff_tempo2 = []
    # diff_tempo3 = []
    # diff_tempo4 = []
    avg_diff_tempo1 = 0
    avg_diff_tempo2 = 0
    avg_diff_tempo3 = 0
    avg_diff_no_tempo = 0

    for par in all_participants:
        df_user = df[(df.user_id == par[4])]

        tempo1_test = par[2][0]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == tempo1_test)]
        y = df_task[variable]
        print(y)
        var_tempo1.append(np.mean(y.values.astype(float)))

        tempo2_test = par[2][2]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == tempo2_test)]
        y = df_task[variable]
        print(y)
        var_tempo2.append(np.mean(y.values.astype(float)))

        tempo3_test = par[2][3]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == tempo3_test)]
        y = df_task[variable]
        print(y)
        var_tempo3.append(np.mean(y.values.astype(float)))

        tempo4_test = par[2][4]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == tempo4_test)]
        y = df_task[variable]
        print(y)
        var_tempo4.append(np.mean(y.values.astype(float)))

        transfer_test = par[2][1]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == transfer_test)]
        y = df_task[variable]
        print(y)
        var_trans.append(np.mean(y.values.astype(float)))

        #print(par[1][par[5][0]][1])

    return var_tempo1, var_tempo2, var_tempo3, var_tempo4, var_trans

def calcAggregPracByVar(all_participants, variable):

    df = pd.read_csv('all_participants.csv')

    var_no_tempo = []
    var_tempo_slow =[]
    var_tempo_med = []
    var_tempo_high = []
    var_trans = []

    # diff_tempo2 = []
    # diff_tempo3 = []
    # diff_tempo4 = []
    avg_diff_tempo1 = 0
    avg_diff_tempo2 = 0
    avg_diff_tempo3 = 0
    avg_diff_no_tempo = 0

    for par in all_participants:
        df_user = df[(df.user_id == par[4])]

        no_tempo_test = par[1][par[5][0]][0]
        df_task = df_user[(df_user.phase == 'Practice') & (df_user.task_number == no_tempo_test)]
        y = df_task[variable]
        print(y)
        var_no_tempo.append(np.mean(y.values.astype(float)))

        slow_tempo_test = par[1][par[5][1]][0]
        df_task = df_user[(df_user.phase == 'Practice') & (df_user.task_number == slow_tempo_test)]
        y = df_task[variable]
        print(y)
        var_tempo_slow.append(np.mean(y.values.astype(float)))

        med_tempo_test = par[1][par[5][2]][0]
        df_task = df_user[(df_user.phase == 'Practice') & (df_user.task_number == med_tempo_test)]
        y = df_task[variable]
        print(y)
        var_tempo_med.append(np.mean(y.values.astype(float)))

        high_tempo_test = par[1][par[5][3]][0]
        df_task = df_user[(df_user.phase == 'Practice') & (df_user.task_number == high_tempo_test)]
        y = df_task[variable]
        print(y)
        var_tempo_high.append(np.mean(y.values.astype(float)))

        transfer_test = par[1][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == transfer_test)]
        y = df_task[variable]
        print(y)
        var_trans.append(np.mean(y.values.astype(float)))

        #print(par[1][par[5][0]][1])

    return var_no_tempo, var_tempo_slow, var_tempo_med, var_tempo_high, var_trans

def calcAggregPracByVarOrdered(all_participants, variable):

    df = pd.read_csv('all_participants.csv')

    var_tempo1 = []
    var_tempo2 =[]
    var_tempo3 = []
    var_tempo4 = []
    var_trans = []

    # diff_tempo2 = []
    # diff_tempo3 = []
    # diff_tempo4 = []
    avg_diff_tempo1 = 0
    avg_diff_tempo2 = 0
    avg_diff_tempo3 = 0
    avg_diff_no_tempo = 0

    for par in all_participants:
        df_user = df[(df.user_id == par[4])]

        tempo1_test = par[1][0][0]
        df_task = df_user[(df_user.phase == 'Practice') & (df_user.task_number == tempo1_test)]
        y = df_task[variable]
        print(y)
        var_tempo1.append(np.mean(y.values.astype(float)))

        tempo2_test = par[1][2][0]
        df_task = df_user[(df_user.phase == 'Practice') & (df_user.task_number == tempo2_test)]
        y = df_task[variable]
        print(y)
        var_tempo2.append(np.mean(y.values.astype(float)))

        tempo3_test = par[1][3][0]
        df_task = df_user[(df_user.phase == 'Practice') & (df_user.task_number == tempo3_test)]
        y = df_task[variable]
        print(y)
        var_tempo3.append(np.mean(y.values.astype(float)))

        tempo4_test = par[1][4][0]
        df_task = df_user[(df_user.phase == 'Practice') & (df_user.task_number == tempo4_test)]
        y = df_task[variable]
        print(y)
        var_tempo4.append(np.mean(y.values.astype(float)))

        transfer_test = par[1][1]
        df_task = df_user[(df_user.phase == 'Test') & (df_user.task_number == transfer_test)]
        y = df_task[variable]
        print(y)
        var_trans.append(np.mean(y.values.astype(float)))

        #print(par[1][par[5][0]][1])

    return var_tempo1, var_tempo2, var_tempo3, var_tempo4, var_trans

def getMidTempo(all_participants):
    df = pd.read_csv('all_participants.csv')
    mid_tempo = []

    for par in all_participants:
        df_user = df[(df.user_id == par[4])]
        ret = par[2][0]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == ret)]
        y = df_task['bpm']
        mid_tempo.append(int(y.values[0]))

    return mid_tempo

def getComplexity(all_participants):
    df = pd.read_csv('all_participants.csv')
    complex = []

    for par in all_participants:
        df_user = df[(df.user_id == par[4])]
        ret = par[2][0]
        df_task = df_user[(df_user.phase == 'Retention') & (df_user.task_number == ret)]
        y = df_task['complexityLevel']
        if y.values[0].find('C_TO_G')>0:
            comp = 5
        else:
            comp = 3
        complex.append(comp)

    return complex

some_participants_indexes = [4,5,8,10,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28]
some_participants = [all_participants[index] for index in some_participants_indexes]
user_ids = [all_participants[index][4] for index in some_participants_indexes]

diff_tempo1, diff_tempo2, diff_tempo3, diff_tempo4 = calcAggreg(some_participants)
print(diff_tempo3)
print(diff_tempo4)
print(np.mean(diff_tempo1))
print(np.mean(diff_tempo2))
print(np.mean(diff_tempo3))
print(np.mean(diff_tempo4))
# diff_tempo1, diff_tempo2, diff_tempo3, diff_tempo4 = calcAggregByVar(some_participants, 'Summed_right')
# print(np.mean(diff_tempo1))
# print(np.mean(diff_tempo2))
# print(np.mean(diff_tempo3))
# print(np.mean(diff_tempo4))

mid_tempo = getMidTempo(some_participants)
complex = getComplexity(some_participants)

calcShortTable(some_participants)

diff_no_tempo_test, diff_tempo_slow_test, diff_tempo_med_test, diff_tempo_high_test = calcAggregTestByVar(some_participants, 'diff_rating')
perf_no_tempo_test, perf_tempo_slow_test, perf_tempo_med_test, perf_tempo_high_test = calcAggregTestByVar(some_participants, 'perf_rating')
err_no_tempo_test, err_tempo_slow_test, err_tempo_med_test, err_tempo_high_test = calcAggregTestByVar(some_participants, 'Summed_right')

diff_no_tempo_ret, diff_tempo_slow_ret, diff_tempo_med_ret, diff_tempo_high_ret, diff_trans_ret = calcAggregRetenByVar(some_participants, 'diff_rating')
perf_no_tempo_ret, perf_tempo_slow_ret, perf_tempo_med_ret, perf_tempo_high_ret, perf_trans_ret = calcAggregRetenByVar(some_participants, 'perf_rating')
err_no_tempo_ret, err_tempo_slow_ret, err_tempo_med_ret, err_tempo_high_ret, err_trans_ret = calcAggregRetenByVar(some_participants, 'Summed_right')

diff_no_tempo_prac, diff_tempo_slow_prac, diff_tempo_med_prac, diff_tempo_high_prac, diff_trans_prac = calcAggregPracByVar(some_participants, 'diff_rating')
perf_no_tempo_prac, perf_tempo_slow_prac, perf_tempo_med_prac, perf_tempo_high_prac, perf_trans_prac = calcAggregPracByVar(some_participants, 'perf_rating')
err_no_tempo_prac, err_tempo_slow_prac, err_tempo_med_prac, err_tempo_high_prac, err_trans_prac = calcAggregPracByVar(some_participants, 'Summed_right')

diff_tempo1_test, diff_tempo2_test, diff_tempo3_test, diff_tempo4_test = calcAggregTestByVarOrdered(some_participants, 'diff_rating')
perf_tempo1_test, perf_tempo2_test, perf_tempo3_test, perf_tempo4_test = calcAggregTestByVarOrdered(some_participants, 'perf_rating')
err_tempo1_test, err_tempo2_test, err_tempo3_test, err_tempo4_test = calcAggregTestByVarOrdered(some_participants, 'Summed_right')

diff_tempo1_ret, diff_tempo2_ret, diff_tempo3_ret, diff_tempo4_ret, diff_trans_ret = calcAggregRetenByVarOrdered(some_participants, 'diff_rating')
perf_tempo1_ret, perf_tempo2_ret, perf_tempo3_ret, perf_tempo4_ret, perf_trans_ret = calcAggregRetenByVarOrdered(some_participants, 'perf_rating')
err_tempo1_ret, err_tempo2_ret, err_tempo3_ret, err_tempo4_ret, err_trans_ret = calcAggregRetenByVarOrdered(some_participants, 'Summed_right')

diff_tempo1_prac, diff_tempo2_prac, diff_tempo3_prac, diff_tempo4_prac, diff_trans_prac = calcAggregPracByVarOrdered(some_participants, 'diff_rating')
perf_tempo1_prac, perf_tempo2_prac, perf_tempo3_prac, perf_tempo4_prac, perf_trans_prac = calcAggregPracByVarOrdered(some_participants, 'perf_rating')
err_tempo1_prac, err_tempo2_prac, err_tempo3_prac, err_tempo4_prac, err_trans_prac = calcAggregPracByVarOrdered(some_participants, 'Summed_right')


#print(diff_no_tempo_ret, diff_tempo_slow_ret, diff_tempo_med_ret, diff_tempo_high_ret)

df_par = pd.DataFrame({'id':user_ids,
                       'mid_tempo':mid_tempo,
                       'complexity':complex,
                       'diff_no_tempo_prac':diff_no_tempo_prac,
                       'perf_no_tempo_prac':perf_no_tempo_prac,
                       'err_no_tempo_prac':err_no_tempo_prac,

                       'diff_no_tempo_test':diff_no_tempo_test,
                       'perf_no_tempo_test':perf_no_tempo_test,
                       'err_no_tempo_test':err_no_tempo_test,

                       'diff_no_tempo_ret':diff_no_tempo_ret,
                       'perf_no_tempo_ret':perf_no_tempo_ret,
                       'err_no_tempo_ret':err_no_tempo_ret,

                       'diff_tempo_slow_prac':diff_tempo_slow_prac,
                       'perf_tempo_slow_prac':perf_tempo_slow_prac,
                       'err_tempo_slow_prac':err_tempo_slow_prac,

                       'diff_tempo_slow_test':diff_tempo_slow_test,
                       'perf_tempo_slow_test':perf_tempo_slow_test,
                       'err_tempo_slow_test':err_tempo_slow_test,

                       'diff_tempo_slow_ret':diff_tempo_slow_ret,
                       'perf_tempo_slow_ret':perf_tempo_slow_ret,
                       'err_tempo_slow_ret':err_tempo_slow_ret,

                       'diff_tempo_med_prac':diff_tempo_med_prac,
                       'perf_tempo_med_prac':perf_tempo_med_prac,
                       'err_tempo_med_prac':err_tempo_med_prac,

                       'diff_tempo_med_test':diff_tempo_med_test,
                       'perf_tempo_med_test':perf_tempo_med_test,
                       'err_tempo_med_test':err_tempo_med_test,

                       'diff_tempo_med_ret':diff_tempo_med_ret,
                       'perf_tempo_med_ret':perf_tempo_med_ret,
                       'err_tempo_med_ret':err_tempo_med_ret,

                       'diff_tempo_high_prac':diff_tempo_high_prac,
                       'perf_tempo_high_prac':perf_tempo_high_prac,
                       'err_tempo_high_prac':err_tempo_high_prac,

                       'diff_tempo_high_test':diff_tempo_high_test,
                       'perf_tempo_high_test':perf_tempo_high_test,
                       'err_tempo_high_test':err_tempo_high_test,

                       'diff_tempo_high_ret':diff_tempo_high_ret,
                       'perf_tempo_high_ret':perf_tempo_high_ret,
                       'err_tempo_high_ret':err_tempo_high_ret,

                       'diff_trans_prac':diff_trans_prac,
                       'perf_trans_prac':perf_trans_prac,
                       'err_trans_prac':err_trans_prac,

                       'diff_trans_ret':diff_trans_ret,
                       'perf_trans_ret':perf_trans_ret,
                       'err_trans_ret':err_trans_ret,

                       'diff_tempo1_prac':diff_tempo1_prac,
                       'perf_tempo1_prac':perf_tempo1_prac,
                       'err_tempo1_prac':err_tempo1_prac,

                       'diff_tempo1_test':diff_tempo1_test,
                       'perf_tempo1_test':perf_tempo1_test,
                       'err_tempo1_test':err_tempo1_test,

                       'diff_tempo1_ret':diff_tempo1_ret,
                       'perf_tempo1_ret':perf_tempo1_ret,
                       'err_tempo1_ret':err_tempo1_ret,

                       'diff_tempo2_prac':diff_tempo2_prac,
                       'perf_tempo2_prac':perf_tempo2_prac,
                       'err_tempo2_prac':err_tempo2_prac,

                       'diff_tempo2_test':diff_tempo2_test,
                       'perf_tempo2_test':perf_tempo2_test,
                       'err_tempo2_test':err_tempo2_test,

                       'diff_tempo2_ret':diff_tempo2_ret,
                       'perf_tempo2_ret':perf_tempo2_ret,
                       'err_tempo2_ret':err_tempo2_ret,

                       'diff_tempo3_prac':diff_tempo3_prac,
                       'perf_tempo3_prac':perf_tempo3_prac,
                       'err_tempo3_prac':err_tempo3_prac,

                       'diff_tempo3_test':diff_tempo3_test,
                       'perf_tempo3_test':perf_tempo3_test,
                       'err_tempo3_test':err_tempo3_test,

                       'diff_tempo3_ret':diff_tempo3_ret,
                       'perf_tempo3_ret':perf_tempo3_ret,
                       'err_tempo3_ret':err_tempo3_ret,

                       'diff_tempo4_prac':diff_tempo4_prac,
                       'perf_tempo4_prac':perf_tempo4_prac,
                       'err_tempo4_prac':err_tempo4_prac,

                       'diff_tempo4_test':diff_tempo4_test,
                       'perf_tempo4_test':perf_tempo4_test,
                       'err_tempo4_test':err_tempo4_test,

                       'diff_tempo4_ret':diff_tempo4_ret,
                       'perf_tempo4_ret':perf_tempo4_ret,
                       'err_tempo4_ret':err_tempo4_ret,

                       'diff_trans_prac':diff_trans_prac,
                       'perf_trans_prac':perf_trans_prac,
                       'err_trans_prac':err_trans_prac,

                       'diff_trans_ret':diff_trans_ret,
                       'perf_trans_ret':perf_trans_ret,
                       'err_trans_ret':err_trans_ret

                       })

#df_par.to_csv('participants_proc2.csv')

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