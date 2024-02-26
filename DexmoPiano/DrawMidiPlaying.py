from midiutil.MidiFile import MIDIFile
import xml.etree.ElementTree as ET
import json
import sys
import pickle
import pathlib
import os
import csv
from collections import namedtuple, defaultdict
from error_calc import functions as errorCalc
import numpy as np
from PIL import Image
from PIL import ImageDraw
import matplotlib.pyplot as plt


cwd = os.getcwd()
print(cwd)
basename = '2022_08_17-12_28_39'
basename = '2022_06_29-14_01_22'
basename = '2023_05_31-11_48_33'
#basename = '2023_05_31-12_37_23'
basename = '2023_06_05-15_06_47'
basename = '2023_06_06-10_13_41'
basename = '2023_06_06-12_04_35'

#  participant 1
# 2023_06_06-10_52_36.xml
# 2023_06_06-11_08_00.xml

#  participant 2
# 2023_06_06-11_26_46.mid
# 2023_06_06-11_41_25.xml

#  participant 3
# 2023_06_06-11_51_44.xml
# 2023_06_06-12_04_35.xml


def analyze_play_trials(basename):
    taskdata_filename = cwd + '\\output\\'+ basename + '-data.task'
    xmlfilename = cwd + '\\output\\'+ basename + '.xml'

    taskdata_filename = cwd + '/output/'+ basename + '-data.task'
    xmlfilename = cwd + '/output/'+ basename + '.xml'


    # read task_data
    with open(taskdata_filename, 'rb') as f:
        task_data_from_file = pickle.load(f)
    print("loaded data: ", task_data_from_file)
    [taskData, taskParameters] = task_data_from_file

    # read xml with Played Notes
    try:
        tree = ET.parse(xmlfilename)
    except FileNotFoundError:
        print("Cannot open", xmlfilename)


    root = tree.getroot()
    trials = root.find("trials")
 #   target = root.find("target_notes")

    NoteInfo = namedtuple("NoteInfo", ["pitch", "velocity", "note_on_time", "note_off_time"])

    order_list = []
    batch_list = []
    target_pitch_list = []
    played_pitch_list = []
    velocity_list = []
    start_time_list = []
    end_time_list = []

    trials = [trials[1], trials[2]]
    batch = 0
    for trial in trials:
        #trial_offset += 60
        PlayedNotes = []
        trial_no = trial.get("trial_no")
        print('trial no: ',trial_no)
        notes = trial.find("notes").text
        notesArray = json.loads(notes)
        # startsongtime = notesArray[0][2]
        if len(notesArray) == 0:  # i.e., it is empty
            continue
        #startsongtime = notesArray[0]['note_on_time']
        note_counter = 0
        for m in notesArray:
            # note = m[0]
            note = m['pitch']
            velocity = m['velocity']
            # starttime = m[2] - startsongtime
            starttime = m['note_on_time'] #- startsongtime
            # endtime = m[3] - startsongtime
            endtime = m['note_off_time'] #- startsongtime
            duration = endtime - starttime
            print(note, velocity, starttime, endtime)

            current_note = NoteInfo(note, velocity, starttime, endtime)
            PlayedNotes.append(current_note)

            order_list.append(note_counter)
            batch_list.append(batch)
            played_pitch_list.append(note)
            velocity_list.append(velocity)
            start_time_list.append(starttime)
            end_time_list.append(endtime)
            note_counter += 1
        print(PlayedNotes)
        batch += 1
    return order_list, batch_list, played_pitch_list, velocity_list, start_time_list, end_time_list
#  participant 1
# 2023_06_06-10_52_36.xml
# 2023_06_06-11_08_00.xml

#  participant 2
# 2023_06_06-11_26_46.mid
# 2023_06_06-11_41_25.xml

#  participant 3
# 2023_06_06-11_51_44.xml
# 2023_06_06-12_04_35.xml

participants = [['par1','I','2023_06_06-10_52_36','2023_06_06-11_08_00' ], \
                ['par2','S','2023_06_06-11_26_46', '2023_06_06-11_41_25'],\
                ['par3','I','2023_06_06-11_51_44', '2023_06_06-12_04_35'],\
                ['par4','S','2023_06_08-13_26_39', '2023_06_08-13_42_00'],\
                ['par5','I','2023_06_11-10_28_48', '2023_06_11-10_41_17'],\
                ['par6','S','2023_06_11-12_46_03', '2023_06_11-12_59_03'],\
                ['par7','I','2023_06_12-12_37_32', '2023_06_12-12_49_37'],\
                ['par8','S','2023_06_12-15_14_20', '2023_06_12-15_29_11'], \
                ['par9','I','2023_06_13-11_31_32', '2023_06_13-11_43_12'], \
                ['par10','S','2023_06_14-12_21_12', '2023_06_14-12_34_08'], \
                ['par11','I','2023_06_14-13_32_03', '2023_06_14-13_49_04'], \
                ['par12','S','2023_06_19-10_36_33', '2023_06_19-10_50_07'], \
                ['par13', 'I', '2023_06_14-15_50_39', '2023_06_14-16_03_42'], \
                ['par14', 'I', '2023_06_19-11_08_54', '2023_06_19-11_22_42'], \
                ['par15', 'S', '2023_06_19-11_36_38', '2023_06_19-11_50_01'], \
                ['par16', 'S', '2023_06_19-12_07_54', '2023_06_19-12_22_22'], \
                ['par17', 'I', '2023_06_19-16_04_10', '2023_06_19-16_19_06'], \
                ['par18', 'S', '2023_06_19-16_33_59', '2023_06_19-16_49_57'], \
                ['par19', 'I', '2023_06_19-17_01_42', '2023_06_19-17_17_49'], \
                ['par20', 'S', '2023_06_21-10_33_08', '2023_06_21-10_49_05'], \
                ['par21', 'I', '2023_06_21-13_00_58', '2023_06_21-13_15_16'], \
                ['par22', 'S', '2023_06_26-14_06_55', '2023_06_26-14_24_38'], \
                ]


test_trials = [['number', 'group', 'order', 'batch', 'played_pitch', 'velocity', 'start_time', 'end_time']]
for participant in participants:

    order_list, batch_list, played_pitch_list, velocity_list, start_time_list, end_time_list = analyze_play_trials(participant[2])
    for k in range(len(order_list)):
        test_trials.append([participant[0],participant[1],order_list[k], batch_list[k], played_pitch_list[k], velocity_list[k], start_time_list[k], end_time_list[k]])


# field names

with open('playing_intervention.csv', 'w') as f:
    # using csv.writer method from CSV package
    write = csv.writer(f)
    write.writerows(test_trials)

