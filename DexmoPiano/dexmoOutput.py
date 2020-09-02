import mido
from mido import Message
from mido import MidiFile
import time
import datetime

import noteHandler as nh

# FIXME: this needs to be adapted
global midi_interface, midi_interface_sound, CHAN, actualNote, metronome
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

metronome = True


# set dexmo port
def set_dexmo(port):
    global midi_interface
    midi_interface = port

# set sound port
def set_sound_outport(port):
    global midi_interface_sound
    midi_interface_sound = port

# set Channel for dexmo
def set_channel(channel):
    global CHAN
    CHAN = channel

# should metronome sound be played
def set_metronome():
    global metronome
    metronome = not metronome

def get_midi_interfaces():
    return mido.get_output_names(), mido.get_input_names()


def stop_haptic_actions(outport):
    global actualNote
    if (actualNote != None):
        msg = Message('note_off', channel=CHAN, note=actualNote + NOTE_E, velocity=50)
        #print(msg)
        outport.send(msg)

# TODO delete? old haptic dexmo messages
# Send an action to the haptic device over the midi interface
def haptic_action(char, pitch, outport):
    global actualNote
    if pitch == None: #if pitch so finger isnt choosen, use index finger
        pitch =  MHP_ACT_IND

    if char == 'i':  # inwards dexmo impulse, stop last outwards impulse
        stop_haptic_actions(outport)
        msg = Message('note_on', channel=CHAN, note=pitch + NOTE_F, velocity=50)
        # print(msg)
        outport.send(msg)
    elif char == 'o':  # outwards dexmo impulse, stop inwards impulse
        msg = Message('note_off', channel=CHAN, note=actualNote+NOTE_F, velocity=50)
        # print(msg)
        outport.send(msg)
        msg = Message('note_on', channel=CHAN, note=pitch + NOTE_E, velocity=50)
        # print(msg)
        outport.send(msg)
    actualNote = pitch

#TODO add outwards guidance after note off, stop this befor next note with note_off
def dexmo_action(msg, outport):
    outport.send(msg)
    #if (msg.type == 'note_on'):
    #    outport.send(msg)
    #elif (msg.type == 'note_off'):
    #    outport.send(msg)


# play demo: sound output of notes and haptic feedback guidance
def play_demo(midiFile, guidanceMode):
    global actualNote
    actualNote = None
    if (midi_interface != "None"):
        dexmoPort = mido.open_output(midi_interface)
    with mido.open_output(midi_interface_sound) as soundPort:
        for msg in MidiFile(midiFile).play():
            # sound from piano and metronome track,channel 9 is metronome, piano is 0
            if metronome == True:
                if msg.channel == 0 or msg.channel == 9:
                    soundPort.send(msg)
            elif msg.channel == 0 : # only piano sound
                soundPort.send(msg)

            # haptic feedback on dexmo for right (channel 10) and left hand (channel 11)
            if msg.channel != 0 and msg.channel != 9:
                if guidanceMode != "None":
                    if msg.type == 'note_on':
                        dexmo_action(msg=msg, outport=dexmoPort)
                    elif msg.type == 'note_off':
                        dexmo_action(msg=msg, outport=dexmoPort)

    #if (midi_interface != "None"): # stop outwards guidance
    #    stop_haptic_actions(dexmoPort)
        dexmoPort.close()


# only haptic feedback guidance
def practice_task(midiFile, noteInfoTemp, noteInfoList, guidanceMode):
    global actualNote
    actualNote = None
    if (midi_interface != "None"):
        dexmoPort = mido.open_output(midi_interface)
    with mido.open_output(midi_interface_sound) as soundPort:
        noteCounter = 1

        # set start time
        nh.initTime()

        for msg in MidiFile(midiFile):
            if not msg.is_meta:
                # do not play all notes at once
                time.sleep(msg.time)

                if msg.channel == 9 and metronome == True:
                    soundPort.send(msg)  # sound only from metronome track

                if msg.channel == 0:  # haptic feeback for notes in Piano track

                    ##____________________HANDLE note_____________________________##
                    if (msg.type == 'note_on') or (msg.type == 'note_off'):
                        # handle note
                        noteInfo = nh.handleNote(msg.type, msg.note, msg.velocity, noteInfoTemp, noteInfoList)

                        if type(noteInfo) == list:
                            print("TARGET:", noteCounter, "\t", noteInfo)
                            noteCounter += 1

                if msg.channel != 0 and msg.channel != 9:
                    if guidanceMode != "None":
                        if msg.type == 'note_on':
                            dexmo_action(msg=msg, outport=dexmoPort)
                        elif msg.type == 'note_off':
                            dexmo_action(msg=msg, outport=dexmoPort)
                    ##____________________HANDLE note_____________________________##
                    #if (guidanceMode == "At every note"):
                    #    if msg.type == 'note_on':
                    #        haptic_action(char='i',pitch=None, outport=dexmoPort)
                    #    elif msg.type == 'note_off':
                    #        haptic_action(char='o',pitch=None, outport=dexmoPort)

                    ##__________HANDLE note  C-G for different fingers____________##
                    #if (guidanceMode == "At every note (note C-G)"):
                    #    if (msg.type == 'note_on') or (msg.type == 'note_off'):
                    #        if msg.note == 60:
                    #            finger = 24
                    #        elif msg.note == 62:
                    #            finger = 36
                    #        elif msg.note == 64:
                    #            finger = 48
                    #        elif msg.note == 65:
                    #            finger = 60
                    #        elif msg.note == 67:
                    #            finger = 72
                    #    if msg.type == 'note_on':
                    #        haptic_action(char='i', pitch=finger, outport=dexmoPort)
                    #    elif msg.type == 'note_off':
                    #        haptic_action(char='o', pitch=finger, outport=dexmoPort)
#    if (midi_interface != "None"):
#        stop_haptic_actions(dexmoPort)
        dexmoPort.close()



if __name__ == '__main__':
    # start_music()
    play_demo()
    # practice_task()
