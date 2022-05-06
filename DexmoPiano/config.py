from visualNotes import VisualNotes

waitThread = 0

# directory/filename strings
outputDir = './output/'
tempDir = './output/temp/'
inputFileStrs = [tempDir + 'output.mid', tempDir + 'output-m.mid', tempDir + 'output-md.mid', tempDir + 'output.xml']

current_midi = "midi_test"

str_date = ""
playing_start_time = 0
guidance_mode = ""
timestr = ""
participant_id = ""
free_text = ""

stopButton = ""

playMode = ""

vnotes = []