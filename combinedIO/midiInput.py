import mido
import time

MAX_NOTE = 128

# initialize list of tuples for note on/off times
# index = note: [t_on, t_off, velocity]
noteTimes = [[-1, -1, -1]] * MAX_NOTE

# get current time in milliseconds
def getTime():
	return int(round(time.time() * 1000))


# organizes note on/off array
# saves on/off times (ms)
# returns: 	0 for note_on success, -1 for failure
#			time difference (note_off), -1 for failure
def noteHandler(noteType, pitch, velocity):

	# store note_on time
	if noteType == 'note_on':
		# check if note_on was not set already
		if noteTimes[pitch][0] != -1:
			print("note_on was set twice! Pitch:", pitch)
			return -1
		
		noteTimes[pitch] = [getTime(), -1, velocity]
		return 0
			

	# store note_off time and return difference
	elif noteType == 'note_off':
		# check if note_off was not set already
		if (noteTimes[pitch][0] == -1) or (noteTimes[pitch][1] != -1):
			print("note_off was set twice! Pitch:", pitch)
			return -1

		noteOffTime = getTime()
		### TODO: needed? see TODO below
		noteTimes[pitch][1] = [noteOffTime]
		noteOnTime = noteTimes[pitch][0]

		# reset entry
		noteTimes[pitch] = [-1, -1, -1]

		### TODO: remove?
		timeDiff = noteOffTime - noteOnTime
		return timeDiff
			
	else:
		print("noteType error:", noteType)
		return -1

	### TODO: velocity needed in this function?
	### TODO: maybe don't even store noteOffTime and return diff immediately?


# get keyboard input
def getMidiInput(inportName):

	inport = mido.open_input(inportName)

	while True:
		# event-triggered
		msg = inport.receive()
		#print(msg)

		if not msg.is_meta:
			if (msg.type == 'note_on') or (msg.type == 'note_off'):
				retVal = noteHandler(msg.type, msg.note, msg.velocity)
				
				if retVal > 0:
					print("Note", msg.note, "pressed for", retVal, "ms")



if __name__ == "__main__":

	#inputNames = mido.get_input_names()
	#print(inputNames)

	port = 'Q25 MIDI 1'

	### TODO: remove
	print(mido.get_output_names())

	playMidi(file, port)
	