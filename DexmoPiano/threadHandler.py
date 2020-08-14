# run midi player and keyboard input as separate threads
# kill by Ctrl-C

from threading import Thread

import dexmoOutput
from midiInput import MidiInputThread
import errorCalc


# GLOBAL CONSTANTS
MAX_NOTE = 128


global inPort
#inPort = 'Q25 MIDI 1'
#inPort = 'VMPK Output:out'

# set inport from GUI
def set_inport(port):
	global inPort
	inPort = port

# reset global arrays (target times/temp)
def resetArrays():
	global targetTemp, targetTimes

	print("\nRESET!!!\n")

	# arrays for target and actual note times
	targetTimes = []

	# initialize list of tuples for note on/off times
	# index = note: [t_on, t_off, velocity]
	###TODO: documentation (temporary etc.)
	targetTemp = [[-1, -1, -1]] * MAX_NOTE



# initialize keyboard input thread (avoid multiple instances)
def initInputThread():
	global inputThread


	inputThread = MidiInputThread(inPort, MAX_NOTE)

	# set MIDI input thread as daemon is killed on main termination)
	# necessary as the thread is blocking for MIDI input data
	inputThread.daemon = True

	inputThread.start()



def startThreads(midiFileLocation, guidance):
	global targetTemp, targetTimes, inputThread

	###TODO: change?
	resetArrays()
	inputThread.resetArrays()

	# MIDI PLAYER THREAD

	#outPort = 'FLUID Synth (5011):Synth input port (5011:0) 130:0'

	# initialize MIDI file player thread
	playerThread = Thread(target=dexmoOutput.practice_task,
						  args=(midiFileLocation, targetTemp, targetTimes, guidance))

	playerThread.start()



	# KEYBOARD MIDI INPUT THREAD
	# (has been started before)

	# activate input handling
	inputThread.inputOn()

	# ... MIDI playing ...

	# wait for MIDI player thread to terminate
	playerThread.join()

	# deactivate input handling
	inputThread.inputOff()


	# get array with actual notes
	actualTimes = inputThread.noteInfoList

	###TODO: remove/change
	# print results
	print("\n\n--- NOTES ---")
	print("\nTarget notes:", targetTimes)
	print("\nActual notes:", actualTimes)



	# COMPUTE ERROR (naive example)
	global errorDiff

	timeSums, errorDiff = errorCalc.computeError(targetTimes, actualTimes)
	print("\n\n--- ERRORS ---")
	print("\nTARGET TIME:", timeSums[0])
	print("\nACTUAl TIME:", timeSums[1])
	print("\nDIFFERENCE: ", errorDiff)

def get_errors():
	return errorDiff



# inputThread will die on main termination
#sys.exit()
