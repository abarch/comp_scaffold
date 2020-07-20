import mido
from mido import Message
from mido import MidiFile
import time

import datetime

import noteHandler as nh


# FIXME: this needs to be adapted
global midi_interface
midi_interface = 'DEXMO_R:DEXMO_R MIDI 1 24:0'
midi_interface_sound = 'Synth input port (Qsynth1:0)'

# abstract in python of the MIDI_HAPTIC_DEFINITION
# define channel of the device here
CHAN = 9
# choosing action on the index here
MHP_ACT_IND = 36
# various action modes
NOTE_E= 4
NOTE_F= 5
NOTE_A= 9


# check if DEXMO is plugged in and set right interface port
def check_Dexmo():
    global midi_interface
    outportNames = []
    outportNames = mido.get_output_names()
    matching = [s for s in outportNames if "DEXMO" in s]
    if matching:
        midi_interface = matching[0]
        return True
    else: return False

# Send an action to the haptic device over the midi interface
def haptic_action(char):
    with mido.open_output(midi_interface) as outport:

        if char == 'i': # inwards dexmo impulse
            msg = Message('note_on', channel=CHAN, note=MHP_ACT_IND+NOTE_F, velocity=50)
            outport.send(msg)
        elif char == 'o': # outwards dexmo impulse
            #msg = Message('note_off', channel=CHAN, note=MHP_ACT_IND+NOTE_F, velocity=50)
            msg = Message('note_on', channel=CHAN, note=MHP_ACT_IND+NOTE_E, velocity=50)
            outport.send(msg)

# play demo: sound output of notes and haptic feedback impulse
def play_demo(midiFile, guidanceMode):
    with mido.open_output(midi_interface_sound) as port:
        for msg in MidiFile(midiFile).play():
            port.send(msg)       # sound from piano and metronome track
            if msg.channel == 0: # haptic feeback for notes in Piano track
                if (guidanceMode != "None"):
                    if msg.type == 'note_on':
                        haptic_action('i')
                    elif msg.type == 'note_off':
                        haptic_action('o')

# only haptic feedback impulse
def practice_task(midiFile, noteInfoTemp, noteInfoList, guidanceMode):
    with mido.open_output(midi_interface_sound) as port:
        noteCounter = 1

        # set start time
        nh.initTime()

        for msg in MidiFile(midiFile):
            if not msg.is_meta:
    			# do not play all notes at once
                time.sleep(msg.time)

                if msg.channel == 9:
                    port.send(msg)      # sound only from metronome track

                if msg.channel == 0:    # haptic feeback for notes in Piano track

                ##____________________HANDLE note_____________________________##
                    if (msg.type == 'note_on') or (msg.type == 'note_off'):
    					# handle note
                        noteInfo = nh.handleNote(msg.type, msg.note, msg.velocity, noteInfoTemp, noteInfoList)

                        if type(noteInfo) == list:
                            print("TARGET:", noteCounter, "\t", noteInfo)
                            noteCounter += 1
                ##____________________HANDLE note_____________________________##
                    if (guidanceMode == "At every note"):
                        if msg.type == 'note_on':
                            haptic_action('i')
                        elif msg.type == 'note_off':
                            haptic_action('o')

if __name__ == '__main__':
    #start_music()
    play_demo()
    # practice_task()
