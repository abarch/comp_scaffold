def computeError(targetNoteInfoList, actualNoteInfoList):
	"""
	Naive example for error computation.
	Adds up all milliseconds where notes where pressed in either case.
	Pitch, velocity etc. are not taken into account.

	@param targetNoteInfoList: List of notes that the user is supposed to play.
	@param actualNoteInfoList: List of notes that the user actually played.
	@return: timeSums (time sums of target and actual notes), error difference
	"""
	timeSums = []

	for noteInfoList in [targetNoteInfoList, actualNoteInfoList]:

		tempSum = 0

		for noteInfo in noteInfoList:
			tempSum += noteInfo.note_off_time - noteInfo.note_on_time

		timeSums.append(round(tempSum, 3))

	errorDiff = round(timeSums[1] - timeSums[0], 3)

	return timeSums, errorDiff
