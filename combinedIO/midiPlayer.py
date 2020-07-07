# make sure to run Qsynth at the right setup!

import mido
from mido import MidiFile

import time


###TODO: compute note timings (-> ms) like in noteHandler
### (see also midiGenerator/test.py)
def noteHandler():
	print("...handling note...")

# just plays the whole midi file
###TODO: remove?
def playMidiOnly(fileName, outportName):
	outport = mido.open_output(outportName)

	for msg in MidiFile(fileName).play():

		# filter channel (e.g. play Piano notes only)
		###TODO: decide by argument?
		if msg.channel == 0:
			outport.send(msg)


# plays the midi file while handling its notes
# (for comparing etc.)
def playMidi(fileName, outportName):
	outport = mido.open_output(outportName)

	for msg in MidiFile(fileName):
		print(msg)
		

		if not msg.is_meta:
			time.sleep(msg.time)

			# filter channel (e.g. play Piano notes only)
			###TODO: decide by argument?
			if msg.channel == 0:
				# send midi message to port (i.e. play note)
				outport.send(msg)

				# handle note
				###TODO: implement!
				noteHandler()
	


if __name__ == "__main__":

	file = '../midiGenerator/output.mid'
	port = 'Synth input port (qsynth:0)'

	### TODO: remove
	print(mido.get_output_names())

	playMidi(file, port)
