from visualNotes import VisualNotes

waitThread = 0

# directory/filename strings
outputDir = './output/'
tempDir = './output/temp/'
inputFileStrs = [tempDir + 'output.mid', tempDir + 'output-m.mid', tempDir + 'output-md.mid', tempDir + 'output.xml']

currentMidi = "midi_test"

str_date = ""
playing_start_time = 0
guidanceMode = ""
timestr = ""
participant_id = ""
freetext = ""

stopButton = ""

playMode = ""

vnotes = []