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



cwd = os.getcwd()
print(cwd)
basename = '2022_08_17-12_15_57'
basename = '2022_08_17-12_28_39'
basename = '2022_08_17-12_38_38'
basename = '2022_08_17-12_43_05'
basename = '2022_08_17-12_47_07'
basename = '2022_08_17-12_59_30'
basename = '2022_08_17-14_33_09'
basename = '2022_08_17-14_51_42'
basename = '2022_08_17-15_09_19'
basename = '2022_08_17-16_08_18'
basename = '2022_08_17-16_42_04'
basename = '2022_08_17-12_47_07'
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

NoteInfo = namedtuple("NoteInfo", ["pitch", "velocity", "note_on_time", "note_off_time"])
errors_table = []

for trial in trials:
    PlayedNotes = []
    trial_no = trial.get("trial_no")
    print('trial no: ',trial_no)
    timestamp = trial.get("timestamp")
    print('timestamp: ', timestamp)
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
    output_note_list, errorVec, errorVecLeft, errorVecRight = \
        errorCalc.computeErrorEvo(taskData, PlayedNotes,
                                  openface_data=None,
                                  inject_explanation=True,
                                  plot=False)
    print("task data", taskData.__dict__)
    print("\n\n--- ERRORS ---")
    print("\nNOTE_ERRORS:")
    import shutil

    cwidth = shutil.get_terminal_size().columns

    # print("NOTES".center(cwidth, "+"))
    note_errorString = []
    for n in output_note_list:
        print(n.err_string())
        note_errorString.append(n.err_string(use_colors=False))
    print("\nSUMMED ERROR: ", errorVec)

    print("ERROR LEFT: ", errorVecLeft)
    print("ERROR RIGHT:", errorVecRight)
    #print(errorVec, errorVecLeft, errorVecRight)
    errors_table.append([trial_no, timestamp, errorVecRight.pitch, errorVecRight.note_hold_time, errorVecRight.timing, errorVecRight.n_missing_notes, errorVecRight.n_extra_notes,errorVecRight.pitch + errorVecRight.timing + errorVecRight.n_missing_notes + errorVecRight.n_extra_notes])

for k in range(len(errors_table)):
    print(errors_table[k],"\n")

error_file = f"../stats/{basename}_error_fix.csv"
f = open(error_file,'a')
writer = csv.writer(f)
writer.writerow(['trial_no', 'timestamp', 'pitch', 'note_hold_time', 'timing', 'n_missing_notes', 'n_extra_notes', 'Summed'])
for k in range(len(errors_table)):
    writer.writerow(errors_table[k])
f.close()