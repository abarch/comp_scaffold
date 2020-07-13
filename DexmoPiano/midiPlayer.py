# make sure to run Qsynth at the right setup!

import mido
from mido import MidiFile

import time

import noteHandler as nh


# plays the midi file while handling its notes
# (for comparing etc.)
def playMidi(fileName, outportName, noteInfoTemp, noteInfoList):
	# open MIDI output port
	outport = mido.open_output(outportName)

	###TODO: remove?
	noteCounter = 1

	for msg in MidiFile(fileName):
		#print(msg)

		if not msg.is_meta:
			# do not play all notes at once
			time.sleep(msg.time)

			###TODO: remove? or change at least? see below, channel etc!
			if msg.channel == 0:
				if (msg.type == 'note_on') or (msg.type == 'note_off'):
					# handle note
					noteInfo = nh.handleNote(msg.type, msg.note, msg.velocity,
							  				 noteInfoTemp, noteInfoList)

					if type(noteInfo) == list:
						print("TARGET:", noteCounter, "\t", noteInfo)
						noteCounter += 1



			# filter channel (e.g. play Piano notes only)
			###TODO: decide by argument?
			#if msg.channel == 0:
				# send midi message to port (i.e. play note)
			outport.send(msg)




if __name__ == "__main__":

	print("Not meant to be executed directly!")
