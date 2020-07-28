import mido
import threading
import time

import noteHandler as nh

###TODO: remove? needed for testing
testMode = False


class MidiInputThread(threading.Thread):

	def __init__(self, inportName, tempSize):
		threading.Thread.__init__(self)
		self.inportName = inportName
		self.tempSize = tempSize
		# initialize note array and list
		self.noteInfoList = []
		self.noteInfoTemp = [[-1, -1, -1]] * self.tempSize


	# target function of the thread class
	def run(self):
		# only handle input if true
		self.handleInput = False

		# start keyboard input handler
		self.getMidiInput()


	# get keyboard input
	def getMidiInput(self):
		# open MIDI input port
		inport = mido.open_input(self.inportName)

		###TODO: remove? needs to be reset after each run!
		noteCounter = 1

		while True:

			# event-triggered
			msg = inport.receive()

			###TODO: after removing testMode: enclose code below instead continuing
			if not self.handleInput:
				continue

			###TODO: remove? needed for testing
			if not testMode:

				if not msg.is_meta:
					if (msg.type == 'note_on') or (msg.type == 'note_off'):

						# handle note
						noteInfo = nh.handleNote(msg.type, msg.note, msg.velocity,
												 self.noteInfoTemp, self.noteInfoList)

						if type(noteInfo) == list:
							print("ACTUAL:", noteCounter, "\t", noteInfo)
							noteCounter += 1

						#if retVal > 0:
							#print("Note", msg.note, "pressed for", retVal, "ms")

			else:
				# just print all incoming MIDI messages
				print(msg)


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

	#port = 'Q25 MIDI 1'
	port = 'VMPK Output:out 130:0'
	testMode = True

	# print available MIDI input ports
	print(mido.get_input_names())

	# this will just print all incoming MIDI messages
	#getMidiInput(port, [], [])
