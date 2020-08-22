# run midi player and keyboard input as separate threads
# kill by Ctrl-C

from threading import Thread

import dexmoOutput
from midiInput import MidiInputThread
import errorCalc


# GLOBAL CONSTANTS
MAX_NOTE = 128
global portname


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



# initialize keyboard input thread
def initInputThread():
	global inputThread

	# create inputThread instance (port is set to None in constructor)
	inputThread = MidiInputThread(MAX_NOTE)	

# set MIDI input port from GUI (installing callback for input messages)
def set_inport(portName):
	global inputThread, portname
	portname = portName

	# check if inputThread was defined
	if 'inputThread' in globals():
		inputThread.setPort(portName)
	else:
		print("ERROR: inputThread was not defined yet")


def startThreads(midiFileLocation, guidance):
	global targetTemp, targetTimes, inputThread

	###TODO: change?
	resetArrays()
	inputThread.resetArrays()


	# MIDI PLAYER THREAD

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

	return targetTimes, actualTimes, errorDiff


###TODO: remove?
def get_errors():
	return errorDiff
