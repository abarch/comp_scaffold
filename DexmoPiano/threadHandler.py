# run midi player and keyboard input as separate threads
# kill by Ctrl-C

from threading import Thread
import sys

###remove
import time

import midiPlayer
import DexmoOutput
import midiInput
import errorCalc


def startThreads(midiFileLocation, guidance):
	# CONSTANTS
	MAX_NOTE = 128

	# arrays for target and actual note times
	actualTimes = []
	targetTimes = []

	# initialize list of tuples for note on/off times
	# index = note: [t_on, t_off, velocity]
	###TODO: documentation (temporary etc.)
	actualTemp = [[-1, -1, -1]] * MAX_NOTE
	targetTemp = [[-1, -1, -1]] * MAX_NOTE



	# MIDI PLAYER THREAD

	#midiFile = './testFiles/output.mid'
	#midiFile = './testFiles/easy.mid'
	#outPort = 'FLUID Synth (5011):Synth input port (5011:0) 130:0'

	# initialize MIDI file player thread
	#playerThread = Thread(target=midiPlayer.playMidi,args=(midiFile, outPort, targetTemp, targetTimes))

	playerThread = Thread(target=DexmoOutput.practice_task,
						  args=(midiFileLocation, targetTemp, targetTimes, guidance))

	#playerThread = Thread(target = DexmoOutput.practice_task(midiFileLocation,
	#														 targetTemp,
	#														 targetTimes,
	#														 guidance))

	playerThread.start()




	# KEYBOARD MIDI INPUT THREAD

	#inPort = 'Q25 MIDI 1'

	inPort = 'VMPK Output:out 131:0'

	# initialize keyboard MIDI input thread
	inputThread = Thread(target=midiInput.getMidiInput,
						 args=(inPort, actualTemp, actualTimes))

	# set MIDI input thread as daemon is killed on main termination)
	# necessary as the thread is blocking for MIDI input data
	inputThread.daemon = True

	inputThread.start()


	### remove
	# for i in range(10):
	# 	print(i)
	# 	time.sleep(1)



	# wait for MIDI player thread to terminate
	playerThread.join()


	###TODO: remove/change
	# print results
	print("\n\n--- NOTES ---")
	print("\nTarget notes:", targetTimes)
	print("\nActual notes:", actualTimes)



	# COMPUTE ERROR (naive example)

	timeSums, errorDiff = errorCalc.computeError(targetTimes, actualTimes)
	print("\n\n--- ERRORS ---")
	print("\nTARGET TIME:", timeSums[0])
	print("\nACTUAl TIME:", timeSums[1])
	print("\nDIFFERENCE: ", errorDiff)



	# inputThread will die on main termination
	#sys.exit()
