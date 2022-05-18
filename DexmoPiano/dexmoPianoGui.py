# -*- coding: utf-8 -*-
# Main file for Piano with Dexmo project (2020)
import pathlib
import tkinter as tk
from tkinter import filedialog, NW
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
import thread_handler

from optionsWindow import OptionsWindowClass
from pianoCapture import setupVisualNotes
from task_generation.generator import TaskParameters
from task_generation.scheduler import Scheduler, threshold_info, complexity_error
from task_generation.scheduler import choosePracticeMode
from task_generation.practice_modes import PracticeMode

# directory/filename strings
OUTPUT_DIR = './output/'
OUTPUT_TEMP_DIR = './output/temp/'

OUTPUT_FILES_STR = [OUTPUT_TEMP_DIR + 'output.mid', OUTPUT_TEMP_DIR + 'output-m.mid',
                    OUTPUT_TEMP_DIR + 'output-md.mid',
                    OUTPUT_TEMP_DIR + 'output.xml']

OUTPUT_LY_STR = OUTPUT_TEMP_DIR + 'output.ly'
OUTPUT_NOTE_SHEET_PNG = OUTPUT_TEMP_DIR + 'output.png'

LILYPOND_PYTHON_EXE_WIN = "c:/Program Files (x86)/LilyPond/usr/bin/python.exe"
XMl_2_LY_WIN_FOLDER = "c:/Program Files (x86)/LilyPond/usr/bin/musicxml2ly"
MIDI_TO_LY_WIN = "c:/Program Files (x86)/LilyPond/usr/bin/midi2ly"

guidance_modes = ["None", "At every note", "Individual"]
guidance_mode = "At every note"
task_parameters = TaskParameters()

errors = []
change_task = []

midi_saved = False
first_start = True
task_set = None

difficulty_scaling = False
complex_index = 0
nodes = None

root = tk.Tk()
root.title("Piano with Dexmo")

# Tk variables
show_error_details = tk.BooleanVar()
show_guidance = tk.BooleanVar()
metronome = tk.BooleanVar()
show_score_guidance = tk.IntVar(value=1)
show_vertical_guidance = tk.IntVar(value=1)
use_visual_attention = tk.BooleanVar()
node_params = tk.StringVar()

# Tk view elements
dexmo_port_btn = None
num_notes_warning_label = None
hand_warning_label = None
show_error_details_checkbox = None
midi_bpm_label = None
participant_id_text = None
free_text = None


def start_task():
    """
    Starts practice task which only has metronome output (if chosen) and haptic
    impulse from Dexmo for every note.

    @return: None
    """
    global midi_saved

    config.participant_id = participant_id_text.get("1.0", 'end-1c')
    config.freetext = free_text.get("1.0", 'end-1c')

    targetNotes, actualNotes, errorVal, errorVecLeft, errorVecRight, task_data, note_errorString = \
        thread_handler.start_midi_playback(OUTPUT_FILES_STR[2], guidance_mode,
                                           scheduler.current_task_data(),
                                           use_visual_attention=use_visual_attention.get())
    df_error = hmm_data_acquisition.save_hmm_data(errorVecLeft, errorVecRight, task_data,
                                                  task_parameters, note_errorString,
                                                  config.participant_id, config.freetext)
    if difficulty_scaling:
        next_level = difficulty.thresholds(df_error)
        print("Next Level", next_level)
        if next_level:
            new_complexity_level()
        else:
            threshold_info(root)

    if not midi_saved:
        save_midi_and_xml(targetNotes, scheduler.current_task_data(), task_parameters)
        midi_saved = True

    timestamp = get_current_timestamp()

    # create entry containing actual notes in XML
    fileIO.create_trial_entry(OUTPUT_DIR, timestamp, timestamp, guidance_mode, actualNotes, errorVal)

    errors.append(abs(errorVal))
    show_error_plot()

    refresh_buttons()


def start_demo():
    """
    Starts demo (playback) of the practice task with piano and (if chosen) metronome
    output as well as haptic impulse from Dexmo for every note.

    @return: None
    """
    # use MIDI file with metronome staff
    dexmoOutput.play_demo(OUTPUT_FILES_STR[2], guidance_mode)


def save_midi_and_xml(target_notes, task_data, task_parameters):
    """
    Saves the MIDI and the XML file to the globally defined output folder.

    @param target_notes: List of notes to be played by the user.
    @param task_data: a class with all task data.
    @param task_parameters: a list of the parameters that generated the task.
    @return: None
    """

    time_str = get_current_timestamp()

    # MIDI
    shutil.copy(OUTPUT_FILES_STR[0], OUTPUT_DIR + time_str + '.mid')
    shutil.copy(OUTPUT_FILES_STR[1], OUTPUT_DIR + time_str + '-m.mid')
    shutil.copy(OUTPUT_FILES_STR[2], OUTPUT_DIR + time_str + '-md.mid')

    # save task_data and task Parameters to pickle file
    data_to_save = [task_data, task_parameters]

    with open(OUTPUT_DIR + time_str + '-data.task', 'wb') as f:
        pickle.dump(data_to_save, f)

    fileIO.createXML(OUTPUT_DIR, time_str, task_parameters.astuple(), target_notes)


def get_current_timestamp() -> str:
    """
    Receives and formats the current time and date.
    @return: Current timestamp (YearMonthDay-HourMinuteSecond).
    """
    return time.strftime("%Y_%m_%d-%H_%M_%S")


def generate_next_task():
    choice = choosePracticeMode(root)

    def inEnum(val, enum):
        return val in enum

    if choice == "NEW_TASK":
        next_task()
        set_complexity_index('?')
        return
    elif choice == "TEST_MOVEMENT_1":
        scheduler.new_task_forced_practice_sequence_prior(task_parameters,
                                                          [PracticeMode.SINGLE_NOTE])
        load_up_task()
    elif choice == "NEXT_LEVEL":
        new_complexity_level()
    elif inEnum(choice, PracticeMode):
        scheduler.queue_practice_mode(choice)
        load_up_task()
    elif choice == "X":
        print("The window to generate a new task was closed without specifing a new task.")
    else:
        raise ValueError(f"Unexpected choice {repr(choice)}!")


def next_task():
    scheduler.get_next_task(task_parameters=task_parameters)
    load_up_task()


def load_previous_task():
    scheduler.get_previous_task()
    load_up_task()


def load_up_task(task_is_selected_by_user: bool = False, midi_file: str = OUTPUT_FILES_STR[0]):
    """
    Generates a new MIDI file considering the current settings or opens a user-selected one.
    In each case, a metronome track and fingering numbers are added (if possible).
    The resulting file (MIDI or MusicXML) is converted to a sheet music (png) using LilyPond.

    @param task_is_selected_by_user: True if the task is user-selected, False otherwise.
    @param midi_file: Location of the user-selected MIDI file (if chosen).
    @return: None
    """
    global midi_saved, task_parameters
    remove_both_hands_warning()

    # load saved midi
    if task_is_selected_by_user:
        try:
            midiProcessing.generate_metronome_and_fingers_for_midi(task_parameters.left,
                                                                   task_parameters.right,
                                                                   OUTPUT_FILES_STR,
                                                                   midi_file,
                                                                   custom_bpm=int(
                                                                       midi_bpm_label.get("1.0",
                                                                                          'end-1c')))

        # TODO: refactor to not use catch all
        except:
            show_both_hands_warning()
            return

    # generate new midi
    else:
        # new task is correctly created
        config.fileName = ""

        task = scheduler.current_task_data()

        # new xml file is not correctly created -> bug must be in generateMidi
        midiProcessing.generateMidi(task,
                                    outFiles=OUTPUT_FILES_STR)
        midi_saved = False

    gen_ly_for_current_task()

    subprocess.run(['lilypond', '--png', '-o', OUTPUT_TEMP_DIR, OUTPUT_LY_STR],
                   stderr=subprocess.DEVNULL)

    load_note_sheet(OUTPUT_NOTE_SHEET_PNG)

    check_dexmo_connected(main_window=True)
    refresh_buttons()
    load_interface()

    # if task is changed remember trial to show in visualisation
    if errors:
        change_task.append(len(errors))

    show_error_plot()


def check_dexmo_connected(main_window: bool):
    """
    Checks if Dexmo is connected and changes the list of feasible guidance modes accordingly.

    @param main_window: True if the current window is the main window.
    @return: None
    """

    global guidance_modes, guidance_mode
    if dexmo_port_btn.get() == "None":
        guidance_modes = ["None"]
        guidance_mode = "None"
        if main_window:
            add_dexmo_Warning()
    else:
        guidance_modes = ["None", "At every note", "Individual"]


def load_note_sheet(png: str):
    """
    Loads the note sheet (png) for the current task.

    @param png: Image file (png format).
    @return: None
    """

    background = Image.open(png)
    background = background.convert("RGBA")
    # width, height = background.size

    img = ImageTk.PhotoImage(background)
    panel = tk.Label(root, image=img)
    panel.image = img
    panel.place(x=170, y=0, width=835, height=1181)


def delete_xml_and_mid_output_files():
    """
    Deletes possible old MIDI and XML files from the last execution.

    @return: None
    """
    files = os.listdir(OUTPUT_DIR)
    for item in files:
        if item.endswith('.mid') or item.endswith('.xml'):
            os.remove(os.path.join(OUTPUT_DIR, item))


def gen_ly_for_current_task():
    """
    Generates a .ly file (LilyPond format) from the current task's file (needed for png generation).
    If the file is in MusicXML format, finger numbers are taken into account. This is not the case
    for MIDI files.

    @return: None
    """
    xml_generated = False
    files = os.listdir(OUTPUT_TEMP_DIR)
    for item in files:
        if item.endswith('.xml'):
            xml_generated = True

    # create png from music xml with fingernumbers
    # or from midi without finger numbers, if to less notes are generated
    if xml_generated:
        remove_finger_numbers_warning()
        if os.name == 'nt':
            subprocess.run([LILYPOND_PYTHON_EXE_WIN, XMl_2_LY_WIN_FOLDER,
                            OUTPUT_FILES_STR[3], '--output=' + OUTPUT_LY_STR],
                           stderr=subprocess.DEVNULL)
        else:
            subprocess.run(['musicxml2ly',
                            OUTPUT_FILES_STR[3], '--output=' + OUTPUT_LY_STR],
                           stderr=subprocess.DEVNULL)

    else:
        show_fingernumbers_warning()
        if os.name == 'nt':
            subprocess.run([LILYPOND_PYTHON_EXE_WIN, MIDI_TO_LY_WIN,
                            OUTPUT_FILES_STR[0], '--output=' + OUTPUT_LY_STR],
                           stderr=subprocess.DEVNULL)
        else:
            subprocess.run(['midi2ly',
                            OUTPUT_FILES_STR[0], '--output=' + OUTPUT_LY_STR],
                           stderr=subprocess.DEVNULL)


def generate_and_show_note_sheet():
    """
    Displays the note sheet also containing the Dexmo guidance tracks.

    @return: None
    """
    if show_guidance.get():
        if os.name == 'nt':
            subprocess.run([LILYPOND_PYTHON_EXE_WIN, MIDI_TO_LY_WIN,
                            OUTPUT_FILES_STR[2], '--output=' + OUTPUT_LY_STR],
                           stderr=subprocess.DEVNULL)
        else:
            subprocess.run(['midi2ly',
                            OUTPUT_FILES_STR[2], '--output=' + OUTPUT_LY_STR],
                           stderr=subprocess.DEVNULL)

    else:  # output xml oder midi
        gen_ly_for_current_task()

    subprocess.run(['lilypond', '--png', '-o', OUTPUT_TEMP_DIR, OUTPUT_LY_STR],
                   stderr=subprocess.DEVNULL)
    load_note_sheet(OUTPUT_NOTE_SHEET_PNG)


def specify_task():
    """
    Updates the current options set by the user in the options window.

    @return: None
    """
    global errors, change_task, task_parameters
    prev_values = task_parameters

    options.changeParameter()

    new_values = options.get_data()
    # if parameters changed, delete errors to start a new diagram
    if prev_values != new_values:
        errors = []
        change_task = []
    task_parameters = new_values


# TODO: add error plot with saved xml errors, if previous or next task is chosen
def show_error_plot():
    """
    Adds a plot to the main window that shows the user's errors.

    @return: None
    """

    global show_error_details_checkbox

    tk.Label(root, text=" Error visualization:").place(x=1200, y=10, width=150, height=20)

    fig = Figure(figsize=(9, 6), facecolor="white")
    axis = fig.add_subplot(111)
    np.linspace(0, 10, 1000)

    x_values = []
    for i in range(len(errors)):
        x_values.append(i + 1)
    axis.plot(x_values, errors, label="General error", marker='o')

    if change_task:
        for i in change_task:
            axis.axvline(x=i + 0.5, color="black")
            axis.text(i + 0.5, 4.05, "new task", rotation=45, fontsize=8)

    axis.axhline(y=0.2, color="red", linestyle="--")

    axis.set_xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
    axis.set_yticks([0, 1, 2, 3])
    axis.set_ylim(0, 4)
    axis.set_xlabel("Trials")
    axis.set_ylabel("Error")
    axis.grid()

    canvas = FigureCanvasTkAgg(fig, master=root)
    canvas._tkcanvas.place(x=1050, y=30, width=400, height=400)

    show_error_details.set(False)
    show_error_details_checkbox = tk.Checkbutton(root, text='show error show_error_details',
                                                 command=add_error_details,
                                                 variable=show_error_details)
    show_error_details_checkbox.place(x=1050, y=440)


def add_error_details():
    """
    Adds descriptions and show_error_details concerning the user's error to the error plot.

    @return: None
    """
    global show_error_details_checkbox, show_error_details

    fig = Figure(figsize=(9, 6), facecolor="white")
    axis = fig.add_subplot(111)
    x = np.linspace(0, 10, 1000)

    x_values = []
    for i in range(len(errors)):
        x_values.append(i + 1)
    axis.plot(x_values, errors, label="General error", marker='o')

    if change_task:
        for i in change_task:
            axis.axvline(x=i + 0.5, color="black")
            axis.text(i + 0.5, 4.05, "new task", rotation=45, fontsize=8)

    axis.set_xticks([1, 2, 3, 4, 5, 6, 7, 8, 9, 10])
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

    show_error_details.set(True)
    show_error_details_checkbox = tk.Checkbutton(root, text='show error show_error_details',
                                                 command=show_error_plot,
                                                 variable=show_error_details)
    show_error_details_checkbox.place(x=1050, y=440)


def show_fingernumbers_warning():
    """
    Creates a warning in case that a created or selected MIDI has only to less notes to
    show fingernumbers.

    @return: None
    """
    global num_notes_warning_label
    num_notes_warning_label = tk.Label(root,
                                       text=" Info: \n Too few notes generated to show\n fingernumbers on music sheet.",
                                       fg="red")
    num_notes_warning_label.place(x=1030, y=770, width=250, height=100)


def remove_finger_numbers_warning():
    """
    Removes the warning created by add_no_fingernumbers_warning().

    @return: None
    """
    global num_notes_warning_label
    num_notes_warning_label = tk.Label(root, text="")
    num_notes_warning_label.place(x=1030, y=770, width=250, height=100)


def show_both_hands_warning():
    """
    Creates a warning in case that a user-selected MIDI file has only one track/staff
    but both hands are currently selected.

    @return: None
    """
    global hand_warning_label
    hand_warning_label = tk.Label(root,
                                  text=" Warning: \n Hand selection error \n or too few notes in file.",
                                  fg="red")
    hand_warning_label.place(x=10, y=660, width=150, height=70)


def remove_both_hands_warning():
    """
    Removes the warning created by add_both_hands_warning().

    @return: None
    """
    global hand_warning_label
    hand_warning_label = tk.Label(root, text="")
    hand_warning_label.place(x=10, y=660, width=150, height=70)


def add_dexmo_Warning():
    """
    Creates a warning in case that Dexmo is not connected.

    @return: None
    """
    tk.Label(root, text=" Warning: \n No Dexmo connected, \n no guidance possible.",
             fg="red").place(x=10, y=300, width=150, height=70)


# create button for demo, practicing, next task, back to start menu, guidance mode
def load_interface():
    """
    Create several GUI buttons (start demo, start task etc.).

    @return: None
    """
    global metronome
    global participant_id_text, free_text
    global midi_bpm_label
    global show_score_guidance, show_vertical_guidance

    showVerticalGuidanceCheck = tk.Checkbutton(root, text='Show vertical guidance',
                                               variable=show_vertical_guidance,
                                               command=update_guidance)
    showVerticalGuidanceCheck.place(x=1200, y=300, height=50, width=200)
    config.showVerticalGuidance = show_vertical_guidance.get()

    node_params.set("")
    tk.Label(root, textvariable=node_params, font=("Courier", 12)).place(x=10, y=40)
    tk.Button(root, text='Start Task', command=start_task).place(x=10, y=90, height=50, width=150)
    tk.Button(root, text='Start Demo', command=start_demo).place(x=10, y=150, height=50, width=150)

    # add button to disable metronome sound
    metronome.set(dexmoOutput.metronome)
    check_metronome = tk.Checkbutton(root, text='play metronome', variable=metronome,
                                     command=dexmoOutput.set_metronome)
    check_metronome.place(x=10, y=200)

    ##  GUIDANCE Mode
    l = tk.Label(root, text=" Guidance mode:")
    l.place(x=10, y=220, width=150, height=70)
    guidance = tk.StringVar(root)
    guidance.set(guidance_mode)

    option_menu = tk.OptionMenu(root, guidance, *guidance_modes, command=set_guidance)
    option_menu.place(x=10, y=270, width=150, height=30)

    tk.Button(root, text='Generate new Task', command=generate_next_task).place(x=10, y=370,
                                                                                height=40,
                                                                                width=150)
    tk.Button(root, text='Specify next Task', command=specify_task).place(x=10, y=415, height=40,
                                                                          width=150)
    tk.Button(root, text='Recommender', command=dif_scaling).place(x=10, y=470, height=40,
                                                                   width=150)
    tk.Button(root, text='Open Midi file', command=open_midi_file).place(x=10, y=520, height=25,
                                                                         width=150)

    # Scalebar to change BPM in loaded MIDI File
    l = tk.Label(root, text=" BPM for loaded MIDI File:")
    l.place(x=10, y=550)

    tk.Button(root, text='Open saved MIDI File', command=open_saved_midi_file).place(x=10, y=635,
                                                                                     height=25,
                                                                                     width=150)

    midi_bpm_label = tk.Text(root, bg="white", fg="black", relief=tk.GROOVE, bd=1, height=1,
                             width=10,
                             state=tk.NORMAL)
    midi_bpm_label.place(x=10, y=580)
    midi_bpm_label.insert(tk.INSERT, 0)

    l2 = tk.Label(root, text="0 will load BPM from MIDI")
    l2.place(x=10, y=610)

    use_visual_attention.set(False)
    chk = tk.Checkbutton(root, text='Use Visual Attention', variable=use_visual_attention)
    chk.place(x=0, y=735)

    ## Back to Menu
    tk.Button(root, text='Back to Menu', command=reload_start_menu).place(x=10, y=940, height=50,
                                                                          width=150)

    participant_id_text = tk.Text(root, bg="white", fg="black", relief=tk.GROOVE, bd=1,
                                  state=tk.NORMAL)
    participant_id_text.place(x=1050, y=480, height=25, width=150)
    participant_id_text.insert(tk.INSERT, "Enter ID")

    free_text = tk.Text(root, bg="white", fg="black", relief=tk.GROOVE, bd=1)
    free_text.place(x=1050, y=520, height=60, width=150)
    free_text.insert(tk.INSERT, "Free text")


def dif_scaling():
    global task_parameters, difficulty_scaling, task_set, nodes, node_params

    start_with_level = 0
    node_params.set(str(start_with_level))
    difficulty_scaling = True
    task_set, nodes = difficulty.getTasks()

    task_parameters = task_set[start_with_level]

    scheduler.get_next_task(task_parameters)
    print("new task params", task_parameters)
    load_up_task()
    set_complexity_index(start_with_level)


def new_complexity_level():
    global task_set, complex_index, nodes, node_params

    assert isinstance(nodes, list)
    assert isinstance(task_set, list)
    assert node_params is not None
    try:
        next_complextiy_index = complex_index + 1
        if next_complextiy_index < len(nodes):
            print("complex_index", complex_index)
            new_parameters = task_set[next_complextiy_index]
            print("New complexity_level: ", repr(new_parameters))
            scheduler.get_next_task(new_parameters)
            load_up_task()
            set_complexity_index(next_complextiy_index)
            node_params.set(str(nodes[next_complextiy_index]))
        else:
            # get back to the first exercise, preliminary hack..
            print("going back to the first complexity level")
            set_complexity_index(0)

    except TypeError:
        print(
            "Error: To use the predefined complexity levels, please start the Dynamic Difficulty Adjustment!")
        complexity_error(root)


def set_complexity_index(index):
    global complex_index
    complex_index = index


def update_guidance():
    global showNotes1, showNotes2, show_vertical_guidance, canvas, piano_img, hand_img

    config.showVerticalGuidance = show_vertical_guidance.get()

    if show_vertical_guidance.get() == 0:
        canvas.create_rectangle(0, 200, 500, 600, fill='white', outline='white')
    else:
        setupVisualNotes()

    if showNotes1.get() == 0:
        canvas.create_rectangle(200, 300, 200 + 264 - 1, 300 + 219 - 1, fill='white',
                                outline='white')
    else:
        canvas.create_image(200, 300, anchor=NW, image=piano_img)

    if showNotes2.get() == 0:
        canvas.create_rectangle(470, 300, 470 + 277 - 1, 300 + 277 - 1, fill='white',
                                outline='white')
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
        tk.Button(root, text='Next Task >>', command=next_task).place(x=10, y=800, height=50,
                                                                      width=150)

    if not scheduler.previous_task_exists():
        tk.Button(root, text='<< Previous Task', state=tk.DISABLED).place(x=10, y=880, height=50,
                                                                          width=150)
    else:
        tk.Button(root, text='<< Previous Task', command=load_previous_task).place(x=10, y=880,
                                                                                   height=50,
                                                                                   width=150)

    # add button to show note sheet with haptic guidance
    show_guidance.set(False)
    checkShowGuidance = tk.Checkbutton(root, text='show guidance in note sheet',
                                       variable=show_guidance,
                                       command=generate_and_show_note_sheet)
    checkShowGuidance.place(x=1050, y=900)


# set guidance for task
def set_guidance(guidance):
    """
    Sets guidance mode globally.

    @param guidance: Guidance mode.
    @return: None
    """
    global guidance_mode
    guidance_mode = guidance


# open midi file user can choose
def open_midi_file():
    """
    Opens user-selected MIDI file via a file dialog.

    @return: None
    """
    load_up_task(task_is_selected_by_user=True,
                 midi_file=filedialog.askopenfilename(
                     filetypes=[("Midi files", ".midi .mid")]))


# open midi file that was automatically created when task was played.
def open_saved_midi_file():
    """
    Opens user-selected MIDI file via a file dialog.

    @return: None
    """

    global midi_saved, task_parameters
    remove_both_hands_warning()

    # load saved midi
    midi_file = filedialog.askopenfilename(filetypes=[("Midi files", ".midi .mid")])
    #    chosenMidiFile = midi_file
    try:
        # copy the saved outFiles to output/temp/ folder.
        # these files are saved when the user plays the task.
        basename, ext = os.path.splitext(midi_file)
        shutil.copy(basename + '.mid', OUTPUT_FILES_STR[0])
        shutil.copy(basename + '-m.mid', OUTPUT_FILES_STR[1])
        shutil.copy(basename + '-md.mid', OUTPUT_FILES_STR[2])

        # read the task data from file. This file is created when the user plays the task.
        with open(basename + '-data.task', 'rb') as f:
            task_data_from_file = pickle.load(f)
        print("loaded data: ", task_data_from_file)
        [task_data, task_parameters] = task_data_from_file

    except FileNotFoundError:
        print("didn't find metronome and/or dexmo files")

    custom_bpm = int(midi_bpm_label.get("1.0", 'end-1c'))
    if custom_bpm > 0:
        # change tempo to custom tempo
        temp_mido_file0 = mido.MidiFile(OUTPUT_FILES_STR[0])
        temp_mido_file0.tracks[0][1].tempo = int(
            60000000 / custom_bpm)  # tempo is in MicroTempo units.
        temp_mido_file0.save(OUTPUT_FILES_STR[0])

        temp_mido_file1 = mido.MidiFile(OUTPUT_FILES_STR[1])
        temp_mido_file1.tracks[0][1].tempo = int(
            60000000 / custom_bpm)  # tempo is in MicroTempo units.
        temp_mido_file1.save(OUTPUT_FILES_STR[1])

        temp_mido_file2 = mido.MidiFile(OUTPUT_FILES_STR[2])
        temp_mido_file2.tracks[0][1].tempo = int(
            60000000 / custom_bpm)  # tempo is in MicroTempo units.
        temp_mido_file2.save(OUTPUT_FILES_STR[2])

        task_data.bpm = custom_bpm
        task_parameters.bpm = custom_bpm

        # upadte midi events to task_data. The midi events changed due to the change of bpm.
        temp_mido_file = mido.MidiFile(
            OUTPUT_FILES_STR[0])  # outFile[0] (output.mid) is already updated with the custom bpm.
        mid_left = midiProcessing._midi_messages_to_note_events(temp_mido_file.tracks[2],
                                                                temp_mido_file)
        mid_right = midiProcessing._midi_messages_to_note_events(temp_mido_file.tracks[1],
                                                                 temp_mido_file)
        task_data.midi.register_midi_events(mid_left, mid_right)

    # remove XML which has the previous tempo.
    try:
        os.remove(OUTPUT_FILES_STR[3])  # removes the XML file
    except FileNotFoundError:
        print("xml file was not found")

    config.fromFile = True
    config.LoadedFileName = midi_file
    config.customBPM = int(midi_bpm_label.get("1.0", 'end-1c'))
    print("data with new bpm:", task_data, task_parameters)
    scheduler.add_task_from_file(task_data, task_parameters)

    gen_ly_for_current_task()

    subprocess.run(['lilypond', '--png', '-o', OUTPUT_TEMP_DIR, OUTPUT_LY_STR],
                   stderr=subprocess.DEVNULL)
    load_note_sheet(OUTPUT_NOTE_SHEET_PNG)

    check_dexmo_connected(main_window=True)
    refresh_buttons()
    load_interface()

    # if task is changed remember trial to show in visualisation
    if errors:
        change_task.append(len(errors))

    show_error_plot()


def init_gui_and_start_first_task():
    """
    Starts the GUI, loads the buttons and initializes the first task.

    @return: None
    """
    load_interface()
    if not os.path.exists("/tmp/DexmoPiano"):
        os.mkdir("/tmp/DexmoPiano")

    next_task()


def load_start_menu():
    """
    Loads the start window with buttons for starting the first task and
    quitting the program.

    @return: None
    """
    tk.Button(root, text='Start first task', command=init_gui_and_start_first_task).place(x=675,
                                                                                          y=440,
                                                                                          height=50,
                                                                                          width=150)
    tk.Button(root, text='Quit', command=quit_program).place(x=675, y=500, height=50, width=150)
    create_port_drop_downs()


def clear_frame():
    """
    Destroys all widgets from the frame.

    @return: None
    """
    for widget in root.winfo_children():
        widget.destroy()


def reload_start_menu():
    clear_frame()
    load_start_menu()


def quit_program():
    root.destroy()


def create_port_btn(portText: str, findStr: str, yPos: int, portList: [str],
                    setFunc) -> tk.StringVar:
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
    global first_start

    x_pos = 660
    x_diff = 10
    y_diff = 40
    text_height = 50
    field_height = 25
    width = 200

    # place button label (text)
    l = tk.Label(root, text=portText + " port:")
    l.place(x=x_pos, y=yPos, height=text_height, width=width)

    # match port
    midi_port = tk.StringVar(root)
    if first_start:
        matching = [s for s in portList if findStr in s.lower()]
        if matching:
            midi_port.set(matching[0])
        else:
            midi_port.set("None")

        setFunc(midi_port.get())
    else:
        if portText == "Dexmo output":
            midi_port.set(dexmoOutput.midi_interface)
        elif portText == "Sound output":
            midi_port.set(dexmoOutput.midi_interface_sound)
        elif portText == "Piano input":
            midi_port.set(thread_handler.portname)

    options_menu = tk.OptionMenu(root, midi_port, *portList, command=setFunc)
    options_menu.place(x=x_pos - x_diff, y=yPos + y_diff, height=field_height, width=width)

    return midi_port


def create_port_drop_downs():
    """
    Creates drop-down menus for choosing the ports for MIDI input/output and Dexmo
    in the start window.

    @return: None
    """
    global dexmo_port_btn, first_start

    # choose outport for (Lego)Dexmo etc
    outports, inports = dexmoOutput.get_midi_interfaces()
    outports.append("None")
    inports.append("None")

    # create port buttons with automatic port name choice (if possible)
    dexmo_port_btn = create_port_btn("Dexmo output", "dexmo", 680, outports, dexmoOutput.set_dexmo)
    create_port_btn("Sound output", "qsynth", 760, outports,
                    dexmoOutput.set_sound_outport)
    create_port_btn("Piano input", "vmpk", 840, inports, thread_handler.set_inport)

    first_start = False


if __name__ == '__main__':
    scheduler = Scheduler(load_up_task)

    # create file output folder if it does not already exist
    pathlib.Path(OUTPUT_TEMP_DIR).mkdir(parents=True, exist_ok=True)

    # initialize keyboard input thread
    thread_handler.init_midi_keyboard_thread()

    load_start_menu()
    # Set the resolution of window
    root.geometry("1500x1000")

    check_dexmo_connected(main_window=False)
    options = OptionsWindowClass(root=root, task_paramters=task_parameters)

    root.mainloop()
