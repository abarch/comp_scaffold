# run midi player and keyboard input as separate threads
# kill by Ctrl-C

from threading import Thread

import dexmoOutput
from midiInput import MidiInputThread, empty_noteinfo
from error_calc import functions as errorCalc
from collections import defaultdict
from midiOutput import MidiOutputThread
import time
import config
import fileIO

# GLOBAL CONSTANTS
MAX_NOTE = 128
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
    # targetTemp = [[-1, -1, -1]] * MAX_NOTE (PL)


def initInputThread():
    """
    Initializes MIDI keyboard input thread.

    @return: None
    """
    global inputThread

    # create inputThread instance (port is set to None in constructor)
    inputThread = MidiInputThread()


def initOutputThread(root):
    global outputThread

    outputThread = MidiOutputThread(MAX_NOTE, root)


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
        return (True)
    else:
        print("ERROR: inputThread was not defined yet")


# set MIDI input port from GUI (installing callback for input messages)
def set_outport(portName):
    global outputThread, portname
    portname = portName

    # check if inputThread was defined
    if 'outputThread' in globals():
        outputThread.setPort(portName)
        return True
    else:
        print("ERROR: outputThread was not defined yet")


def startThreads(midiFileLocation, guidance, task_data, taskParameters, useVisualAttention=True):
    """
    Starts the MIDI playback thread and activates the MIDI input handler.
    After the player thread terminates, the input handler is deactivated again.
    The user's played notes and the error are received and displayed afterwards.

    @param midiFileLocation: Path to the MIDI file.
    @param guidance: Current Dexmo guidance mode.
    @return: Target notes, actual notes and the error.
    """
    global targetTemp, targetTimes, inputThread, outputThread

    ###TODO: change?
    resetArrays()
    inputThread.resetArrays()
    # outputThread.resetArrays()

    if useVisualAttention:
        from openfaceInput import OpenFaceInput
        ofi = OpenFaceInput()
        ofi.start()

    # MIDI PLAYER THREAD
    # initialize MIDI file player thread
    playerThread = Thread(target=dexmoOutput.practice_task_with_midi,  # target=outputThread.playMidi (PL)
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

    if useVisualAttention:
        import time
        time.sleep(2)
        openface_data = ofi.stop()

        if openface_data is not None:
            import noteHandler as nh
            midi_offset = nh.startTime

            # note time = real_time - midi_offset
            # of   time = real_time
            openface_data.timestamp = openface_data.timestamp - midi_offset

    else:
        openface_data = None

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
    imp.reload(errorCalc)

    try:
        if len(actualTimes) == 0:  # i.e. they did not play
            print("No notes were played!!!")
            return targetTimes, actualTimes, 99, 99, 99, task_data, 'No notes were played'

        output_note_list, errorVec, errorVecLeft, errorVecRight = \
            errorCalc.computeErrorEvo(task_data, actualTimes,
                                      openface_data=openface_data,
                                      inject_explanation=True,
                                      plot=False)
        print("task data", task_data.__dict__)
        print("\n\n--- ERRORS ---")
        print("\nNOTE_ERRORS:")
        import shutil
        cwidth = shutil.get_terminal_size().columns

        # print("NOTES".center(cwidth, "+"))
        note_errorString = []
        for n in output_note_list:
            print(n.err_string())
            note_errorString.append(n.err_string(use_colors=False))
        print("\nSUMMED ERROR: ", errorVec)

        print("ERROR LEFT: ", errorVecLeft)
        print("ERROR RIGHT:", errorVecRight)

        # sum(errorVec[:7]): since errorVec[7] is the number of notes it is excluded from the sum
        # changed to sum([errorVec[i] for i in [0,2,3,4,5,6]]) in order to exclude note_hold_time error which is less relevant
        # return targetTimes, actualTimes, sum(errorVec[:7]), errorVecLeft, errorVecRight, task_data, note_errorString
        return targetTimes, actualTimes, sum([errorVec[i] for i in [0,2,3,4,5,6]]), errorVecLeft, errorVecRight, task_data, note_errorString
    except:
        import traceback
        traceback.print_exc()

        return targetTimes, actualTimes, 99


def startThreadsPianoCapture(midiFileLocation, guidance, task_data, taskParameters, useVisualAttention=True):
    """
    Starts the MIDI playback thread and activates the MIDI input handler.
    After the player thread terminates, the input handler is deactivated again.
    The user's played notes and the error are received and displayed afterwards.

    @param midiFileLocation: Path to the MIDI file.
    @param guidance: Current Dexmo guidance mode.
    @return: Target notes, actual notes and the error.
    """
    global targetTemp, targetTimes, inputThread, outputThread

    ###TODO: change?
    resetArrays()
    inputThread.resetArrays()
    # outputThread.resetArrays()

    if useVisualAttention:
        from openfaceInput import OpenFaceInput
        ofi = OpenFaceInput()
        ofi.start()

    # MIDI PLAYER THREAD
    # initialize MIDI file player thread
    playerThread = Thread(target=outputThread.playMidi,
                          args=(midiFileLocation, guidance, True))
    playerThread.start()

    # KEYBOARD MIDI INPUT THREAD (has been started before)
    # activate input handling
    inputThread.inputOn()

    # ... MIDI playing ...

    # wait for MIDI player thread to terminate
    playerThread.join()

    # deactivate input handling
    inputThread.inputOff()

    if useVisualAttention:
        import time
        time.sleep(2)
        openface_data = ofi.stop()

        if openface_data is not None:
            import noteHandler as nh
            midi_offset = nh.startTime

            # note time = real_time - midi_offset
            # of   time = real_time
            openface_data.timestamp = openface_data.timestamp - midi_offset

    else:
        openface_data = None

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
    imp.reload(errorCalc)

    try:
        if len(actualTimes) == 0:  # i.e. they did not play
            print("No notes were played!!!")
            return targetTimes, actualTimes, 99, 99, 99, task_data, 'No notes were played'

        output_note_list, errorVec, errorVecLeft, errorVecRight = \
            errorCalc.computeErrorEvo(task_data, actualTimes,
                                      openface_data=openface_data,
                                      inject_explanation=True,
                                      plot=False)
        print("task data", task_data.__dict__)
        print("\n\n--- ERRORS ---")
        print("\nNOTE_ERRORS:")
        import shutil
        cwidth = shutil.get_terminal_size().columns

        # print("NOTES".center(cwidth, "+"))
        note_errorString = []
        for n in output_note_list:
            print(n.err_string())
            note_errorString.append(n.err_string(use_colors=False))
        print("\nSUMMED ERROR: ", errorVec)

        print("ERROR LEFT: ", errorVecLeft)
        print("ERROR RIGHT:", errorVecRight)

        # sum(errorVec[:7]): since errorVec[7] is the number of notes it is excluded from the sum
        # changed to sum([errorVec[i] for i in [0,2,3,4,5,6]]) in order to exclude note_hold_time error which is less relevant
        # return targetTimes, actualTimes, sum(errorVec[:7]), errorVecLeft, errorVecRight, task_data, note_errorString
        return targetTimes, actualTimes, sum([errorVec[i] for i in [0,2,3,4,5,6]]), errorVecLeft, errorVecRight, task_data, note_errorString
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


# Only record the user without playing the expected midi file.
# If duration is set to 0, wait for the stop button to be pressed
def startRecordThread(midiFileLocation, guidance, duration, root):
    global targetTemp, inputThread, outputThread

    ###TODO: change?
    resetArrays()
    inputThread.resetArrays()

    # KEYBOARD MIDI INPUT THREAD
    # (has been started before)

    # activate input handling
    print("starting input on.")
    inputThread.inputOn()

    if duration > 0:
        root.update()
        root.after(duration * 1000, recordingFinished)


def recordingFinished():
    global targetTimes, actualTimes

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

    timeSums, errorDiff = errorCalc.computeErrorOld(targetTimes, actualTimes)
    print("\n\n--- ERRORS ---")
    print("\nTARGET TIME:", timeSums[0])
    print("\nACTUAl TIME:", timeSums[1])
    print("\nDIFFERENCE: ", errorDiff)

    options = [1, True, "bla"]
    fileIO.createXML(config.outputDir,
                     config.currentMidi + config.str_date + config.participant_id + "_" + config.freetext, options,
                     targetTimes)

    # create entry containing actual notes in XML
    fileIO.createTrialEntry(config.outputDir,
                            config.currentMidi + config.str_date + config.participant_id + "_" + config.freetext,
                            config.timestr, config.guidanceMode,
                            actualTimes, errorDiff)
    ###TODO: remove (testing)
    # fileIO.printXML(config.outputDir + config.currentMidi + ".xml", True)
    print("Created XML")
