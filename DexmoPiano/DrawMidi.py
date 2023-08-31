from midiutil.MidiFile import MIDIFile
import xml.etree.ElementTree as ET
import json
import sys
import pickle
import pathlib
import os
from collections import namedtuple, defaultdict
from error_calc import functions as errorCalc
import numpy as np
from PIL import Image
from PIL import ImageDraw
import matplotlib.pyplot as plt
import pandas as pd



cwd = os.getcwd()
print(cwd)
basename = '2022_08_17-12_28_39'
basename = '2022_06_29-14_01_22'
basename = '2022_08_17-19_12_37'
basename = '2022_08_17-12_47_07'
basename = '2022_08_17-19_12_37'
basename = '2022_08_17-16_20_41'
basename = '2022_11_03-10_32_30'
basename = '2022_11_03-11_00_07'
basename = '2022_11_03-11_06_14'
basename = '2022_11_03-10_39_18'
basename = '2022_10_26-14_43_34'
basename = '2022_10_26-14_23_17'
basename = '2022_10_26-14_09_11'

def drawTrials(basename, title):

    taskdata_filename = cwd + '\\output\\'+ basename + '-data.task'
    xmlfilename = cwd + '\\output\\'+ basename + '.xml'

    taskdata_filename = cwd + '/output/'+ basename + '-data.task'
    xmlfilename = cwd + '/output/'+ basename + '.xml'

    # read task_data
    with open(taskdata_filename, 'rb') as f:
        task_data_from_file = pickle.load(f)
    print("loaded data: ", task_data_from_file)
    [taskData, taskParameters] = task_data_from_file

    # rescale notes according to a different tempo (due to error in saving in the right tempo)
    # current_tempo = 322.0
    # new_tempo = 248.0
    # for k in range(len(taskData.midi.right)):
    #     note = taskData.midi.right[k]._replace(note_on_time=taskData.midi.right[k].note_on_time * current_tempo / new_tempo)
    #     note = note._replace(note_off_time=note.note_off_time * current_tempo / new_tempo)
    #     taskData.midi.right[k] = note

    # read xml with Played Notes
    try:
        tree = ET.parse(xmlfilename)
    except FileNotFoundError:
        print("Cannot open", xmlfilename)


    root = tree.getroot()
    trials = root.find("trials")
    target = root.find("target_notes")

    target_notes = target.find("notes").text
    target_notes_array = json.loads(target_notes)

    NoteInfo = namedtuple("NoteInfo", ["pitch", "velocity", "note_on_time", "note_off_time"])
    errors_table = []

    TargetNotes = []
    #if len(target_notes_array) != 0:  # i.e., it is empty

    max_endtime = 0

    # startsongtime = notesArray[0]['note_on_time']
    for m in target_notes_array:
        # note = m[0]
        note = m['pitch']
        velocity = m['velocity']
        # starttime = m[2] - startsongtime
        starttime = m['note_on_time']  # - startsongtime
        # endtime = m[3] - startsongtime
        endtime = m['note_off_time']  # - startsongtime
        max_endtime = max(max_endtime, endtime)
        duration = endtime - starttime
        print(note, velocity, starttime, endtime)

        current_note = NoteInfo(note, velocity, starttime, endtime)
        TargetNotes.append(current_note)
    print("Target Notes:", TargetNotes)

    trial_offset = -50

    #for note in taskData.midi.right:
    #    draw.line(
    #        ((note.note_on_time*150, note.pitch+trial_offset), (note.note_off_time*150, note.pitch+trial_offset)),
    #        fill=(0, 200, 0), width=5)
    #max_endtime = 0

    max_endtime = max(max_endtime, taskData.midi.right[-1].note_off_time)
    print(max_endtime)

    for trial in trials:
        trial_no = trial.get("trial_no")
        notes = trial.find("notes").text
        notesArray = json.loads(notes)
        if len(notesArray) == 0:  # i.e., it is empty
            continue
        for m in notesArray:
            endtime = m['note_off_time'] #- startsongtime
            max_endtime = max(max_endtime, endtime)


    s = (int(max_endtime * 100) + 10, len(trials) * 100)
    im = Image.new('RGBA', s, (255, 255, 255, 255))
    draw = ImageDraw.Draw(im)

    for trial in trials:
        trial_offset += 60
        PlayedNotes = []
        trial_no = trial.get("trial_no")
        print('trial no: ',trial_no)
        notes = trial.find("notes").text
        notesArray = json.loads(notes)
        # startsongtime = notesArray[0][2]
        if len(notesArray) == 0:  # i.e., it is empty
            continue
        #startsongtime = notesArray[0]['note_on_time']
        for m in notesArray:
            # note = m[0]
            note = m['pitch']
            velocity = m['velocity']
            # starttime = m[2] - startsongtime
            starttime = m['note_on_time'] #- startsongtime
            # endtime = m[3] - startsongtime
            endtime = m['note_off_time'] #- startsongtime
            max_endtime = max(max_endtime, endtime)
            duration = endtime - starttime
            print(note, velocity, starttime, endtime)

            current_note = NoteInfo(note, velocity, starttime, endtime)
            PlayedNotes.append(current_note)
        print(PlayedNotes)

        for note in taskData.midi.right:
            draw.polygon([(note.note_on_time * 100, note.pitch + trial_offset-1),
                          (note.note_off_time * 100, note.pitch + trial_offset-1),
                          (note.note_off_time * 100, note.pitch + trial_offset + 15),
                          (note.note_on_time * 100, note.pitch + trial_offset + 15)], fill=(0, 200, 0), width=1,
                         outline=(255, 255, 255))
            print(note.pitch, note.note_on_time, note.note_off_time, 60.0/(note.note_off_time- note.note_on_time))
        for note in PlayedNotes:
            draw.polygon([(note.note_on_time*100, note.pitch+trial_offset),(note.note_off_time*100, note.pitch+trial_offset),(note.note_off_time*100, note.pitch+trial_offset+10),(note.note_on_time*100, note.pitch+trial_offset+10)],fill=(0, 0, 200), width=1, outline=(0,0,0))
     #   for note in TargetNotes:
     #       target_offset = -16
     #       draw.polygon([(note.note_on_time * 100, note.pitch + trial_offset+target_offset),
     #                     (note.note_off_time * 100, note.pitch + trial_offset+target_offset),
     #                     (note.note_off_time * 100, note.pitch + trial_offset + 10+target_offset),
     #                     (note.note_on_time * 100, note.pitch + trial_offset + 10+target_offset)], fill=(200, 100, 0), width=1,
     #                    outline=(0, 0, 0))

    plt.imshow(np.asarray(im), origin = 'lower')
    plt.title(title + ' ' + basename)

def drawParticipant(list_task_num):
    df = pd.read_csv('./stats/all_participants.csv')
    df = df[(df.user_id == list_task_num[4])]
    df1 = df[(df.task_number == list_task_num[0][0])]
    #basename_ext = df1['saved_filename'].values[0]
    #basename = os.path.splitext(basename_ext)[0]
#    basename = os.path.splitext(df1['saved_filename'].values[0])[0] # use two above lines together

    task_num = list_task_num[1][0][0]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'prac 1 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][0][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'test 1 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[2][0]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'ret 1 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'trans 2 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[2][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'ret 2 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][2][0]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'prac 3 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][2][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'test 3 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[2][2]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'ret 3 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][3][0]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'prac 4 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][3][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'test 4 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[2][3]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'ret 4 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][4][0]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'prac 5 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][4][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'test 5 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[2][4]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'ret 5 '+'task:'+ str(task_num))
    plt.figure()

def drawParticipantChrono(list_task_num):
    df = pd.read_csv('./stats/all_participants.csv')
    df = df[(df.user_id == list_task_num[4])]
    df1 = df[(df.task_number == list_task_num[0][0])]
    #basename_ext = df1['saved_filename'].values[0]
    #basename = os.path.splitext(basename_ext)[0]
#    basename = os.path.splitext(df1['saved_filename'].values[0])[0] # use two above lines together

    task_num = list_task_num[0][0]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'calib 1 ' + 'task:' + str(task_num))
    plt.figure()

    task_num = list_task_num[0][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'calib 2 ' + 'task:' + str(task_num))
    plt.figure()

    task_num = list_task_num[0][2]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'calib 3 ' + 'task:' + str(task_num))
    plt.figure()


    task_num = list_task_num[1][0][0]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'prac 1 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][0][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'test 1 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'trans 2 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][2][0]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'prac 3 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][2][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'test 3 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][3][0]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'prac 4 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][3][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'test 4 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][4][0]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'prac 5 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[1][4][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'test 5 '+'task:'+ str(task_num))
    plt.figure()

    task_num = list_task_num[2][0]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'ret 1 ' + 'task:' + str(task_num))
    plt.figure()

    task_num = list_task_num[2][1]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'ret 2 ' + 'task:' + str(task_num))
    plt.figure()

    task_num = list_task_num[2][2]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'ret 3 ' + 'task:' + str(task_num))
    plt.figure()

    task_num = list_task_num[2][3]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'ret 4 ' + 'task:' + str(task_num))
    plt.figure()

    task_num = list_task_num[2][4]
    df1 = df[(df.task_number == task_num)]
    basename = os.path.splitext(df1['saved_filename'].values[0])[0]
    drawTrials(basename, 'ret 5 '+'task:'+ str(task_num))
    plt.figure()


all_participants = [
[[6,7,8],[[9,10],11,[12,13],[14,15],[16,17]],[18,19,20,21,22],'par. 1','1', [0,2,3,4]],
[[3,4,5],[[6,7],8,[9,11],[12,13],[14,15]],[18,19,20,21,22],'par. 2','2', [4,0,2,3]],
[[3,4,5],[[6,7],8,[9,11],[12,12],[13,13]],[14,15,16,17,18],'par. 3','3', [3,4,0,2]], #last test was missing
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
[[4,5,6],[[2,3],4,[6,7],[8,9],[10,11]],[13,14,15,16,17],'par. 29','29', [4,0,2,3]]
]

tasks_num = [[2,3,4],[[6,7],8,[9,10],[11,12],[14,15]],[17,20,21,22,24],'par. 8','8']
tasks_num = [[4,5,6],[[8,9],11,[13,14],[15,17],[18,19]],[21,22,24,25,26],'par. 4','4']
tasks_num = [[4,5,7],[[8,8],9,[10,11],[12,12],[13,14]],[15,16,19,22,23],'par. 7','7']
tasks_num = [[4,5,6],[[8,9],11,[13,14],[15,17],[18,19]],[21,22,24,25,26],'par. 4','4']
tasks_num = [[3,4,5],[[6,7],8,[9,11],[12,13],[14,15]],[18,19,20,21,22],'par. 2','2']
tasks_num = [[6,7,8],[[9,10],11,[12,13],[14,15],[16,17]],[18,19,20,21,22],'par. 1','1']

tasks_num = all_participants[5]
drawParticipantChrono(tasks_num)

#drawTrials('2022_11_21-07_07_26', 'bug_test')
#plt.figure()

#tasks_num = [[5,6,7],[[8,9],11,[12,13],[14,15],[16,19]],[22,[24 25]!!,26,28,29],'par. 12','12']
#tasks_num = [[5,6,7],[[8,9],11,[12,13],[14,15],[16,19]],[22,24,26,28,29],'par. 12','12']
#drawParticipant('12', tasks_num)

#tasks_num = [[4,5,6],[[7,8],9,[10,11],[12,13],[14,15]],[18,20,22,24,26],'par. 5','5']
#drawParticipant('5', tasks_num)

#
# drawTrials('2022_10_26-14_09_11', 'prac 1')
# plt.figure()
# drawTrials('2022_10_26-14_11_30', 'test 1')
# plt.figure()
# drawTrials('2022_10_26-14_34_52', 'ret 1')
# plt.figure()
#
# drawTrials('2022_10_26-14_13_51', 'prac 2')
# plt.figure()
# drawTrials('2022_10_26-14_37_41', 'ret 2')
# plt.figure()
#
# drawTrials('2022_10_26-14_16_29', 'prac 3')
# plt.figure()
# drawTrials('2022_10_26-14_18_32', 'test 3')
# plt.figure()
# drawTrials('2022_10_26-14_39_19', 'ret 3')
# plt.figure()
#
# drawTrials('2022_10_26-14_21_00', 'prac 4')
# plt.figure()
# drawTrials('2022_10_26-14_23_17', 'test 4')
# plt.figure()
# drawTrials('2022_10_26-14_41_14', 'ret 4')
# plt.figure()
#
# drawTrials('2022_10_26-14_25_30', 'prac 5')
# plt.figure()
# drawTrials('2022_10_26-14_28_14', 'test 5')
# plt.figure()
# drawTrials('2022_10_26-14_43_34', 'ret 5')

plt.show()