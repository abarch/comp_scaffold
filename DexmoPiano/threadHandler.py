from threading import Thread

import dexmoOutput
from midiInput import MidiInputThread, empty_noteinfo
import errorCalc
import errorCalcLevenshtein as errorCalcLV

from collections import defaultdict

# GLOBAL CONSTANTS
global portname


def resetArrays():
    """
    Resets global lists/arrays (target and temporary notes).

    @return: None
    """
    global targetTemp, targetTimes

    print("\nRESET!!!\n")

    # arrays for target and actual note times
    targetTimes = []

    # initialize list of tuples for note on/off times
    # index = note: [t_on, t_off, velocity]
    ###TODO: documentation (temporary etc.)
    targetTemp = defaultdict(empty_noteinfo)


def initInputThread():
    """
    Initializes MIDI keyboard input thread.

    @return: None
    """
    global inputThread

    # create inputThread instance (port is set to None in constructor)
    inputThread = MidiInputThread()    

def set_inport(portName):
    """
    Sets MIDI input port (selected in GUI).

    @param portName: Name of the MIDI port.
    @return: None
    """
    global inputThread, portname
    portname = portName

    # check if inputThread was defined
    if 'inputThread' in globals():
        inputThread.setPort(portName)
    else:
        print("ERROR: inputThread was not defined yet")


def startThreads(midiFileLocation, guidance):
    """
    Starts the MIDI playback thread and activates the MIDI input handler.
    After the player thread terminates, the input handler is deactivated again.
    The user's played notes and the error are received and displayed afterwards.

    @param midiFileLocation: Path to the MIDI file.
    @param guidance: Current Dexmo guidance mode.
    @return: Target notes, actual notes and the error.
    """
    global targetTemp, targetTimes, inputThread

    ###TODO: change?
    resetArrays()
    inputThread.resetArrays()

    # MIDI PLAYER THREAD
    # initialize MIDI file player thread
    playerThread = Thread(target=dexmoOutput.practice_task,
                          args=(midiFileLocation, targetTemp, targetTimes, guidance))
    playerThread.start()


    # KEYBOARD MIDI INPUT THREAD (has been started before)
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

    # timeSums, errorDiff = errorCalc.computeError(targetTimes, actualTimes)
    # print("\n\n--- ERRORS ---")
    # print("\nTARGET TIME:", timeSums[0])
    # print("\nACTUAl TIME:", timeSums[1])
    # print("\nDIFFERENCE: ", errorDiff)

    import imp
    imp.reload(errorCalcLV)

    try:
        output_note_list, errorVec = errorCalcLV.computeError(targetTimes, actualTimes)
        print("\n\n--- ERRORS ---")
        print("\nNOTE_ERRORS:")
        from pprint import pprint
        pprint([n.err_string() for n in output_note_list])
        print("\nSUMMED ERROR: ", errorVec)
    

        return targetTimes, actualTimes, sum(errorVec)
    except:
        import traceback
        traceback.print_exc()
        
        return targetTimes, actualTimes, 99


###TODO: remove?
def get_errors():
    """
    Returns the error (currently the naive prototype).

    @return: Error value.
    """
    return errorDiff
