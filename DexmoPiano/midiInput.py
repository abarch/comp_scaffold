import mido

import noteHandler as nh


class MidiInputThread():

    ###TODO: remove
    testPort = ""

    def __init__(self, tempSize):
        #threading.Thread.__init__(self)
        self.inport = None
        self.tempSize = tempSize
        # initialize note array and list
        self.noteInfoList = []
        self.noteInfoTemp = [[-1, -1, -1]] * self.tempSize

        # only handle input if true
        self.handleInput = False

        self.noteCounter = 1


    # close old and open new MIDI input port
    def setPort(self, portName):
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
        self.noteInfoList = []
        self.noteInfoTemp = [[-1, -1, -1]] * self.tempSize

    # activate input handler
    def inputOn(self):
        self.handleInput = True

    # deactivate input handler
    def inputOff(self):
        self.handleInput = False


if __name__ == "__main__":
    ###TODO: remove? (just needed for testing)

    # port = 'Q25 MIDI 1'
    port = 'VMPK Output:out 130:0'
    testMode = True

    # print available MIDI input ports
    print(mido.get_input_names())
