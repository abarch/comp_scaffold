import pathlib
import tkinter as tk
from tkinter import filedialog, NW
from PIL import Image, ImageTk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import subprocess
import os

import dexmoOutput
import midiProcessing
import config
import threadHandler

from optionsWindow import optionsWindowClass
from task_generation.generator import TaskParameters

OUTPUT_DIR = './output/'
TEMP_DIR = './output/temp/'
inputFileStrs = [TEMP_DIR + 'output.mid', TEMP_DIR + 'output-m.mid', TEMP_DIR + 'output-md.mid',
                 TEMP_DIR + 'output.xml']
OUTPUT_LY_STR = TEMP_DIR + 'output.ly'
OUTPUT_PNG_STR = TEMP_DIR + 'output.png'

LILYPOND_PYTHON_EXE_WIN = "c:/Program Files (x86)/LilyPond/usr/bin/python.exe"
XMl_2_LY_WIN_FOLDER = "c:/Program Files (x86)/LilyPond/usr/bin/musicxml2ly"
MIDI_TO_LY_WIN = "c:/Program Files (x86)/LilyPond/usr/bin/midi2ly"

guidance_modes = ["None", "At every note", "Individual"]
guidance_mode = "At every note"
task_parameters = TaskParameters()

first_start = True
midi_bpm_label = None

errors = []
change_task = []

root = tk.Tk()

# TODO: define real threshold for both tasks
ERROR_THRESHOLD = 3
EXIT_PRACTISE_MODE_THRESHOLD = 1


class LearningState:

    def on_enter(self):
        pass

    def on_exit(self):
        pass

    def next_state(self):
        raise NotImplementedError("nextState() must be implemented in subclasses")

    def is_end(self):
        return False


class ShowCompleteSong(LearningState):

    def on_enter(self):
        midi_file = filedialog.askopenfilename(
            filetypes=[("Midi files", ".midi .mid")])
        midiProcessing.generate_metronome_and_fingers_for_midi(task_parameters.left,
                                                               task_parameters.right,
                                                               inputFileStrs,
                                                               midi_file,
                                                               )
        gen_ly_for_current_task()
        subprocess.run(['lilypond', '--png', '-o', TEMP_DIR, OUTPUT_LY_STR],
                       stderr=subprocess.DEVNULL)
        load_note_sheet(OUTPUT_PNG_STR)
        check_dexmo_connected(mainWindow=True)

    def next_state(self):
        return feedback_state


class FeedbackState(LearningState):

    def on_enter(self):
        add_error_plot()

    def next_state(self):
        return None

    def is_end(self):
        return True


class CalcError(LearningState):

    def get_next_state(self):
        error = 0
        # TODO: How to calculate error?
        if error < ERROR_THRESHOLD:
            return calc_error_state
        else:
            return end_state


class PractiseModeState(LearningState):

    def get_next_state(self):
        return feedback_state


class EndOfOnePractiseItterationState(LearningState):

    def get_next_state(self):
        # TODO: Add case when user want to exit practise loop
        user_forced_exit = False
        # TODO: How to calc error?
        error = 0
        if user_forced_exit:
            return show_complete_song
        else:
            if error < ERROR_THRESHOLD:
                return show_complete_song
            else:
                return practise_mode_state


class EndState(LearningState):

    def is_end(self):
        return True


show_complete_song = ShowCompleteSong()
feedback_state = FeedbackState()
calc_error_state = CalcError()
practise_mode_state = PractiseModeState()

end_state = EndState()


class Statemachine:

    def __init__(self):
        self.current_state = show_complete_song

    def start(self):
        show_complete_song.on_enter()
        next_state = show_complete_song.next_state()
        # TODO: Replace dummy loop by call switch in btns or after events are done
        while next_state is not None and not self.current_state.is_end():
            self.to_next_state(next_state)

    def to_next_state(self, next_state):
        self.current_state.on_exit()
        self.current_state = next_state
        self.current_state.on_enter()


def add_error_plot():
    """
    Adds a plot to the main window that shows the user's errors.

    @return: None
    """
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
    checkbox = tk.Checkbutton(root, text='show error show_error_details', command=add_error_details,
                              var=details)
    checkbox.place(x=1050, y=440)


def add_error_details():
    """
    Adds descriptions and show_error_details concerning the user's error to the error plot.

    @return: None
    """
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

    global checkbox, details
    details = tk.BooleanVar()
    details.set(True)
    checkbox = tk.Checkbutton(root, text='show error show_error_details', command=add_error_plot, var=details)
    checkbox.place(x=1050, y=440)


def clear_frame():
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
    clear_frame()
    load_start_menu()


def updateGuidance():
    global showNotes1, showNotes2, showScoreGuidance, showVerticalGuidance, canvas, piano_img, hand_img

    config.showVerticalGuidance = showVerticalGuidance.get()

    if showVerticalGuidance.get() == 0:
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


def load_gp_training_interface():
    """
    Create several GUI buttons (start demo, start task etc.).

    @return: None
    """
    global node_params
    global currentMidi, metronome
    global showScoreGuidance, showVerticalGuidance
    global id_textbox, freetext
    global midi_bpm_label

    showScoreGuidance = tk.IntVar(value=1)
    showVerticalGuidance = tk.IntVar(value=1)
    showVerticalGuidanceCheck = tk.Checkbutton(root, text='Show vertical guidance',
                                               variable=showVerticalGuidance,
                                               command=updateGuidance)
    showVerticalGuidanceCheck.place(x=1050, y=300, height=50, width=150)
    config.showVerticalGuidance = showVerticalGuidance.get()

    node_params = tk.StringVar()
    node_params.set("")
    tk.Label(root, textvariable=node_params, font=("Courier", 12)).place(x=10, y=40)

    # add button to disable metronome sound
    metronome = tk.BooleanVar()
    metronome.set(dexmoOutput.metronome)
    checkmetronome = tk.Checkbutton(root, text='play metronome', variable=metronome,
                                    command=dexmoOutput.set_metronome)
    checkmetronome.place(x=10, y=200)

    ##  GUIDANCE Mode
    l = tk.Label(root, text=" Guidance mode:")
    l.place(x=10, y=220, width=150, height=70)
    guidance = tk.StringVar(root)
    guidance.set(guidance_mode)

    guideopt = tk.OptionMenu(root, guidance, *guidance_modes, command=set_guidance)
    guideopt.place(x=10, y=270, width=150, height=30)

    # Scalebar to change BPM in loaded MIDI File
    l = tk.Label(root, text=" BPM for loaded MIDI File:")
    l.place(x=10, y=550)

    midiBPM = tk.Text(root, bg="white", fg="black", relief=tk.GROOVE, bd=1, height=1, width=10,
                      state=tk.NORMAL)
    midiBPM.place(x=10, y=580)
    midiBPM.insert(tk.INSERT, 0)

    global useVisualAttention
    useVisualAttention = tk.BooleanVar()
    useVisualAttention.set(False)
    chk = tk.Checkbutton(root, text='Use Visual Attention', var=useVisualAttention)
    chk.place(x=0, y=735)

    ## Back to Menu
    tk.Button(root, text='Back to Menu', command=backToMenu).place(x=10, y=940, height=50,
                                                                   width=150)

    id_textbox = tk.Text(root, bg="white", fg="black", relief=tk.GROOVE, bd=1, state=tk.NORMAL)
    id_textbox.place(x=1050, y=480, height=25, width=150)
    id_textbox.insert(tk.INSERT, "Enter ID")

    freetext = tk.Text(root, bg="white", fg="black", relief=tk.GROOVE, bd=1)
    freetext.place(x=1050, y=520, height=60, width=150)
    freetext.insert(tk.INSERT, "Free text")


def load_note_sheet(png):
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


def add_no_fingernumbers_warning():
    """
    Creates a warning in case that a created or selected MIDI has only to less notes to
    show fingernumbers.

    @return: None
    """
    global numNotesWarning
    numNotesWarning = tk.Label(root,
                               text=" Info: \n Too few notes generated to show\n fingernumbers on music sheet.",
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


def gen_ly_for_current_task():
    """
    Generates a .ly file (LilyPond format) from the current task's file (needed for png generation).
    If the file is in MusicXML format, finger numbers are taken into account. This is not the case
    for MIDI files.

    @return: None
    """
    xmlGenerated = False
    files = os.listdir(TEMP_DIR)
    for item in files:
        if item.endswith('.xml'):
            xmlGenerated = True

    # create png from music xml with fingernumbers
    # or from midi without finger numbers, if to less notes are generated
    if xmlGenerated:
        delete_no_fingernumbers_warning()
        subprocess.run(
            [LILYPOND_PYTHON_EXE_WIN if os.name == 'nt' else 'musicxml2ly', XMl_2_LY_WIN_FOLDER,
             inputFileStrs[3], '--output=' + OUTPUT_LY_STR],
            stderr=subprocess.DEVNULL)

    else:
        add_no_fingernumbers_warning()
        if os.name == 'nt':
            subprocess.run([LILYPOND_PYTHON_EXE_WIN, MIDI_TO_LY_WIN,
                            inputFileStrs[0], '--output=' + OUTPUT_LY_STR],
                           stderr=subprocess.DEVNULL)
        else:
            subprocess.run(['midi2ly',
                            inputFileStrs[0], '--output=' + OUTPUT_LY_STR],
                           stderr=subprocess.DEVNULL)


def start_gp_learning():
    load_gp_training_interface()
    Statemachine().start()


def load_start_menu():
    """
    Loads the start window with buttons for starting the first task and
    quitting the program.

    @return: None
    """
    tk.Button(root, text='Start GP learning', command=start_gp_learning).place(x=675, y=560,
                                                                               height=50,
                                                                               width=150)
    tk.Button(root, text='Quit', command=quit).place(x=675, y=500, height=50, width=150)
    choose_ports()


def choose_ports():
    """
    Creates drop-down menus for choosing the ports for MIDI input/output and Dexmo
    in the start window.

    @return: None
    """
    global dexmo_port_btn, first_start

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
        global first_start
        # place button label (text)
        l = tk.Label(root, text=portText + " port:")
        l.place(x=X_POS, y=yPos, height=TEXT_HEIGHT, width=WIDTH)

        # match port
        midiPort = tk.StringVar(root)
        if firstStart:
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
    dexmo_port_btn = createPortButton("Dexmo output", "dexmo", 680, outports, dexmoOutput.set_dexmo)
    createPortButton("Sound output", "qsynth", 760, outports,
                     dexmoOutput.set_sound_outport)
    createPortButton("Piano input", "vmpk", 840, inports, threadHandler.set_inport)

    firstStart = False


def set_guidance(guidance):
    """
    Sets guidance mode globally.

    @param guidance: Guidance mode.
    @return: None
    """
    global guidance_mode
    guidanceMode = guidance


def add_dexmo_Warning():
    """
    Creates a warning in case that Dexmo is not connected.

    @return: None
    """
    tk.Label(root, text=" Warning: \n No Dexmo connected, \n no guidance possible.",
             fg="red").place(x=10, y=300, width=150, height=70)


def check_dexmo_connected(mainWindow):
    """
    Checks if Dexmo is connected and changes the list of feasible guidance modes accordingly.

    @param mainWindow: True if the current window is the main window.
    @return: None
    """

    global guidance_modes, guidance_mode
    if dexmo_port_btn.get() == "None":
        GuidanceModeList = ["None"]
        guidanceMode = "None"
        if mainWindow:
            add_dexmo_Warning()
    else:
        GuidanceModeList = ["None", "At every note", "Individual"]


if __name__ == '__main__':
    # create file output folder if it does not already exist
    pathlib.Path(TEMP_DIR).mkdir(exist_ok=True)
    # Create a window and title
    root.title("Piano with Dexmo")

    threadHandler.initInputThread()

    load_start_menu()
    # Set the resolution of window
    root.geometry("1500x1000")

    check_dexmo_connected(mainWindow=False)
    options = optionsWindowClass(root=root, taskParamters=task_parameters)

    root.mainloop()
