import mido
import time

import noteHandler as nh

###TODO: remove? needed for testing
testMode = False

# get keyboard input
def getMidiInput(inportName, noteInfoTemp, noteInfoList):
	# open MIDI input port
	inport = mido.open_input(inportName)

	###TODO: remove?
	noteCounter = 1

	while True:

		# event-triggered
		msg = inport.receive()

		###TODO: remove? needed for testing
		if not testMode:

			if not msg.is_meta:
				if (msg.type == 'note_on') or (msg.type == 'note_off'):
				
					# handle note
					noteInfo = nh.handleNote(msg.type, msg.note, msg.velocity,
											 noteInfoTemp, noteInfoList)

					if type(noteInfo) == list:
						print("ACTUAL:", noteCounter, "\t", noteInfo)
						noteCounter += 1
		
					#if retVal > 0:
						#print("Note", msg.note, "pressed for", retVal, "ms")

		else:
			# just print all incoming MIDI messages
			print(msg)



if __name__ == "__main__":

	###TODO: remove? (just needed for testing)

	port = 'Q25 MIDI 1'
	testMode = True

	# print available MIDI input ports
	print(mido.get_input_names())

	# this will just print all incoming MIDI messages
	getMidiInput(port, [], [])
	