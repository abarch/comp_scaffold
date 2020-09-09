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

# should metronome sound be played
def set_metronome():
    global metronome
    metronome = not metronome

def get_midi_interfaces():
    return mido.get_output_names(), mido.get_input_names()

# stop guidance outwards when new note starts or after track is finished
def stop_guidance_out(outport):
    global actualMsgRight, actualMsgLeft
    if actualMsgRight is not None:
        msg = Message('note_off', channel=actualMsgRight.channel, note=actualMsgRight.note -1, velocity=actualMsgRight.velocity)
        outport.send(msg)
        #print(msg)
        actualMsgRight = None

    if actualMsgLeft is not None:
        msg = Message('note_off', channel=actualMsgLeft.channel, note=actualMsgLeft.note -1, velocity=actualMsgLeft.velocity)
        outport.send(msg)
        #print(msg)
        actualMsgLeft = None


# guidance outwards after note is finished
def guidance_outwards(msg, outport):
    global actualMsgRight, actualMsgLeft
    if msg.channel == 10:
        actualMsgRight = msg
        msg = Message('note_on', channel=actualMsgRight.channel, note=actualMsgRight.note -1, velocity=actualMsgRight.velocity)
        outport.send(msg)
        #print(msg)
    else:
        actualMsgLeft = msg
        msg = Message('note_on', channel=actualMsgLeft.channel, note=actualMsgLeft.note -1, velocity=actualMsgLeft.velocity)
        outport.send(msg)
        #print(msg)


# send midi message to dexmo for finger guidance
def dexmo_action(msg, outport):
    #outport.send(msg)
    if (msg.type == 'note_on'):
        stop_guidance_out(outport) # stop last guidance out before next note
        outport.send(msg)
        #if msg.channel == 11:
        #print(msg)
    elif (msg.type == 'note_off'):
        outport.send(msg)
        #msg.channel == 11:
        #print(msg)
        guidance_outwards(msg, outport) # start guidance outward after note is finished


# play demo: sound output of notes and haptic feedback guidance
def play_demo(midiFile, guidanceMode):
    global actualMsgRight, actualMsgLeft
    #actualMsg = None
    actualMsgRight = None
    actualMsgLeft = None
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

    if (midi_interface != "None"): # stop outwards guidance
        stop_guidance_out(dexmoPort)
        dexmoPort.close()


# only haptic feedback guidance
def practice_task(midiFile, noteInfoTemp, noteInfoList, guidanceMode):
    global actualMsgRight, actualMsgLeft
    #actualMsg = None
    actualMsgRight = None
    actualMsgLeft = None
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
                # haptic feedback on dexmo for right (channel 10) and left hand (channel 11)
                if msg.channel != 0 and msg.channel != 9:
                    if guidanceMode != "None":
                        if msg.type == 'note_on':
                            dexmo_action(msg=msg, outport=dexmoPort)
                        elif msg.type == 'note_off':
                            dexmo_action(msg=msg, outport=dexmoPort)

    if (midi_interface != "None"):
        stop_guidance_out(dexmoPort)
        dexmoPort.close()



if __name__ == '__main__':
    # start_music()
    play_demo()
    # practice_task()
