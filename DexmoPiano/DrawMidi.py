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

s = (1950 , len(trials)*100)
im = Image.new('RGBA', s, (255, 255, 255, 255))
draw = ImageDraw.Draw(im)
trial_offset = -50

#for note in taskData.midi.right:
#    draw.line(
#        ((note.note_on_time*150, note.pitch+trial_offset), (note.note_off_time*150, note.pitch+trial_offset)),
#        fill=(0, 200, 0), width=5)

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
plt.imshow(np.asarray(im), origin = 'lower')
plt.show()