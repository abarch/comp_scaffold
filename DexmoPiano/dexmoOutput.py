import mido
from mido import Message
from mido import MidiFile
import time

import datetime

import noteHandler as nh


# FIXME: this needs to be adapted
global midi_interface, midi_interface_sound
#midi_interface = 'DEXMO_R:DEXMO_R MIDI 1 24:0'
#midi_interface_sound = 'Synth input port (Qsynth1:0)'

# abstract in python of the MIDI_HAPTIC_DEFINITION
# define channel of the device here
CHAN = 10
# choosing action on the index here
MHP_ACT_IND = 48
# various action modes
NOTE_E = 4
NOTE_F = 5
NOTE_A = 9


# set dexmo port
def set_dexmo(port):
    global midi_interface
    midi_interface = port

# set sound port
def set_sound_outport(port):
    global midi_interface_sound
    midi_interface_sound = port

def get_midi_interfaces():
    return mido.get_output_names(), mido.get_input_names()

# Send an action to the haptic device over the midi interface
def haptic_action(char):
    with mido.open_output(midi_interface) as outport:

        if char == 'i':  # inwards dexmo impulse
            msg = Message('note_on', channel=CHAN, note=MHP_ACT_IND + NOTE_F, velocity=50)
            outport.send(msg)
        elif char == 'o':  # outwards dexmo impulse
            # msg = Message('note_off', channel=CHAN, note=MHP_ACT_IND+NOTE_F, velocity=50)
            msg = Message('note_on', channel=CHAN, note=MHP_ACT_IND + NOTE_E, velocity=50)
            outport.send(msg)


# Send an action to the haptic device over the midi interface
def haptic_action2(char, pitch):
    with mido.open_output(midi_interface) as outport:
        if char == 'i':  # inwards dexmo impulse
            msg = Message('note_on', channel=CHAN, note=pitch + NOTE_F, velocity=50)
            outport.send(msg)
        elif char == 'o':  # outwards dexmo impulse
            # msg = Message('note_off', channel=CHAN, note=MHP_ACT_IND+NOTE_F, velocity=50)
            msg = Message('note_on', channel=CHAN, note=pitch + NOTE_E, velocity=50)
            outport.send(msg)


# play demo: sound output of notes and haptic feedback impulse
def play_demo(midiFile, guidanceMode):
    with mido.open_output(midi_interface_sound) as port:
        for msg in MidiFile(midiFile).play():
            port.send(msg)  # sound from piano and metronome track
            if msg.channel == 0:  # haptic feeback for notes in Piano track

                ##____________________HANDLE note_____________________________##
                if (guidanceMode == "At every note"):
                    if msg.type == 'note_on':
                        haptic_action('i')
                    elif msg.type == 'note_off':
                        haptic_action('o')

                ##__________HANDLE note  C-G for different fingers____________##
                if (guidanceMode == "At every note (note C-G)"):
                    if (msg.type == 'note_on') or (msg.type == 'note_off'):
                        if msg.note == 60:
                            finger = 24
                        elif msg.note == 62:
                            finger = 36
                        elif msg.note == 64:
                            finger = 48
                        elif msg.note == 65:
                            finger = 60
                        elif msg.note == 67:
                            finger = 72
                    if msg.type == 'note_on':
                        haptic_action2('i', finger)
                    elif msg.type == 'note_off':
                        haptic_action2('o', finger)


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
                    port.send(msg)  # sound only from metronome track

                if msg.channel == 0:  # haptic feeback for notes in Piano track

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

                    ##__________HANDLE note  C-G for different fingers____________##
                    if (guidanceMode == "At every note (note C-G)"):
                        if (msg.type == 'note_on') or (msg.type == 'note_off'):
                            if msg.note == 60:
                                finger = 24
                            elif msg.note == 62:
                                finger = 36
                            elif msg.note == 64:
                                finger = 48
                            elif msg.note == 65:
                                finger = 60
                            elif msg.note == 67:
                                finger = 72
                        if msg.type == 'note_on':
                            haptic_action2('i', finger)
                        elif msg.type == 'note_off':
                            haptic_action2('o', finger)



if __name__ == '__main__':
    # start_music()
    play_demo()
    # practice_task()
