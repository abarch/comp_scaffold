# run midi player and keyboard input as separate threads
# kill by Ctrl-C

from threading import Thread

import midiPlayer
import midiInput


# MIDI PLAYER THREAD

midiFile = '../midiGenerator/output.mid'
outPort = 'Synth input port (qsynth:0)'

# initialize midi file player thread
playerThread = Thread(target=midiPlayer.playMidi, args=(midiFile, outPort))

###TODO: remove?
#playerThread.daemon = True

###TODO: join thread somehow/somewhere?
playerThread.start()




# KEYBOARD MIDI INPUT THREAD

inPort = 'Q25 MIDI 1'

# initialize midi file player thread
inputThread = Thread(target=midiInput.getMidiInput, args=(inPort,))

###TODO: join thread somehow/somewhere?
inputThread.start()

