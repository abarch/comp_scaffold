from midiutil.MidiFile import MIDIFile
from music21 import converter

import copy
import os
#import random
import mido
import settings
import shutil

import pianoplayer_interface
from task_generation.note_range_per_hand import NoteRangePerHand  # ,get_pitchlist

temp_mido_file = mido.MidiFile('./output/20220202-151830.mid')
temp_mido_file.tracks[0][1].tempo = 504201*2
#write_midi('./output/20220202-151830-double.mid', temp_mido_file)
with open('./output/20220202-151830-double.mid', 'wb') as outf:
    copy.deepcopy(temp_mido_file).writeFile(outf)
