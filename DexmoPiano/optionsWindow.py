from tkinter import *


class optionsWindowClass():

    def __init__(self, root, bpm, maxNoteperBar, numberOfBars, noteValuesList, pitchesList, twoHandsTup):
        self.root = root
        self.bpm = bpm
        self.maxNoteperBar = maxNoteperBar
        self.numberOfBars = numberOfBars
        self.noteValuesList = noteValuesList
        self.pitchesList = pitchesList
        self.twoHandsTup = twoHandsTup

        self.pitchesOptions = ["One note (C)", "Two notes (C,D)", "Notes C-G (for 5 fingers)", "One octave",
                               "Two octaves (two hands)"]

    # create Window to specify next task, root waiting until this window is closed
    def changeParameter(self):

        self.specifyWindow = Toplevel(master = self.root)

        self.specifyWindow.transient(self.root)
        self.specifyWindow.grab_set()
        self.specifyWindow.geometry("325x600")
        self.specifyWindow.title("Options for next task")

    ## NOTEVALUE checkboxes
        l1 = Label(self.specifyWindow, text=" Notevalues:")
        l1.grid (row=1,columnspan=4,sticky=W, pady=(20,0))

        global fullNote, halfNote, quarterNote, eighthNote, sixteenthNote

        fullNote = BooleanVar()
        fullNote.set(1 in self.noteValuesList)
        chk1 = Checkbutton(self.specifyWindow, text='1', var=fullNote)
        chk1.grid(column=1, row=2)

        halfNote = BooleanVar()
        halfNote.set(1/2 in self.noteValuesList)
        chk1_2 = Checkbutton(self.specifyWindow, text='1/2', var=halfNote)
        chk1_2.grid(column=2, row=2)

        quarterNote = BooleanVar()
        quarterNote.set(1/4 in self.noteValuesList)
        chk1_4 = Checkbutton(self.specifyWindow, text='1/4', var=quarterNote)
        chk1_4.grid(column=3, row=2)

        eighthNote = BooleanVar()
        eighthNote.set(1/8 in self.noteValuesList)
        chk1_8 = Checkbutton(self.specifyWindow, text='1/8', var=eighthNote)
        chk1_8.grid(column=4, row=2)

        sixteenthNote = BooleanVar()
        sixteenthNote.set(1/16 in self.noteValuesList)
        chk1_16 = Checkbutton(self.specifyWindow, text='1/16', var=sixteenthNote)
        chk1_16.grid(column=5, row=2)

    ## Max NOTES per bar
        l2 = Label(self.specifyWindow, text=" Maximal note number per bar:")
        l2.grid(row=3,columnspan=4, sticky=W, pady=(20,0))

        OptionList = ["1","2","3","4"]
        maxNoteNumber = StringVar(self.specifyWindow)
        maxNoteNumber.set(self.maxNoteperBar)

        opt = OptionMenu(self.specifyWindow, maxNoteNumber, *OptionList)
        opt.grid(row=4,columnspan=4,sticky=W,)

    ## Number of BARS
        l3 = Label(self.specifyWindow, text=" Number of bars:")
        l3.grid(row=5,columnspan=4, sticky=W, pady=(20,0))

        numberBars = Scale(self.specifyWindow, from_=2, to=30, orient=HORIZONTAL)
        numberBars.grid(row=6, columnspan=4,sticky=W,)
        numberBars.set(self.numberOfBars)

    ## BEATS per minute
        l4 = Label(self.specifyWindow, text=" Beats per minute:")
        l4.grid(row=7,columnspan=4, sticky=W, pady=(20,0))

        bpmscale = Scale(self.specifyWindow, from_=60, to=200, orient=HORIZONTAL)
        bpmscale.grid(row=8, columnspan=4,sticky=W,)
        bpmscale.set(self.bpm)

    ## NOTEPITCHES checkboxes
        l5 = Label(self.specifyWindow, text=" Notepitches:")
        l5.grid (row=9,columnspan=4,sticky=W, pady=(20,0))

        global chosenpitches
        chosenpitches = StringVar(self.specifyWindow)
        chosenpitches.set(self.check_pitches())
        guideopt = OptionMenu(self.specifyWindow, chosenpitches, *self.pitchesOptions)
        guideopt.grid(row=10, columnspan=6, sticky=W, )

    ##  BOTH HANDS
        l6 = Label(self.specifyWindow, text=" One or both hands:")
        l6.grid (row=12,columnspan=4,sticky=W, pady=(20,0))

        global rightHand, leftHand
        rightHand = BooleanVar()
        rightHand.set(self.twoHandsTup[1])
        chk = Checkbutton(self.specifyWindow, text='Use right hand', var=rightHand)
        chk.grid(column=1,columnspan=3, row=13)

        leftHand = BooleanVar()
        leftHand.set(self.twoHandsTup[0])
        chk = Checkbutton(self.specifyWindow, text='Use left hand', var=leftHand)
        chk.grid(column=3, columnspan=3, row=13)

    ## SAVE and QUIT button
        l8 = Label(self.specifyWindow, text=" \n \n ")
        l8.grid(row=16, columnspan=4, sticky=W)

        saveButton = Button(self.specifyWindow, text='Save and quit',
                            command=lambda: self.save_settings(saveBPM=bpmscale.get(), saveBarNumber=numberBars.get(),
                                                               saveNotesPerBar=maxNoteNumber.get(),
                                                               saveRightHand=rightHand.get(), saveLeftHand=leftHand.get()))
        saveButton.grid(row=17, column=4, columnspan=3, pady=(20, 0))

        quitButton = Button(self.specifyWindow, text='Quit without saving', command=lambda: self.quit_options())
        quitButton.grid(row=17, columnspan=3, pady=(20, 0))

        self.root.wait_window(self.specifyWindow)

    # get list of choosen notevalues
    def get_noteValues(self):
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
        if(self.pitchesList == [60]):
            return "One note (C)"
        elif (self.pitchesList == [60, 62]):
            return "Two notes (C,D)"
        elif (self.pitchesList == [60, 62, 64, 65,67]):
            return "Notes C-G (for 5 fingers)"
        elif (self.pitchesList == list(range(60, 72))):
            return "One octave"
        elif (self.pitchesList == list(range(48, 72))):
            return "Two octaves (two hands)"

    # get list of choosen pitches
    def get_pitches(self):
        pitchesList = []

        if (chosenpitches.get() == "One note (C)"):
            pitchesList = [60]
        elif (chosenpitches.get() == "Two notes (C,D)"):
            pitchesList = [60, 62]
        elif (chosenpitches.get() == "Notes C-G (for 5 fingers)"):
            pitchesList = [60, 62, 64, 65,67]
        elif (chosenpitches.get() == "One octave"):
            pitchesList = list(range(60, 72))
        elif (chosenpitches.get() == "Two octaves (two hands)"):
            pitchesList = list(range(48, 72))

        return pitchesList

    # show error if no pitch or no note value is choosen
    def show_empty_list_error(self):
        l7 = Label(self.specifyWindow, text=" Error: \n At least one notevalue and \n one hand must be selected.",
             fg = "red")
        l7.grid(row=16,column = 2, columnspan=4, sticky=W)

    # save settings to generate a new task with it
    def save_settings(self, saveBPM, saveBarNumber, saveNotesPerBar, saveRightHand, saveLeftHand):
        if (saveRightHand == False and saveLeftHand == False) or not self.get_noteValues() or not self.get_pitches():
            self.show_empty_list_error()
        else:
            self.bpm = saveBPM
            self.numberOfBars = saveBarNumber
            self.maxNoteperBar = int(saveNotesPerBar)
            self.noteValuesList = self.get_noteValues()
            self.pitchesList = self.get_pitches()
            self.twoHandsTup = (saveLeftHand, saveRightHand)
            self.specifyWindow.destroy()

    # quit options window without saving settings
    def quit_options(self):
        self.specifyWindow.destroy()

    # return all choosen options to main
    def get_data(self):
        return self.bpm, self.numberOfBars, self.maxNoteperBar, self.noteValuesList, self.pitchesList, self.twoHandsTup
