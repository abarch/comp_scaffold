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

def analyze_test(basename):
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
    target = root.find("target_notes")

    NoteInfo = namedtuple("NoteInfo", ["pitch", "velocity", "note_on_time", "note_off_time"])
    errors_table = []

    s = (10950 , len(trials)*100)
    im = Image.new('RGBA', s, (255, 255, 255, 255))
    draw = ImageDraw.Draw(im)
    trial_offset = -50

    #for note in taskData.midi.right:
    #    draw.line(
    #        ((note.note_on_time*150, note.pitch+trial_offset), (note.note_off_time*150, note.pitch+trial_offset)),
    #        fill=(0, 200, 0), width=5)

    TargetNotes = []
    notes = target.find("notes").text
    notesArray = json.loads(notes)
    # startsongtime = notesArray[0][2]
    if len(notesArray) == 0:  # i.e., it is empty
        print("No target notes")
        #startsongtime = notesArray[0]['note_on_time']
    else:
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
            TargetNotes.append(current_note)

    trials = [trials[0]]
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
        for note in PlayedNotes:
            draw.polygon([(note.note_on_time*100, note.pitch+trial_offset),(note.note_off_time*100, note.pitch+trial_offset),(note.note_off_time*100, note.pitch+trial_offset+10),(note.note_on_time*100, note.pitch+trial_offset+10)],fill=(0, 0, 200), width=1, outline=(0,0,0))

    def find_first_after(start_time, end_time):
        for note in PlayedNotes:
            if note.note_on_time > start_time and note.note_on_time < end_time:
                return note.pitch, note.note_on_time, note.velocity
        return None, None, None

    target_notes = taskData.midi.right[3::4]
    played_trials = 0
    success_notes = 0
    total_response_time = 0
    total_velocity = 0
    for k in range(len(target_notes)):
        target_pitch = target_notes[k].pitch
        target_start_time = target_notes[k].note_on_time
        target_end_time = target_notes[k].note_on_time + 8.0
        played_pitch, played_time, played_velocity = find_first_after(target_start_time, target_end_time)
        print('target pitch:',target_pitch,' target_start_time: ',target_start_time, ' played_pitch: ', played_pitch, ' played_time: ', played_time)
        if target_pitch == played_pitch:
            success_notes += 1.0
        if played_pitch != None:
            total_response_time += played_time - target_start_time;
            total_velocity += played_velocity
            played_trials +=1


    print ('correct_notes: ',success_notes, 'percent: ', success_notes/(len(target_notes)-1))


    #plt.imshow(np.asarray(im), origin = 'lower')
    #plt.show()
    return success_notes, success_notes/(len(target_notes)-1), total_response_time/played_trials, total_velocity/played_trials, played_trials

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
                ['par4','S','2023_06_08-13_26_39', '2023_06_08-13_42_00']]


tests = [['number','group','perc_succ_pre', 'perc_succ_post', 'avg_RT_pre', 'avg_RT_post','avg_velocity_pre', 'avg_velocity_post']]
for participant in participants:
    correct_notes1, perc1, avg_RT1, avg_velocity1, played_trials1 = analyze_test(participant[2])
    correct_notes2, perc2, avg_RT2, avg_velocity2, played_trials2 = analyze_test(participant[3])
    print(participant[0], perc1, perc2)
    tests.append([participant[0],participant[1], perc1, perc2,avg_RT1,avg_RT2,avg_velocity1,avg_velocity2])

print(tests)