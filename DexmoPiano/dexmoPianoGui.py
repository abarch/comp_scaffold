# -*- coding: utf-8 -*-
# Main file for Piano with Dexmo project (2020)

# from tkinter import *
import tkinter as tk
from pathlib import Path
from tkinter import filedialog
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import subprocess
import shutil
import time
import os
import pickle
import mido

import dexmoOutput
import fileIO
import midiProcessing
import config, difficulty, hmm_data_acquisition

from optionsWindow import optionsWindowClass
import threadHandler

# directory/filename strings
outputDir = './output/'
tempDir = './output/temp/'
inputFileStrs = [tempDir + 'output.mid', tempDir + 'output-m.mid', tempDir + 'output-md.mid', tempDir + 'output.xml']
outputLyStr = tempDir + 'output.ly'
outputPngStr = tempDir + 'output.png'
# outputLyStr = tempDir + 'output-midi.ly'
# outputPngStr = tempDir + 'output-midi.png'
windowsLilyPondPythonExe = "c:/Program Files (x86)/LilyPond/usr/bin/python.exe"
#windowsmusicxml2ly = "c:/Program Files (x86)/LilyPond/usr/bin/musicxml2ly.py"
windowsmusicxml2ly = "c:/Program Files (x86)/LilyPond/usr/bin/musicxml2ly"

#windowsmidi2ly = "c:/Program Files (x86)/LilyPond/usr/bin/midi2ly.py"
windowsmidi2ly = "c:/Program Files (x86)/LilyPond/usr/bin/midi2ly"

GuidanceModeList = ["None", "At every note", "Individual"]
guidanceMode = "At every note"

from task_generation.generator import TaskParameters

taskParameters = TaskParameters()


# maxNotePerBar = 2
# numberOfBars = 7
# bpm = 120
# noteValuesList = [1, 1 / 2, 1 / 4, 1 / 8]
# from task_generation.note_range_per_hand import NoteRangePerHand
# noteRangePerHand = NoteRangePerHand.C_TO_G
# twoHandsTup = (False, True)
## outFiles = [inputMidiStr, outputSubdir + 'output-m.mid']

errors = []
changetask = []

midiSaved = False
currentMidi = None

firstStart = True


def startTask():
    """
    Starts practice task which only has metronome output (if chosen) and haptic
    impulse from Dexmo for every note.

    @return: None
    """
    global currentMidi, midiSaved, errors, expMode

    timestr = getCurrentTimestamp()

    # use MIDI file with metronome staff

    config.participant_id = id_textbox.get("1.0",'end-1c')
    config.freetext = freetext.get("1.0",'end-1c')
    config.expMode = exp_mode.get()

    print("actual taskParameter in startTask:", taskParameters)
    targetNotes, actualNotes, errorVal, errorVecLeft, errorVecRight, task_data, note_errorString = \
        threadHandler.startThreads(inputFileStrs[2], guidanceMode,
                                   scheduler.current_task_data(), taskParameters,
                                   useVisualAttention=useVisualAttention.get())
    #df_error = hmm_data_acquisition.save_hmm_data(errorVecLeft, errorVecRight, task_data,
    #                                              taskParameters, note_errorString, config.participant_id, config.freetext)
    if difficultyScaling:
        next_level = difficulty.thresholds(df_error)
        print("Next Level", next_level)
        if next_level:
            new_complexity_level()
        else:
            get_threshold_info()

#    scheduler.register_error(errorVal)

    if not midiSaved:
        saveMidiAndXML(targetNotes, scheduler.current_task_data(), taskParameters)
        midiSaved = True

    eval_window = tk.Toplevel(root)
    eval_window.geometry("500x200")
    tk.Label(eval_window, text="Rate how difficult the task was for you (1-Easy, 7-Hard)").place(x=20, y=20)
    diff_rating = tk.StringVar(root)
    diff_rating.set('None')
    diff_rating_list = ["1", "2", "3", "4", "5","6","7"]
    diff_opt = tk.OptionMenu(eval_window, diff_rating, *diff_rating_list, command=set_diff_rating)
    diff_opt.place(x=400, y=20, width=100, height=30)

    tk.Label(eval_window, text="Rate your performance of the task (1-Low, 7-High)").place(x=20, y=80)
    performace_rating = tk.StringVar(root)
    performace_rating.set('None')
    performace_rating_list = ["1", "2", "3", "4", "5", "6", "7"]
    perf_opt = tk.OptionMenu(eval_window, performace_rating, *performace_rating_list, command=set_performance_rating)
    perf_opt.place(x=400, y=80, width=100, height=30)

    tk.Button(eval_window, text="Done", command = eval_window.destroy).place(x=200, y=140)
    root.wait_window(eval_window)
    print("after wait window")
    df_error = hmm_data_acquisition.save_hmm_data(errorVecLeft, errorVecRight, task_data,
                                                  taskParameters, note_errorString, config.participant_id,
                                                  config.freetext, config.expMode, config.trial_num, config.task_num, config.diff_rating, config.performance_rating)

    config.trial_num += 1

    # create entry containing actual notes in XML
    fileIO.createTrialEntry(outputDir, currentMidi, timestr, guidanceMode, actualNotes, errorVal)
    ###TODO: remove (testing)
    fileIO.printXML(outputDir + currentMidi + ".xml", True)

    # errorVal = threadHandler.get_errors()
    errors.append(abs(errorVal))
    add_error_plot()

    ## if there is a score with errors, show it in a new window
    if  True: # not difficultyScaling:
        score_with_error = Path(tempDir) / "output_with_errors.png"

        # Remove display of score with errors for tempo experiment

        # if score_with_error.exists():
        #     new_window = tk.Toplevel(root)
        #     new_window.geometry("835x1181")
        #     background = Image.open(score_with_error)
        #     background = background.convert("RGBA")
        #
        #     img = ImageTk.PhotoImage(background)
        #
        #     panel = tk.Label(new_window, image=img)
        #     panel.image = img
        #     panel.place(x=0, y=0, width=835, height=1181)

    refresh_buttons()

def set_diff_rating(rating):
    """
        Sets difficulty rating globally.

        @param rating: user's selected rating.
        @return: None
        """
    global config
    config.diff_rating = rating
    print(config.diff_rating)

def set_performance_rating(rating):
    """
            Sets performance rating globally.

            @param rating: user's selected rating.
            @return: None
            """
    global config
    config.performance_rating = rating

def startDemo():
    """
    Starts demo (playback) of the practice task with piano and (if chosen) metronome
    output as well as haptic impulse from Dexmo for every note.

    @return: None
    """
    # use MIDI file with metronome staff
    dexmoOutput.play_demo(inputFileStrs[2], guidanceMode)


def saveMidiAndXML(targetNotes, taskData, taskParameters):
    """
    Saves the MIDI and the XML file to the globally defined output folder.

    @param targetNotes: List of notes to be played by the user.
    @param taskData: a class with all task data.
    @param taskParameters: a list of the parameters that generated the task.
    @return: None
    """
    global currentMidi

    timestr = getCurrentTimestamp()

    # MIDI
    print("\nMIDI SAVED:", timestr)  ###TODO: Delete
    currentMidi = timestr
    shutil.copy(inputFileStrs[0], outputDir + timestr + '.mid')
    shutil.copy(inputFileStrs[1], outputDir + timestr + '-m.mid')
    shutil.copy(inputFileStrs[2], outputDir + timestr + '-md.mid')

    # save taskData and task Parameters to pickle file
    data_to_save = [taskData, taskParameters]
    with open(outputDir + timestr + '-data.task', 'wb') as f:
        pickle.dump(data_to_save, f)

    # XML
    # currOptions = [bpm, numberOfBars, maxNotePerBar, noteValuesList, noteRangePerHand, twoHandsTup]
    fileIO.createXML(outputDir, timestr, taskParameters.astuple(), targetNotes)

    config.savedFileName = timestr + '.xml'

def getCurrentTimestamp():
    """
    Receives and formats the current time and date.
    @return: Current timestamp (YearMonthDay-HourMinuteSecond).
    """
    return time.strftime("%Y_%m_%d-%H_%M_%S")


def generateNextTask():
    from task_generation.scheduler import choosePracticeMode
    from task_generation.practice_modes import PracticeMode
    choice = choosePracticeMode(root)

    def inEnum(val, enum):
        try:
            return val in enum
        except:
            return False

    if choice == "NEW_TASK":
        nextTask()
        update_complexity_index('?')
        return
    elif choice == "TEST_MOVEMENT_1":
        scheduler.new_task_forced_practice_sequence_prior(taskParameters,
                                                          [PracticeMode.SINGLE_NOTE])
        loadUpTask()
    elif choice == "NEXT_LEVEL":
        new_complexity_level()
    elif inEnum(choice, PracticeMode):
        scheduler.queue_practice_mode(choice)
        loadUpTask()
    elif choice == "X":
        print("The window to generate a new task was closed without specifing a new task.")
    else:
        raise ValueError(f"Unexpected choice {repr(choice)}!")


def nextTask():
    scheduler.get_next_task(taskParameters=taskParameters)
    loadUpTask()


def previousTask():
    scheduler.get_previous_task()
    loadUpTask()


def loadUpTask(userSelectedTask=False, userSelectedLocation=inputFileStrs[0]):
    """
    Generates a new MIDI file considering the current settings or opens a user-selected one.
    In each case, a metronome track and fingering numbers are added (if possible).
    The resulting file (MIDI or MusicXML) is converted to a sheet music (png) using LilyPond.

    @param userSelectedTask: True if the task is user-selected, False otherwise.
    @param userSelectedLocation: Location of the user-selected MIDI file (if chosen).
    @return: None
    """
    global midiSaved, currentMidi, taskParameters, leftHand, rightHand
    delete_warning()

    # load saved midi
    if userSelectedTask:
        chosenMidiFile = userSelectedLocation
        try:
            midiProcessing.generate_metronome_for_midi(taskParameters.left, taskParameters.right, inputFileStrs,
                                                                   chosenMidiFile,
                                                                   custom_bpm=int(midiBPM.get("1.0", 'end-1c')))
            #midiProcessing.generate_metronome_and_fingers_for_midi(False, True, inputFileStrs,
            #                                                       chosenMidiFile, custom_bpm=midiBPM.get("1.0",'end-1c'))
            #taskData, taskParameters = midiProcessing.generate_metronome_and_fingers_for_midi(taskParameters.left, taskParameters.right, inputFileStrs,
            #                                                       chosenMidiFile, custom_bpm=int(midiBPM.get("1.0",'end-1c')))
        except:
            add_both_hands_warning()
            return

    # generate new midi
    else:
        # files = os.listdir(tempDir)
        # for item in files:
        #     if item.endswith('.xml'):
        #         os.remove(os.path.join(tempDir, item))

        # new task is correctly created
        config.fromFile = False
        config.fileName = ""

        task = scheduler.current_task_data()

        # new xml file is not correctly created -> bug must be in generateMidi
        midiProcessing.generateMidi(task,
                                    outFiles=inputFileStrs)

        currentMidi = None
        midiSaved = False
        chosenMidiFile = inputFileStrs[0]

    get_ly()

    subprocess.run(['lilypond', '--png', '-o', tempDir, outputLyStr], stderr=subprocess.DEVNULL)
    # clearFrame()
    load_notesheet(outputPngStr)

    check_dexmo_connected(mainWindow=True)
    refresh_buttons()
    load_taskButtons()

    # if task is changed remember trial to show in visualisation
    if errors:
        changetask.append(len(errors))

    add_error_plot()

    config.task_num += 1
    config.trial_num = 1


# def nextSavedTask(goToTask=False):
#     """
#     Loads the next (newer) saved MIDI file if it exists.

#     @param goToTask: True for switching to next task immediately.
#     @return: False if no next task is found.
#     """
#     global midiSaved, currentMidi, errors, changetask
#     if currentMidi == None:
#         return False

#     files = getTimeSortedMidiFiles()
#     # if the current file is already the newest or there are none, there is no next task
#     if len(files) < 1 or (files.index(currentMidi) + 1) == len(files):
#         return False

#     newMidi = files[files.index(currentMidi) + 1]

#     if (goToTask == True):
#         # TODO: delete? and add errors from xml in GUI
#         errors = []
#         changetask = []

#         midiSaved = True
#         currentMidi = newMidi
#         loadUpTask(userSelectedTask=True, userSelectedLocation=outputDir + newMidi + '.mid')


# def previousTask(goToTask=False):
#     """
#     Loads the previous (older) saved MIDI file if it exists.

#     @param goToTask: True for switching to next task immediately.
#     @return: False if no previous task is found.
#     """
#     global midiSaved, currentMidi, errors, changetask

#     files = getTimeSortedMidiFiles()
#     # if there are no midi files return false
#     if len(files) < 1:
#         return False

#     # if the current is already the oldest, there is no previous task
#     if (currentMidi != None):
#         if files.index(currentMidi) == 0:
#             return False

#     # if actual task is already saved, use second newest to go back
#     if midiSaved:
#         newMidi = files[files.index(currentMidi) - 1]
#     else:
#         newMidi = files[len(files) - 1]

#     if (goToTask == True):
#         # TODO: delete? and add errors from xml in GUI
#         errors = []
#         changetask = []

#         midiSaved = True
#         currentMidi = newMidi
#         loadUpTask(userSelectedTask=True, userSelectedLocation=outputDir + newMidi + '.mid')


def check_dexmo_connected(mainWindow):
    """
    Checks if Dexmo is connected and changes the list of feasible guidance modes accordingly.

    @param mainWindow: True if the current window is the main window.
    @return: None
    """
    # TODO: Make dexmo_port not global?
    global GuidanceModeList, guidanceMode, dexmo_port
    if (dexmo_port.get() == "None"):
        GuidanceModeList = ["None"]
        guidanceMode = "None"
        if (mainWindow):
            add_Dexmo_Warning()
    else:
        GuidanceModeList = ["None", "At every note", "Individual"]


def load_notesheet(png):
    """
    Loads the note sheet (png) for the current task.

    @param png: Image file (png format).
    @return: None
    """
    global background

    background = Image.open(png)
    background = background.convert("RGBA")
    # width, height = background.size

    img = ImageTk.PhotoImage(background)
    panel = tk.Label(root, image=img)
    panel.image = img
    panel.place(x=170, y=0, width=835, height=1181)


def deleteOldFiles():
    """
    Deletes possible old MIDI and XML files from the last execution.

    @return: None
    """
    files = os.listdir(outputDir)
    for item in files:
        if item.endswith('.mid') or item.endswith('.xml'):
            os.remove(os.path.join(outputDir, item))


def get_ly():
    """
    Generates a .ly file (LilyPond format) from the current task's file (needed for png generation).
    If the file is in MusicXML format, finger numbers are taken into account. This is not the case
    for MIDI files.

    @return: None
    """
    xmlGenerated = False
    files = os.listdir(tempDir)
    for item in files:
        if item.endswith('.xml'):
            xmlGenerated = True

    # create png from music xml with fingernumbers
    # or from midi without finger numbers, if to less notes are generated
    if xmlGenerated:
        delete_no_fingernumbers_warning()
        if os.name == 'nt':
            subprocess.run([windowsLilyPondPythonExe, windowsmusicxml2ly,
                             inputFileStrs[3], '--output=' + outputLyStr], stderr = subprocess.DEVNULL)
        else:
            subprocess.run(['musicxml2ly',
                             inputFileStrs[3], '--output=' + outputLyStr], stderr = subprocess.DEVNULL)

    else:
        add_no_fingernumbers_warning()
        if os.name == 'nt':
            subprocess.run([windowsLilyPondPythonExe, windowsmidi2ly,
                            inputFileStrs[0], '--output=' + outputLyStr], stderr = subprocess.DEVNULL)
        else:
            subprocess.run(['midi2ly',
                            inputFileStrs[0], '--output=' + outputLyStr], stderr = subprocess.DEVNULL)


def showGuidanceNotesheet():
    """
    Displays the note sheet also containing the Dexmo guidance tracks.

    @return: None
    """
    if (showGuidance.get()):  # output_md anzeigen
        if os.name == 'nt':
            subprocess.run([windowsLilyPondPythonExe, windowsmidi2ly,
                            inputFileStrs[2], '--output=' + outputLyStr], stderr = subprocess.DEVNULL)
        else:
            subprocess.run(['midi2ly',
                            inputFileStrs[2], '--output=' + outputLyStr], stderr = subprocess.DEVNULL)

    else:  # output xml oder midi
        get_ly()

    subprocess.run(['lilypond', '--png', '-o', tempDir, outputLyStr], stderr=subprocess.DEVNULL)
    load_notesheet(outputPngStr)


##_______________________________OPTIONS______________________________________##
def specifyTask():
    """
    Updates the current options set by the user in the options window.

    @return: None
    """
    global errors, changetask, taskParameters

    prev_values = taskParameters

    print("TaskParam in Dexmo specify", repr(taskParameters))
    options.changeParameter()

    newValues = options.get_data()
    # if parameters changed, delete errors to start a new diagram
    if prev_values != newValues:
        errors = []
        changetask = []
    taskParameters = newValues


##_____________________________ERROR-PLOT_____________________________________##
# TODO: add error plot with saved xml errors, if previous or next task is chosen
def add_error_plot():
    """
    Adds a plot to the main window that shows the user's errors.

    @return: None
    """
    tk.Label(root, text=" Error visualization:").place(x=1200, y=10, width=150, height=20)

    fig = Figure(figsize=(9, 6), facecolor="white")
    axis = fig.add_subplot(111)
    np.linspace(0, 10, 1000)

    xvalues = []
    for i in range(len(errors)):
        xvalues.append(i + 1)
    axis.plot(xvalues, errors, label="General error", marker='o')

    if (changetask):
        for i in changetask:
            axis.axvline(x=i + 0.5, color="black")
            axis.text(i + 0.5, 4.05, "new task", rotation=45, fontsize=8)

    axis.axhline(y=0.2, color="red", linestyle="--")

    axis.set_xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    # axis.set_xticks(xvalues)
    axis.set_yticks([0, 1, 2, 3])
    axis.set_ylim(0, 4)
    axis.set_xlabel("Trials")
    axis.set_ylabel("Error")
    # axis.legend()
    axis.grid()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas._tkcanvas.place(x=1050, y=30, width=400, height=400)

    global checkbox, details
    details = tk.BooleanVar()
    details.set(False)
    checkbox = tk.Checkbutton(root, text='show error details', command=add_error_details, var=details)
    checkbox.place(x=1050, y=440)


def add_error_details():
    """
    Adds descriptions and details concerning the user's error to the error plot.

    @return: None
    """
    fig = Figure(figsize=(9, 6), facecolor="white")
    axis = fig.add_subplot(111)
    x = np.linspace(0, 10, 1000)

    xvalues = []
    for i in range(len(errors)):
        xvalues.append(i + 1)
    axis.plot(xvalues, errors, label="General error", marker='o')

    if (changetask):
        for i in changetask:
            axis.axvline(x=i + 0.5, color="black")
            axis.text(i + 0.5, 4.05, "new task", rotation=45, fontsize=8)

    axis.set_xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    # axis.set_xticks(xvalues)
    axis.set_yticks([0, 1, 2, 3])
    axis.set_ylim(0, 4)
    axis.set_xlabel("Trials")
    axis.set_ylabel("Error")

    axis.plot(x, np.sin(x), "-r", label="Tempo")
    axis.plot(x, np.cos(x), "-g", label="Notes")
    axis.plot(x, np.tan(x), "--y", label="etc")

    axis.legend(loc='upper right')
    axis.grid()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas._tkcanvas.place(x=1050, y=30, width=400, height=400)

    global checkbox, details
    details = tk.BooleanVar()
    details.set(True)
    checkbox = tk.Checkbutton(root, text='show error details', command=add_error_plot, var=details)
    checkbox.place(x=1050, y=440)


##____________________________________________________________________________##

def add_no_fingernumbers_warning():
    """
    Creates a warning in case that a created or selected MIDI has only to less notes to
    show fingernumbers.

    @return: None
    """
    global numNotesWarning
    numNotesWarning = tk.Label(root, text=" Info: \n Too few notes generated to show\n fingernumbers on music sheet.",
                               fg="red")
    numNotesWarning.place(x=1030, y=770, width=250, height=100)


def delete_no_fingernumbers_warning():
    """
    Removes the warning created by add_no_fingernumbers_warning().

    @return: None
    """
    global numNotesWarning
    numNotesWarning = tk.Label(root, text="")
    numNotesWarning.place(x=1030, y=770, width=250, height=100)


def add_both_hands_warning():
    """
    Creates a warning in case that a user-selected MIDI file has only one track/staff
    but both hands are currently selected.

    @return: None
    """
    global handWarning
    handWarning = tk.Label(root, text=" Warning: \n Hand selection error \n or too few notes in file.",
                           fg="red")
    handWarning.place(x=10, y=660, width=150, height=70)


def delete_warning():
    """
    Removes the warning created by add_both_hands_warning().

    @return: None
    """
    global handWarning
    handWarning = tk.Label(root, text="")
    handWarning.place(x=10, y=660, width=150, height=70)


def add_Dexmo_Warning():
    """
    Creates a warning in case that Dexmo is not connected.

    @return: None
    """
    tk.Label(root, text=" Warning: \n No Dexmo connected, \n no guidance possible.",
             fg="red").place(x=10, y=300, width=150, height=70)


# create button for demo, practicing, next task, back to start menu, guidance mode
def load_taskButtons():
    """
    Create several GUI buttons (start demo, start task etc.).

    @return: None
    """
    global node_params
    global currentMidi, metronome
    global showScoreGuidance, showVerticalGuidance
    global id_textbox, freetext
    global exp_mode, quickBPM


    showScoreGuidance = tk.IntVar(value=1)
    showVerticalGuidance = tk.IntVar(value=1)
    showVerticalGuidanceCheck = tk.Checkbutton(root, text='Show vertical guidance', variable=showVerticalGuidance,
                                               command=updateGuidance)
    showVerticalGuidanceCheck.place(x=1200, y=300, height=50, width=200)
    config.showVerticalGuidance = showVerticalGuidance.get()


    node_params = tk.StringVar()
    node_params.set("")
    tk.Label(root, textvariable=node_params, font=("Courier", 12)).place(x=10, y=40)
    tk.Button(root, text='Start Task', command=startTask).place(x=10, y=90, height=50, width=150)
    tk.Button(root, text='Start Demo', command=startDemo).place(x=10, y=150, height=50, width=150)

    # add button to disable metronome sound
    metronome = tk.BooleanVar()
    metronome.set(dexmoOutput.metronome)
    checkmetronome = tk.Checkbutton(root, text='play metronome', variable=metronome, command=dexmoOutput.set_metronome)
    checkmetronome.place(x=10, y=200)

    ##  GUIDANCE Mode
    l = tk.Label(root, text=" Guidance mode:")
    l.place(x=10, y=220, width=150, height=70)
    guidance = tk.StringVar(root)
    guidance.set(guidanceMode)
    guideopt = tk.OptionMenu(root, guidance, *GuidanceModeList, command=set_guidance)
    guideopt.place(x=10, y=270, width=150, height=30)

    tk.Button(root, text='Generate new Task', command=generateNextTask).place(x=10, y=370, height=40, width=150)
    tk.Button(root, text='Specify next Task', command=specifyTask).place(x=10, y=415, height=40, width=150)
    tk.Button(root, text='Recommender', command=dif_scaling).place(x=10, y=470, height=40, width=150)
    tk.Button(root, text='Open Midi file', command=openfile).place(x=10, y=520, height=25, width=150)

    # Scalebar to change BPM in loaded MIDI File
    global loadMidiBPM, midiBPM
    l = tk.Label(root, text=" BPM for loaded MIDI File:")
    l.place(x=10, y=550)

    tk.Button(root, text='Open saved MIDI File', command=openSavedFile).place(x=10, y=635, height=25, width=150)

 #   midiBPM = tk.Scale(root, from_=0, to=250, length=150, orient=tk.HORIZONTAL)
 #   midiBPM.place(x=10, y=570)
 #   midiBPM.set(0)
    try:
        current_midiBPM = midiBPM.get("1.0", 'end-1c')
    except:
        current_midiBPM = 0
    midiBPM = tk.Text(root, bg="white", fg="black", relief=tk.GROOVE, bd=1, height=1, width=10,
                          state=tk.NORMAL)
    midiBPM.place(x=10, y=580)
    midiBPM.insert(tk.INSERT, current_midiBPM)


    l2 = tk.Label(root, text="0 will load BPM from MIDI")
    l2.place(x=10, y=610)

    global useVisualAttention
    useVisualAttention = tk.BooleanVar()
    useVisualAttention.set(False)
    chk = tk.Checkbutton(root, text='Use Visual Attention', var=useVisualAttention)
    chk.place(x=0, y=735)

    ## Back to Menu
    tk.Button(root, text='Back to Menu', command=backToMenu).place(x=10, y=940, height=50, width=150)

    try:
        current_participant_id = id_textbox.get("1.0", 'end-1c')
        current_freetext = freetext.get("1.0", 'end-1c')
        current_exp_mode = exp_mode.get()
        current_quickBPM = quickBPM.get("1.0", 'end-1c')
    except:
        current_participant_id = "Enter ID"
        current_freetext = "Free text"
        current_exp_mode = "None"
        current_quickBPM = "0"
    id_textbox = tk.Text(root, bg="white", fg="black", relief=tk.GROOVE, bd=1, state=tk.NORMAL)
    id_textbox.place(x=1050, y=480, height=25, width=150)
    #id_textbox.insert(tk.INSERT, "Enter ID")
    id_textbox.insert(tk.INSERT, current_participant_id)

    freetext = tk.Text(root, bg="white", fg="black", relief=tk.GROOVE, bd=1)
    freetext.place(x=1050, y=520, height=60, width=150)
    #freetext.insert(tk.INSERT, "Free text")
    freetext.insert(tk.INSERT, current_freetext)

    ##  Experiment Mode
    l = tk.Label(root, text=" Mode:")
    l.place(x=1050, y=590, width=150, height=25)
    exp_mode = tk.StringVar(root)
    exp_mode.set(current_exp_mode)
    ExpModeList = ["Calibration", "Practice","Test", "Retention"]
    guideopt = tk.OptionMenu(root, exp_mode, *ExpModeList, command=set_expmode)
    guideopt.place(x=1050, y=620, width=150, height=30)

    ## quick bpm

    quickBPM = tk.Text(root, bg="white", fg="black", relief=tk.GROOVE, bd=1, height=1, width=10,
                      state=tk.NORMAL)
    quickBPM.place(x=1050, y=660)
    quickBPM.insert(tk.INSERT, current_quickBPM)

    tk.Button(root, text='Generate', command=genQuickTask).place(x=1050, y=690, height=25, width=150)
    tk.Button(root, text='Apply', command=applyQuickBPM).place(x=1050, y=720, height=25, width=150)




difficultyScaling = False
complex_index = 0
nodes = None
node_params = None
def dif_scaling():
    global taskParameters, difficultyScaling,  taskSet, nodes, node_params

    start_with_level=0
    node_params.set(str(start_with_level))
    difficultyScaling = True
    taskSet, nodes= difficulty.getTasks()

    taskParameters = taskSet[start_with_level]

    scheduler.get_next_task(taskParameters)
    print ("new task params", taskParameters)
    loadUpTask()
    update_complexity_index(start_with_level)
#
# def dif_scaling():
#     global taskParameters, difficultyScaling
#
#     previous = taskParameters
#     difficultyScaling = True
#     parameters, index = difficulty.getTaskComplexity()
#     #TODO: How and where to show index of complexity level
#     taskParameters = parameters
#     scheduler.get_next_task(parameters)
#     loadUpTask()
#     update_complexity_index(index)

def get_threshold_info():
    #global difficultyScaling

    threshold_info(root)
    #difficultyScaling = False


def new_complexity_level():
    global  taskSet, complex_index, nodes, node_params
    try:
        if complex_index+1<len(nodes):
            print ("complex_index", complex_index)
            #new_parameters, index = difficulty.getTaskComplexity(previous)
            new_parameters = taskSet[complex_index+1]
            print("New complexity_level: ", repr(new_parameters))
            scheduler.get_next_task(new_parameters)
            loadUpTask()
            update_complexity_index(complex_index+1)
            node_params.set(str(nodes[complex_index]))
        else:
            #get back to the first exercise, preliminary hack..
            print ("going back to the first complexity level")
            update_complexity_index(0)

    except TypeError:
        print("Error: To use the predefined complexity levels, please start the Dynamic Difficulty Adjustment!")
        complexity_error(root)


def update_complexity_index(index):
    global complex_index
    complex_index = index



def updateGuidance():
    global showNotes1, showNotes2, showScoreGuidance, showVerticalGuidance, canvas, piano_img, hand_img

    config.showVerticalGuidance = showVerticalGuidance.get()

    if showVerticalGuidance.get() == 0:
        canvas.create_rectangle(0, 200, 500, 600, fill='white', outline='white')
    else:
        setupVisualNotes()

    if showNotes1.get() == 0:
        canvas.create_rectangle(200, 300, 200 + 264 - 1, 300 + 219 - 1, fill='white', outline='white')
    else:
        canvas.create_image(200, 300, anchor=NW, image=piano_img)

    if showNotes2.get() == 0:
        canvas.create_rectangle(470, 300, 470 + 277 - 1, 300 + 277 - 1, fill='white', outline='white')
    else:
        canvas.create_image(470, 300, anchor=NW, image=hand_img)


def refresh_buttons():
    """
    Updates buttons and checkboxes that change with a new task (next/previous task and
    guidance in the note sheet).

    @return: None
    """
    # next and previous tasks buttons
    if not scheduler.next_task_exists():
        tk.Button(root, text='Next Task >>', state=tk.DISABLED).place(x=10, y=800, height=50,
                                                                      width=150)
    else:
        tk.Button(root, text='Next Task >>', command=nextTask).place(x=10, y=800, height=50, width=150)

    # files = getTimeSortedMidiFiles()
    # if currentMidi != None:
    #     currMidiIdx = files.index(currentMidi) + 1
    #     l2 = tk.Label(root, text=" Midi File " + str(currMidiIdx) + " of " + str(len(files)))
    #     l2.place(x=10, y=860, width=150, height=20)

    if not scheduler.previous_task_exists():
        tk.Button(root, text='<< Previous Task', state=tk.DISABLED).place(x=10, y=880, height=50,
                                                                          width=150)
    else:
        tk.Button(root, text='<< Previous Task', command=previousTask).place(x=10, y=880, height=50, width=150)

    # add button to show note sheet with haptic guidance
    global showGuidance
    showGuidance = tk.BooleanVar()
    showGuidance.set(False)
    checkShowGuidance = tk.Checkbutton(root, text='show guidance in note sheet', variable=showGuidance,
                                       command=showGuidanceNotesheet)
    checkShowGuidance.place(x=1050, y=900)


# set guidance for task
def set_guidance(guidance):
    """
    Sets guidance mode globally.

    @param guidance: Guidance mode.
    @return: None
    """
    global guidanceMode
    guidanceMode = guidance

def set_expmode(chosenExpMode):
    """
    Sets guidance mode globally.

    @param guidance: Guidance mode.
    @return: None
    """
    global expMode
    expMode = chosenExpMode

def genQuickTask():
    """
        Generates a task with current params but with the quick bpm.

        @param None
        @return: None
    """
    global quickBPM, taskParameters

    quick_bpm = quickBPM.get("1.0", 'end-1c')
    taskParameters.bpm = quick_bpm
    scheduler.get_next_task(taskParameters=taskParameters)
    loadUpTask()

def applyQuickBPM():
    """
        Applies the quick bpm to current task.

        @param: None
        @return: None
    """
    global quickBPM, midiSaved, currentMidi, taskParameters, taskData

    quick_bpm = int(quickBPM.get("1.0", 'end-1c'))

    if quick_bpm > 0:
        # change tempo to custom tempo
        temp_mido_file0 = mido.MidiFile(inputFileStrs[0])
        for i in range(len(temp_mido_file0.tracks[0])):
            if temp_mido_file0.tracks[0][i].type=='set_tempo':
                found_ind = i;
        print("found ind :", i)
        temp_mido_file0.tracks[0][found_ind].tempo = int(60000000 / quick_bpm)  # tempo is in MicroTempo units.
        temp_mido_file0.save(inputFileStrs[0])

        temp_mido_file1 = mido.MidiFile(inputFileStrs[1])
        for i in range(len(temp_mido_file1.tracks[0])):
            if temp_mido_file1.tracks[0][i].type=='set_tempo':
                found_ind = i;
        print("found ind :", i)
        temp_mido_file1.tracks[0][found_ind].tempo = int(60000000/quick_bpm) # tempo is in MicroTempo units.
        temp_mido_file1.save(inputFileStrs[1])

        temp_mido_file2 = mido.MidiFile(inputFileStrs[2])
        for i in range(len(temp_mido_file2.tracks[0])):
            if temp_mido_file2.tracks[0][i].type=='set_tempo':
                found_ind = i;
        print("found ind :", i)
        temp_mido_file2.tracks[0][found_ind].tempo = int(60000000 / quick_bpm)  # tempo is in MicroTempo units.
        temp_mido_file2.save(inputFileStrs[2])

        taskData = scheduler.current_task_data()
        taskData.bpm = quick_bpm
        taskParameters.bpm = quick_bpm

        # upadte midi events to taskData. The midi events changed due to the change of bpm.
        temp_mido_file = mido.MidiFile(inputFileStrs[0]) # outFile[0] (output.mid) is already updated with the custom bpm.
        # mid_left = midiProcessing._midi_messages_to_note_events(temp_mido_file.tracks[2], temp_mido_file)
        # mid_left = midiProcessing._midi_messages_to_note_events(temp_mido_file.tracks[2], temp_mido_file)
        mid_left = []
        mid_right = midiProcessing._midi_messages_to_note_events(temp_mido_file.tracks[1], temp_mido_file)
        taskData.midi.register_midi_events(mid_left, mid_right)

    # remove XML which has the previous tempo.
    try:
        os.remove(inputFileStrs[3])  # removes the XML file
    except:
        print("xml file was not found")

    #config.fromFile = True
    #config.loadedFileName = midi_file
    #config.customBPM = int(midiBPM.get("1.0", 'end-1c'))
    #print("data with new bpm:", taskData, taskParameters)
    scheduler.add_task_from_file(taskData, taskParameters)

    get_ly()

    subprocess.run(['lilypond', '--png', '-o', tempDir, outputLyStr], stderr=subprocess.DEVNULL)
    # clearFrame()
    load_notesheet(outputPngStr)

    check_dexmo_connected(mainWindow=True)
    refresh_buttons()
    load_taskButtons()

    # if task is changed remember trial to show in visualisation
    if errors:
        changetask.append(len(errors))

    add_error_plot()

    config.task_num += 1
    config.trial_num = 1


# open midi file user can choose
def openfile():
    """
    Opens user-selected MIDI file via a file dialog.

    @return: None
    """
    loadUpTask(userSelectedTask=True,
               userSelectedLocation=filedialog.askopenfilename(filetypes=[("Midi files", ".midi .mid")]))

# open midi file that was automatically created when task was played.
def openSavedFile():
    """
    Opens user-selected MIDI file via a file dialog.

    @return: None
    """
    #loadUpTask(userSelectedTask=True,
    #           userSelectedLocation=filedialog.askopenfilename(filetypes=[("Midi files", ".midi .mid")]))
    global midiSaved, currentMidi, taskParameters, taskData
    delete_warning()

    # load saved midi
    midi_file = filedialog.askopenfilename(filetypes=[("Midi files", ".midi .mid")])
#    chosenMidiFile = userSelectedLocation
    try:
        # midiProcessing.generate_metronome_and_fingers_for_midi(leftHand.get(), rightHand.get(), inputFileStrs,
        #                                                       chosenMidiFile, custom_bpm=midiBPM.get("1.0",'end-1c'))
        #taskData, taskParameters = midiProcessing.generate_metronome_and_fingers_for_midi(False, True,
        #                                                                                  inputFileStrs,
        #                                                                                  chosenMidiFile,
        #                                                                                  custom_bpm=int(
        #                                                                                      midiBPM.get("1.0",
        #                                                                                                  'end-1c')))

        # copy the saved outFiles to output/temp/ folder.
        # these files are saved when the user plays the task.
        basename, ext = os.path.splitext(midi_file)
        shutil.copy(basename + '.mid', inputFileStrs[0])
        shutil.copy(basename + '-m.mid', inputFileStrs[1])
        shutil.copy(basename + '-md.mid', inputFileStrs[2])

        # read the task data from file. This file is created when the user plays the task.
        with open(basename + '-data.task', 'rb') as f:
            task_data_from_file = pickle.load(f)
        print("loaded data: ", task_data_from_file)
        [taskData, taskParameters] = task_data_from_file

    except:
        print("didn't find metronome and/or dexmo files")

    midiSaved = False # create a new mid and xml file after loading a saved midi file

    custom_bpm = int(midiBPM.get("1.0",'end-1c'))
    if custom_bpm > 0:
        # change tempo to custom tempo
        temp_mido_file0 = mido.MidiFile(inputFileStrs[0])
        for i in range(len(temp_mido_file0.tracks[0])):
            if temp_mido_file0.tracks[0][i].type == 'set_tempo':
                found_ind = i;
        print("found ind :", i)
        temp_mido_file0.tracks[0][found_ind].tempo = int(60000000 / custom_bpm)  # tempo is in MicroTempo units.
        temp_mido_file0.save(inputFileStrs[0])

        temp_mido_file1 = mido.MidiFile(inputFileStrs[1])
        for i in range(len(temp_mido_file1.tracks[0])):
            if temp_mido_file1.tracks[0][i].type == 'set_tempo':
                found_ind = i;
        print("found ind :", i)
        temp_mido_file1.tracks[0][found_ind].tempo = int(60000000 / custom_bpm)  # tempo is in MicroTempo units.
        temp_mido_file1.save(inputFileStrs[1])

        temp_mido_file2 = mido.MidiFile(inputFileStrs[2])
        for i in range(len(temp_mido_file2.tracks[0])):
            if temp_mido_file2.tracks[0][i].type == 'set_tempo':
                found_ind = i;
        print("found ind :", i)
        temp_mido_file2.tracks[0][found_ind].tempo = int(60000000 / custom_bpm)  # tempo is in MicroTempo units.
        temp_mido_file2.save(inputFileStrs[2])

        taskData.bpm = custom_bpm
        taskParameters.bpm = custom_bpm

        # upadte midi events to taskData. The midi events changed due to the change of bpm.
        temp_mido_file = mido.MidiFile(inputFileStrs[0]) # outFile[0] (output.mid) is already updated with the custom bpm.
        #mid_left = midiProcessing._midi_messages_to_note_events(temp_mido_file.tracks[2], temp_mido_file) # commented due to a bug
        mid_left = []
        mid_right = midiProcessing._midi_messages_to_note_events(temp_mido_file.tracks[1], temp_mido_file)
        taskData.midi.register_midi_events(mid_left, mid_right)

    # remove XML which has the previous tempo.
    try:
        os.remove(inputFileStrs[3]) # removes the XML file
    except:
        print("xml file was not found")

    config.fromFile = True
    config.loadedFileName = midi_file
    config.customBPM = int(midiBPM.get("1.0", 'end-1c'))
    print("data with new bpm:", taskData, taskParameters)
    scheduler.add_task_from_file(taskData, taskParameters)

    get_ly()

    subprocess.run(['lilypond', '--png', '-o', tempDir, outputLyStr], stderr=subprocess.DEVNULL)
    # clearFrame()
    load_notesheet(outputPngStr)

    check_dexmo_connected(mainWindow=True)
    refresh_buttons()
    load_taskButtons()

    # if task is changed remember trial to show in visualisation
    if errors:
        changetask.append(len(errors))

    add_error_plot()

    config.task_num += 1
    config.trial_num = 1

def firstTask():
    """
    Starts the GUI, loads the buttons and initializes the first task.

    @return: None
    """
    load_taskButtons()
    if not os.path.exists("/tmp/DexmoPiano"):
        os.mkdir("/tmp/DexmoPiano")
    # try:
    #    os.mkdir("/tmp/DexmoPiano")
    nextTask()


def load_Startmenu():
    """
    Loads the start window with buttons for starting the first task and
    quitting the program.

    @return: None
    """
    tk.Button(root, text='Start first task', command=firstTask).place(x=675, y=440, height=50, width=150)
    tk.Button(root, text='Quit', command=quit).place(x=675, y=500, height=50, width=150)
    choose_ports()


def clearFrame():
    """
    Destroys all widgets from the frame.

    @return: None
    """
    for widget in root.winfo_children():
        widget.destroy()


def backToMenu():
    """
    Switches from main to start window.

    @return: None
    """
    clearFrame()
    load_Startmenu()


def quit():
    """
    Quits the program / closes the windows.

    @return: None
    """
    root.destroy()


def choose_ports():
    """
    Creates drop-down menus for choosing the ports for MIDI input/output and Dexmo
    in the start window.

    @return: None
    """
    global dexmo_port, firstStart

    # CONSTANTS
    X_POS = 660
    X_DIFF = 10
    Y_DIFF = 40
    TEXT_HEIGHT = 50
    FIELD_HEIGHT = 25
    WIDTH = 200

    def createPortButton(portText, findStr, yPos, portList, setFunc):
        """
        Creates a port menu and matches the current MIDI ports for a preselection.
        Example: If Dexmo is connected, a port having "Dexmo" in its name will be preselected.
                 If nothing is found, the user needs to selection the desired port manually.

        @param portText: Text of the port menu description.
        @param findStr: Keyword for matching the port (e.g. "Dexmo").
        @param yPos: Vertical position offset for description and menu.
        @param portList: List of currently existing MIDI ports.
        @param setFunc: Function for setting the port in the respective file.
        @return: MIDI port name (global).
        """
        global firstStart
        # place button label (text)
        l = tk.Label(root, text=portText + " port:")
        l.place(x=X_POS, y=yPos, height=TEXT_HEIGHT, width=WIDTH)

        # match port
        midiPort = tk.StringVar(root)
        if firstStart == True:
            matching = [s for s in portList if findStr in s.lower()]
            if matching:
                midiPort.set(matching[0])
            else:
                midiPort.set("None")

            setFunc(midiPort.get())
        else:
            if portText == "Dexmo output":
                midiPort.set(dexmoOutput.midi_interface)
            elif portText == "Sound output":
                midiPort.set(dexmoOutput.midi_interface_sound)
            elif portText == "Piano input":
                midiPort.set(threadHandler.portname)

        # place drop-down menu
        options = tk.OptionMenu(root, midiPort, *portList, command=setFunc)
        options.place(x=X_POS - X_DIFF, y=yPos + Y_DIFF, height=FIELD_HEIGHT, width=WIDTH)

        return midiPort

    # choose outport for (Lego)Dexmo etc
    outports, inports = dexmoOutput.get_midi_interfaces()
    outports.append("None")
    inports.append("None")

    # create port buttons with automatic port name choice (if possible)
    dexmo_port = createPortButton("Dexmo output", "dexmo", 600, outports, dexmoOutput.set_dexmo)
    sound_port = createPortButton("Sound output", "qsynth", 680, outports, dexmoOutput.set_sound_outport)
    input_port = createPortButton("Piano input", "vmpk", 760, inports, threadHandler.set_inport)

    firstStart = False


##_____________________________START LOOP HERE________________________________##

from task_generation.scheduler import Scheduler, threshold_info, complexity_error

scheduler = Scheduler(loadUpTask)

# create file output folder if it does not already exist
subprocess.run(['mkdir', '-p', tempDir], stderr=subprocess.DEVNULL)
# Create a window and title
root = tk.Tk()
root.title("Piano with Dexmo")

#deleteOldFiles()

# initialize keyboard input thread
threadHandler.initInputThread()

load_Startmenu()
# Set the resolution of window
root.geometry("1500x1000")

check_dexmo_connected(mainWindow=False)
options = optionsWindowClass(root=root, taskParamters=taskParameters)

root.mainloop()
