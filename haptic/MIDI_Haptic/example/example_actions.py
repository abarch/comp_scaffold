import mido
from mido import Message
from mido import MidiFile
import time

import curses
import datetime

stdscr = curses.initscr()
curses.noecho()
stdscr.nodelay(1) # set getch() non-blocking


# FIXME: this needs to be adapted
midi_interface = 'DEXMO_R MIDI 1'

# abstract in python of the MIDI_HAPTIC_DEFINITION
# define channel of the device here
CHAN = 10
# choosing action on the index here
MHP_ACT_IND = 36
# various action modes
NOTE_E= 4
NOTE_F= 5
NOTE_A= 9

# Send an action to the haptic device over the midi interface from the computer keyboard.
def haptic_action():
    with mido.open_output(midi_interface) as outport:
        while 1:

            key = stdscr.getch()
            if key == ord('f'):
                msg = Message('note_on', channel=CHAN, note=MHP_ACT_IND+NOTE_F, velocity=2)
                outport.send(msg)
                print ('action Flex, velocity 2')
            if key == ord('o'):
                msg = Message('note_off', channel=CHAN, note=MHP_ACT_IND+NOTE_F, velocity=2)
                outport.send(msg)
                print ('stop action flex')
            if key == ord('e'):
                msg = Message('note_on', channel=CHAN, note=MHP_ACT_IND+NOTE_E, velocity=50)
                outport.send(msg)
                print ('action Extension, velocity 50')
            if key == ord('a'):
                msg = Message('note_on', channel=CHAN, note=MHP_ACT_IND+NOTE_A, velocity=20)
                outport.send(msg)
                print ('action impulse inwards, threshold 20 for stopping the impulse')
            if key == ord('q'):
                print ('action impulse outwards, threshold 20 for stopping the impulse')
                msg = Message('note_off', channel=CHAN, note=MHP_ACT_IND+NOTE_A, velocity=20)
                outport.send(msg)

if __name__ == '__main__':
    haptic_action()
    curses.endwin()
