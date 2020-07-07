from mido import MidiFile

for msg in MidiFile('output.mid'):
	# only take non-meta messages
	if not msg.is_meta:
		if msg.channel == 0:
			print(msg)
		mType = msg.type

		if not mType == 'program_change':
			mChannel = msg.channel
			mNote = msg.note
			mVelo = msg.velocity
			mTime = msg.time
			print(mType, mChannel, mNote, mVelo, mTime)
			
		else:
			print("\n")


	#time.sleep(msg.time)
	#if not msg.is_meta:
		#port.send(msg)

	#print(msg)
