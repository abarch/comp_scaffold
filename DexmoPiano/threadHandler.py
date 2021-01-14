# run midi player and keyboard input as separate threads
# kill by Ctrl-C

from threading import Thread

from midiOutput import MidiOutputThread
from midiInput import MidiInputThread
import errorCalc
import time

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
 
def initOutputThread():
    global outputThread
    
    outputThread = MidiOutputThread(MAX_NOTE)

# set MIDI input port from GUI (installing callback for input messages)
def set_inport(portName):
    global inputThread, portname
    portname = portName
    
    # check if inputThread was defined
    if 'inputThread' in globals():
        inputThread.setPort(portName)
        return(True)
    else:
        print("ERROR: inputThread was not defined yet")

# set MIDI input port from GUI (installing callback for input messages)
def set_outport(portName):
    global outputThread, portname
    portname = portName
    
    # check if inputThread was defined
    if 'outputThread' in globals():
        outputThread.setPort(portName)
        return(True)
    else:
        print("ERROR: outputThread was not defined yet")

def startThreads(midiFileLocation, guidance):
    global targetTemp, targetTimes, inputThread, outputThread
    
    ###TODO: change?
    resetArrays()
    inputThread.resetArrays()
    outputThread.resetArrays()
    # MIDI PLAYER THREAD
    # initialize MIDI file player thread
    playerThread = Thread(target=outputThread.playMidi,
						  args=(midiFileLocation, guidance))
    
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

# Only record the user without playing the expected midi file.

def startRecordThread(midiFileLocation, guidance):
    global targetTemp, targetTimes, inputThread, outputThread

    ###TODO: change?
    resetArrays()
    inputThread.resetArrays()
    outputThread.resetArrays()
    # MIDI PLAYER THREAD
    # initialize MIDI file player thread
 #   playerThread = Thread(target=outputThread.playMidi,
 #                         args=(midiFileLocation, guidance))

 #   playerThread.start()

    # KEYBOARD MIDI INPUT THREAD
    # (has been started before)

    # activate input handling
    print("starting input on.")
    inputThread.inputOn()

    # ... MIDI playing ...
    # wait for MIDI player thread to terminate
    #playerThread.join()
    time.sleep(5)
    # deactivate input handling
    print("starting input off.")
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