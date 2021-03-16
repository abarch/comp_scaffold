import mido

import noteHandler as nh

from collections import namedtuple, defaultdict


NoteInfo = namedtuple("NoteInfo", ["pitch", "velocity", "note_on_time", "note_off_time"])
empty_noteinfo = lambda: NoteInfo(-1,-1,-1,-1)

def adapt_noteinfo(source, pitch=None, note_on_time=None, note_off_time=None,
                   velocity=None):
    d = source._asdict()
    for var, name in [(pitch, "pitch"), (note_on_time, "note_on_time"), 
                       (note_off_time, "note_off_time"), (velocity, "velocity")]:
        if var is not None:
            d[name] = var
    
    return NoteInfo(**d)
                     
                       

class MidiInputThread():
    """
    Class for handling input from a connected MIDI device, e.g. a keyboard.
    """

    ###TODO: remove
    testPort = ""

    def __init__(self):
        """
        Initializes necessary variables and note lists/arrays.

        @param tempSize: Number of possible MIDI notes (usually 128).
        """
        #threading.Thread.__init__(self)
        self.inport = None
        # initialize note array and list
        self.noteInfoList = []
        self.noteInfoTemp = defaultdict(empty_noteinfo)

        # only handle input if true
        self.handleInput = False

        self.noteCounter = 1


    def setPort(self, portName):
        """
        Updates the MIDI input port by closing the old one (if it exists)
        and opening the new one.

        @param portName: New MIDI port.
        @return: None
        """
        ###TODO: remove
        global testPort

        # close old MIDI input port (if it exists)
        try:
            #print("Trying to close port", testPort)
            self.inport.close()
            #print("Port closed")
        except:
            pass

        # open new MIDI input port and install callback
        # (callback is necessary to avoid blocking after port changes)
        try:
            self.inport = mido.open_input(portName, callback=self.handleMidiInput)
        except IOError as e:
            print(e)

        ###TODO FOR TESTING
        testPort = portName


    # handle MIDI input message (callback function of input port)
    def handleMidiInput(self, msg):
        """
        Handle MIDI input message.
        This function was installed as a callback of the input port to avoid polling
        and starvation.

        @param msg: Input MIDI message.
        @return: None
        """
        global testPort

        #print("current input port:", testPort)

        if self.handleInput:

            if not msg.is_meta:
                if (msg.type == 'note_on') or (msg.type == 'note_off'):

                    # handle note
                    noteInfo = nh.handleNote(msg.type, msg.note, msg.velocity,
                                             self.noteInfoTemp, self.noteInfoList)

                    if type(noteInfo) == list:
                        print("ACTUAL:", self.noteCounter, "\t", noteInfo)
                        self.noteCounter += 1


    ###TODO: needed?
    def resetArrays(self):
        """
        Resets the target note arrays.

        @return: None
        """
        self.noteInfoList = []
        self.noteInfoTemp.clear()

    def inputOn(self):
        """
        Activates the input handler.

        @return: None
        """
        self.handleInput = True

    def inputOff(self):
        """
        Deactivates the input handler.

        @return: None
        """
        self.handleInput = False


if __name__ == "__main__":
    ###TODO: remove? (just needed for testing)

    # port = 'Q25 MIDI 1'
    port = 'VMPK Output:out 130:0'
    testMode = True

    # print available MIDI input ports
    print(mido.get_input_names())
