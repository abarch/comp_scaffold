import mido

import noteHandler as nh

class MidiOutputThread():

    ###TODO: remove
    testPort = ""

    def __init__(self, tempSize):
        #threading.Thread.__init__(self)
        self.outport = None
        self.tempSize = tempSize
        # initialize note array and list
        self.noteInfoList = []
        self.noteInfoTemp = [[-1, -1, -1]] * self.tempSize

        # only handle output if true
        self.handleOutput = False

        self.noteCounter = 1


    # close old and open new MIDI output port
    def setPort(self, portName):
        ###TODO: remove
        global testPort

        # close old MIDI output port (if it exists)
        try:
            #print("Trying to close port", testPort)
            self.outport.close()
            #print("Port closed")
        except:
            pass

        # open new MIDI output port and install callback
        # (callback is necessary to avoid blocking after port changes)
        try:
            print("Trying to open output port " + portName)
            self.outport = mido.open_output(portName, callback=self.handleMidiOutput)
        except IOError as e:
            print(e)

        ###TODO FOR TESTING
        testPort = portName
        print("Opened output port " + portName)

 
    # handle MIDI output message (callback function of output port)
    def handleMidiOutput(self, msg):
        global testPort
        print("current output port:", testPort)

        if self.handleOutput:

            if not msg.is_meta:
                if (msg.type == 'note_on') or (msg.type == 'note_off'):

                    # handle note
                    noteInfo = nh.handleNote(msg.type, msg.note, msg.velocity,
                                             self.noteInfoTemp, self.noteInfoList)

                    if type(noteInfo) == list:
                        print("ACTUAL:", self.noteCounter, "\t", noteInfo)
                        self.noteCounter += 1

    def playMidi(self,filename,guidance):
        mid = mido.MidiFile(filename)
        for msg in mid.play():
            self.outport.send(msg)

    ###TODO: needed?
    def resetArrays(self):
        self.noteInfoList = []
        self.noteInfoTemp = [[-1, -1, -1]] * self.tempSize

    # activate output handler
    def outputOn(self):
        self.handleOutput = True

    # deactivate output handler
    def outputOff(self):
        self.handleOutput = False


if __name__ == "__main__":
    ###TODO: remove? (just needed for testing)

    # port = 'Q25 MIDI 1'
    port = 'VMPK Output:out 130:0'
    testMode = True

    # print available MIDI input ports
    print(mido.get_output_names())
