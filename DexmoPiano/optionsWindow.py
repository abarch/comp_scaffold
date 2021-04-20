# from tkinter import *
import enum
import tkinter as tk

class NoteRangePerHand(enum.Enum):
    ONE_NOTE = enum.auto()
    TWO_NOTES = enum.auto()
    C_TO_G = enum.auto()
    ONE_OCTAVE = enum.auto()
    ONE_OCTAVE_WHITE = enum.auto()
    ONE_OCTAVE_BLACK = enum.auto()
    
    
noteRangePerHandDescription = ["One note (C)", "Two notes (C,D)", 
                               "Notes C-G (for 5 fingers)", "One octave",
                               "One octave (only white keys)",
                               "One octave (only black keys)"
                               ]

noteRangeMap = {const: desc for const, desc in 
                zip(NoteRangePerHand, noteRangePerHandDescription)}
noteRangeMap.update(                   
                    {desc: const for const, desc in 
                zip(NoteRangePerHand, noteRangePerHandDescription)}
                    )

def get_pitchlist(note_range, right=True):
    if right:
        base_note = 60 #C4
    else:
        base_note = 48 #C3
        
    if note_range == NoteRangePerHand.ONE_NOTE:
        pitchesList = [0]
    elif note_range == NoteRangePerHand.TWO_NOTES:
        pitchesList = [0, 2]
    elif note_range == NoteRangePerHand.C_TO_G:
        pitchesList = [0, 2, 4, 5, 7]
    elif note_range == NoteRangePerHand.ONE_OCTAVE:
        pitchesList = list(range(0, 12))
    elif note_range == NoteRangePerHand.ONE_OCTAVE_WHITE:
        pitchesList = [0,2,4,5,7,9,11]
    elif note_range == NoteRangePerHand.ONE_OCTAVE_BLACK:
        pitchesList = [1,3,6,8,10]
    else:
        raise ValueError(f"got unexpected note_range {repr(note_range)}!")
        
    return [base_note + p for p in pitchesList]
    

class optionsWindowClass():
    """
    Class for the GUI's options window, accessible from the main window.
    """

    def __init__(self, root, bpm, maxNoteperBar, numberOfBars, noteValuesList, noteRangePerHand, twoHandsTup):
        """
        Initializes necessary variables.

        @param root: GUI root.
        @param bpm: Tempo (beats per minute).
        @param maxNoteperBar: Maximum number of notes that a bar can contain.
        @param numberOfBars: Total number of bars.
        @param noteValuesList: Possible durations of the notes (e.g. 1, 1/2 etc.).
        @param pitchesList: Possible MIDI pitch numbers (0-127).
        @param twoHandsTup: Tuple of booleans, True if left/right hand is active.
        """
        self.root = root
        self.bpm = bpm
        self.maxNoteperBar = maxNoteperBar
        self.numberOfBars = numberOfBars
        self.noteValuesList = noteValuesList
        self.noteRange = noteRangePerHand
        self.twoHandsTup = twoHandsTup

        self.pitchesOptions = noteRangePerHandDescription

    # create Window to specify next task, root waiting until this window is closed
    def changeParameter(self):
        """
        Creates a window with options to specify the next task.
        The GUI's root waits until this windows is closed by the user.

        @return: None
        """
        self.specifyWindow = tk.Toplevel(master=self.root)

        self.specifyWindow.transient(self.root)
        self.specifyWindow.grab_set()
        self.specifyWindow.geometry("325x600")
        self.specifyWindow.title("Options for next task")

    # NOTEVALUE checkboxes
        l1 = tk.Label(self.specifyWindow, text=" Notevalues:")
        l1.grid(row=1, columnspan=4, sticky=tk.W, pady=(20, 0))

        global fullNote, halfNote, quarterNote, eighthNote, sixteenthNote

        fullNote = tk.BooleanVar()
        fullNote.set(1 in self.noteValuesList)
        chk1 = tk.Checkbutton(self.specifyWindow, text='1', var=fullNote)
        chk1.grid(column=1, row=2)

        halfNote = tk.BooleanVar()
        halfNote.set(1/2 in self.noteValuesList)
        chk1_2 = tk.Checkbutton(self.specifyWindow, text='1/2', var=halfNote)
        chk1_2.grid(column=2, row=2)

        quarterNote = tk.BooleanVar()
        quarterNote.set(1/4 in self.noteValuesList)
        chk1_4 = tk.Checkbutton(self.specifyWindow, text='1/4', var=quarterNote)
        chk1_4.grid(column=3, row=2)

        eighthNote = tk.BooleanVar()
        eighthNote.set(1/8 in self.noteValuesList)
        chk1_8 = tk.Checkbutton(self.specifyWindow, text='1/8', var=eighthNote)
        chk1_8.grid(column=4, row=2)

        sixteenthNote = tk.BooleanVar()
        sixteenthNote.set(1/16 in self.noteValuesList)
        chk1_16 = tk.Checkbutton(self.specifyWindow, text='1/16', var=sixteenthNote)
        chk1_16.grid(column=5, row=2)

    # Max NOTES per bar
        l2 = tk.Label(self.specifyWindow, text=" Maximal note number per bar:")
        l2.grid(row=3,columnspan=4, sticky=tk.W, pady=(20,0))

        OptionList = ["1","2","3","4"]
        maxNoteNumber = tk.StringVar(self.specifyWindow)
        maxNoteNumber.set(self.maxNoteperBar)

        opt = tk.OptionMenu(self.specifyWindow, maxNoteNumber, *OptionList)
        opt.grid(row=4,columnspan=4,sticky=tk.W,)

    # Number of BARS
        l3 = tk.Label(self.specifyWindow, text=" Number of bars:")
        l3.grid(row=5,columnspan=4, sticky=tk.W, pady=(20,0))

        numberBars = tk.Scale(self.specifyWindow, from_=2, to=30, orient=tk.HORIZONTAL)
        numberBars.grid(row=6, columnspan=4,sticky=tk.W,)
        numberBars.set(self.numberOfBars)

    # BEATS per minute
        l4 = tk.Label(self.specifyWindow, text=" Beats per minute:")
        l4.grid(row=7,columnspan=4, sticky=tk.W, pady=(20,0))

        bpmscale = tk.Scale(self.specifyWindow, from_=10, to=200, orient=tk.HORIZONTAL)
        bpmscale.grid(row=8, columnspan=4,sticky=tk.W,)
        bpmscale.set(self.bpm)

    # NOTEPITCHES checkboxes
        l5 = tk.Label(self.specifyWindow, text=" Notepitches:")
        l5.grid (row=9,columnspan=4,sticky=tk.W, pady=(20,0))

        global chosenpitches
        chosenpitches = tk.StringVar(self.specifyWindow)
        chosenpitches.set(self.check_pitches())
        guideopt = tk.OptionMenu(self.specifyWindow, chosenpitches, *self.pitchesOptions)
        guideopt.grid(row=10, columnspan=6, sticky=tk.W, )

    #  BOTH HANDS
        l6 = tk.Label(self.specifyWindow, text=" One or both hands:")
        l6.grid (row=12,columnspan=4,sticky=tk.W, pady=(20,0))

        global rightHand, leftHand
        rightHand = tk.BooleanVar()
        rightHand.set(self.twoHandsTup[1])
        chk = tk.Checkbutton(self.specifyWindow, text='Use right hand', var=rightHand)
        chk.grid(column=1,columnspan=3, row=13)

        leftHand = tk.BooleanVar()
        leftHand.set(self.twoHandsTup[0])
        chk = tk.Checkbutton(self.specifyWindow, text='Use left hand', var=leftHand)
        chk.grid(column=3, columnspan=3, row=13)

    # SAVE and QUIT button
        l8 = tk.Label(self.specifyWindow, text=" \n \n ")
        l8.grid(row=16, columnspan=4, sticky=tk.W)

        saveButton = tk.Button(self.specifyWindow, text='Save and quit',
                            command=lambda: self.save_settings(saveBPM=bpmscale.get(), saveBarNumber=numberBars.get(),
                                                               saveNotesPerBar=maxNoteNumber.get(),
                                                               saveRightHand=rightHand.get(), saveLeftHand=leftHand.get()))
        saveButton.grid(row=17, column=4, columnspan=3, pady=(20, 0))

        quitButton = tk.Button(self.specifyWindow, text='Quit without saving', command=lambda: self.quit_options())
        quitButton.grid(row=17, columnspan=3, pady=(20, 0))

        self.root.wait_window(self.specifyWindow)

    def get_noteValues(self):
        """
        Creates the list of user-selected note values.

        @return: List of user-selected note values.
        """
        noteValuesList = []
        if (fullNote.get() == True):
            noteValuesList.append(1)
        if (halfNote.get() == True):
            noteValuesList.append(1/2)
        if (quarterNote.get() == True):
            noteValuesList.append(1/4)
        if (eighthNote.get() == True):
            noteValuesList.append(1/8)
        if (sixteenthNote.get() == True):
            noteValuesList.append(1/16)

        return noteValuesList

    def check_pitches(self):
        """
        Matches a description to the user-selected note pitches.

        @return: Note pitches description.
        """
        
        return noteRangeMap[self.noteRange]
        

    def get_pitches(self):
        """
        Matches the user-selected note pitch description to the respective list.

        @return: Note pitches list.
        """
        
        return noteRangeMap[chosenpitches.get()]
        

    def show_empty_list_error(self):
        """
        Shows an error if no pitch or no note value has been selected.

        @return: None
        """
        l7 = tk.Label(self.specifyWindow, text=" Error: \n At least one note value and \n one hand must be selected.",
             fg = "red")
        l7.grid(row=16,column = 2, columnspan=4, sticky=tk.W)

    # save settings to generate a new task with it
    def save_settings(self, saveBPM, saveBarNumber, saveNotesPerBar, saveRightHand, saveLeftHand):
        """
        Saves the settings selected in the options window.
        Invoked when clicking the 'save' button. The options will be applied to
        the next generated task.

        @param saveBPM: Tempo (beats per minute).
        @param saveBarNumber: Total number of bars.
        @param saveNotesPerBar: Maximum number of notes that a bar can contain.
        @param saveRightHand: True for generating notes for the right hand.
        @param saveLeftHand: True for generating notes for the left hand.
        @return: None
        """
        if (saveRightHand == False and saveLeftHand == False) or not self.get_noteValues() or not self.get_pitches():
            self.show_empty_list_error()
        else:
            self.bpm = saveBPM
            self.numberOfBars = saveBarNumber
            self.maxNoteperBar = int(saveNotesPerBar)
            self.noteValuesList = self.get_noteValues()
            self.noteRange = self.get_pitches()
            self.twoHandsTup = (saveLeftHand, saveRightHand)
            self.specifyWindow.destroy()

    def quit_options(self):
        """
        Closes the options window without saving changes.

        @return: None
        """
        self.specifyWindow.destroy()

    # return all choosen options to main
    def get_data(self):
        """
        Returns all current option values.

        @return: All current option values.
        """
        return self.bpm, self.numberOfBars, self.maxNoteperBar, self.noteValuesList, self.noteRange, self.twoHandsTup
