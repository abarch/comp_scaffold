from visualNotes import VisualNotes

waitThread = 0

# directory/filename strings
outputDir = './output/'
tempDir = './output/temp/'
inputFileStrs = [tempDir + 'output.mid', tempDir + 'output-m.mid', tempDir + 'output-md.mid', tempDir + 'output.xml']

currentMidi = "midi_test"

str_date = ""
playing_start_time = 0
guidanceMode = "At every note"
#guidanceMode = ""
timestr = ""
participant_id = ""
freetext = ""
expMode = ""
trial_num = 1
task_num = 0
diff_rating = "None"
performance_rating = "None"

fromFile = False #indicates if the task is from file.
loadedFileName = "" # the loaded file name
savedFileName = "" # the file of the saved data of the run task.

stopButton = ""

playMode = ""

vnotes = []