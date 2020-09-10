import mido
from mido import Message
from mido import MidiFile
import time
import datetime

import noteHandler as nh

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
NOTE_A = 9 # note_off outwards impulse

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

## TODO: OLD, Delete?
#stop guidance outwards when new note starts or after track is finished
#def stop_guidance_out(outport):
#    global actualMsgRight, actualMsgLeft
#    if actualMsgRight is not None:
#        msg = Message('note_off', channel=actualMsgRight.channel, note=actualMsgRight.note -1, velocity=actualMsgRight.velocity)
#        outport.send(msg)
#        actualMsgRight = None
#    if actualMsgLeft is not None:
#        msg = Message('note_off', channel=actualMsgLeft.channel, note=actualMsgLeft.note -1, velocity=actualMsgLeft.velocity)
#        outport.send(msg)
#        actualMsgLeft = None

# stop forces on all fingers on dexmo motors
def stop_all_forces(outport):
    x = range(10, 12)
    fingerlist = [28, 40, 53, 64, 76]
    for n in x:
        for finger in fingerlist:
            msg = Message('note_off', channel=n, note=finger, velocity=100)
            outport.send(msg)


# impulse outwards after note is finished
def impulse_outwards(msg, outport):
    #global actualMsgRight, actualMsgLeft
    impulsemsg = Message('note_off', channel=msg.channel, note=msg.note +4, velocity=20)
    outport.send(impulsemsg)
    #if msg.channel == 10:
    #    actualMsgRight = msg
    #    msg = Message('note_on', channel=actualMsgRight.channel, note=actualMsgRight.note -1, velocity=actualMsgRight.velocity)
    #    outport.send(msg)
    #else:
    #    actualMsgLeft = msg
    #    msg = Message('note_on', channel=actualMsgLeft.channel, note=actualMsgLeft.note -1, velocity=actualMsgLeft.velocity)
    #    outport.send(msg)


# send midi message to dexmo for finger guidance
def dexmo_action(msg, outport):
    if (msg.type == 'note_on'):
        #stop_guidance_out(outport) # stop last guidance out before next note
        outport.send(msg)
    elif (msg.type == 'note_off'):
        outport.send(msg)
        impulse_outwards(msg, outport)


# play demo: sound output of notes and haptic feedback guidance
def play_demo(midiFile, guidanceMode):
    #global actualMsgRight, actualMsgLeft
    #actualMsgRight = None
    #actualMsgLeft = None
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

    if (midi_interface != "None"): # stop all forces on dexmo
        stop_all_forces(dexmoPort)
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
        stop_all_forces(dexmoPort)
        dexmoPort.close()



if __name__ == '__main__':
    # start_music()
    play_demo()
    # practice_task()
