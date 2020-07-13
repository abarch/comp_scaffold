import time


# get current time in milliseconds
def getTime():
	return int(round(time.time() * 1000))


#TODO: documentation
def handleNote(noteType, pitch, velocity, noteInfoTemp, noteInfoList):

	# store note_on time
	if noteType == 'note_on':
		# check if note_on was not set already
		if noteInfoTemp[pitch][0] != -1:
			print("note_on was set twice! Pitch:", pitch)
			return -1
		
		noteInfoTemp[pitch] = [getTime(), -1, velocity]
		return 0
			

	# store note_off time and return difference
	elif noteType == 'note_off':
		# check if note_off was not set already
		if (noteInfoTemp[pitch][0] == -1) or (noteInfoTemp[pitch][1] != -1):
			print("note_off was set twice! Pitch:", pitch)
			return -1

		noteOffTime = getTime()
		### TODO: needed? see TODO below
		noteInfoTemp[pitch][1] = [noteOffTime]
		noteOnTime = noteInfoTemp[pitch][0]

		# reset entry
		noteInfoTemp[pitch] = [-1, -1, -1]

		noteInfo = [pitch, velocity, noteOnTime, noteOffTime]

		### TODO: remove?
		#print("NoteInfo:", noteInfo)
		#timeDiff = noteOffTime - noteOnTime

		# store noteInfo to list
		noteInfoList.append(noteInfo)
		#print(noteInfoList)

		return noteInfo
			
	else:
		print("noteType error:", noteType)
		return -1
