from midiutil.MidiFile import MIDIFile

import random

# some code taken from https://github.com/Michael-F-Ellis/tbon

def generateMidi(bpm=120,
				 noteValues=[1, 1/2, 1/4, 1/8],
				 notesPerBar=[1],	# range
				 noOfBars=8,
				 pitches=[60, 62, 64, 65, 67, 69, 71, 72]):


	### CONSTANTS ###

	CHANNEL_PIANO = 0
	CHANNEL_METRO = 9

	INSTRUM_PIANO = 0
	INSTRUM_DRUMS = 9

	PITCH_METRO_HI = 76		# high wood block
	PITCH_METRO_LO = 77		# low wood block

	VOLUME = 100	### change?

	TIME = 0    			# start at the beginning

	INTRO_BARS = 1			# no. of empty first bars for metronome intro

	ACROSS_BARS = 0			# allow notes to reach across two bars


	### INITIALIZATION ###

	# create MIDI object
	mf = MIDIFile(numTracks=2)     # music and metronome track

	#TODO: make constant?
	muTrack = 0   # music track
	meTrack = 1	  # metronome track

	mf.addTrackName(muTrack, TIME, "Piano")
	mf.addTrackName(meTrack, TIME, "Metronome")

	mf.addTempo(muTrack, TIME, bpm)


	### EXERCISE GENERATION ###

	# time signature (ex. 4/4 = (4, 4))
	#TODO: USE AS INPUT?
	timeSig = (4, 4)

	numerator = timeSig[0]
	denominator = timeSig[1]
	# map denominator to power of 2 for MIDI
	midiDenom = {2:1, 4:2, 8:3, 16:4}[denominator]

	# adjust no. of bars (in case of intro bars)
	bars = noOfBars + INTRO_BARS


	# make the midi metronome match beat duration
	# (requires recognizing compound meters)
	if denominator == 16 and (numerator % 3 == 0):
		metro_clocks = 18
	elif denominator == 16:
		metro_clocks = 6
	elif denominator == 8 and (numerator % 3 == 0):
		metro_clocks = 36
	elif denominator == 8:
		metro_clocks = 12
	elif denominator == 4:
		metro_clocks = 24
	elif denominator == 2:
		metro_clocks = 48

	mf.addTimeSignature(track=muTrack,
						time=TIME,
						numerator=numerator,
						denominator=midiDenom,
						clocks_per_tick=metro_clocks)


	### CHOOSE TIMESTEPS ###

	timesteps = []

	# randomly generate the chosen number of timesteps (notes) per bar
	for bar in range(noOfBars):
		# determine no. of notes in this bar
		noOfNotes = random.choice(notesPerBar)

		# shift step numbers
		shift = (bar + INTRO_BARS) * numerator
		steps = [temp + shift for temp in range(numerator)]

		timesteps.append(random.sample(steps, noOfNotes))

	# flatten and sort list
	timesteps = sorted([item for sublist in timesteps for item in sublist])

	# append dummy element to avoid additional bar
	timesteps.append(bars * numerator)

	#print("timesteps:", timesteps[:-1])


	### ADD NOTES ###

	# add music (piano) notes
	mf.addProgramChange(muTrack, CHANNEL_PIANO, TIME, INSTRUM_PIANO)

	for t in range(len(timesteps) - 1):
		# compute maximum note length until next note
		maxNoteVal = (timesteps[t + 1] - timesteps[t]) / denominator
		###temp = maxNoteVal

		# compute maximum note length until next bar
		if not ACROSS_BARS:
			maxToNextBar = 1 - ((timesteps[t] % denominator) / denominator)
			maxNoteVal = min([maxNoteVal, maxToNextBar])

		###print(timesteps[t], "min(", temp, maxToNextBar, ") =", maxNoteVal)

		#TODO: multiply with timeSig[1] here (instead below) when not printing anymore
		duration = random.choice([v for v in noteValues if v <= maxNoteVal])
		#print(duration, "\n")

		pitch = random.choice(pitches)
		mf.addNote(	track=muTrack,
					channel=CHANNEL_PIANO,
					pitch=pitch,
					time=timesteps[t],
					duration=denominator * duration,
					volume=VOLUME)


	# add metronome notes
	mf.addProgramChange(meTrack, CHANNEL_METRO, TIME, INSTRUM_DRUMS)

	for t in range(bars * numerator):

		# decide if downbeat or 'other' note
		if (t % numerator) == 0:
			# first beat in bar
			pitch = PITCH_METRO_HI
		else:
			pitch = PITCH_METRO_LO

		mf.addNote(	track=meTrack,
					channel=CHANNEL_METRO,
					pitch=pitch,
					time=t,
					duration=1,
					volume=VOLUME)


	# write MIDI file
	with open("./output/output.mid", 'wb') as outf:
	    mf.writeFile(outf)


if __name__ == "__main__":
	generateMidi()
