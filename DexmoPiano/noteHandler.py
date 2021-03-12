import time

from midiInput import adapt_noteinfo

# number of digits up to which a float is rounded
ROUND_DIGITS = 3

startTime = 0.0


def initTime():
    """
    Sets start time globally (at task initialization).

    @return: None
    """
    global startTime

    startTime = time.time()

    ###TODO: remove
    print("Start time:", startTime)


def getTime():
    """
    Returns current time in milliseconds.

    @return: Current time [ms].
    """
    return round(time.time() - startTime, ROUND_DIGITS)


def handleNote(noteType, pitch, velocity, noteInfoTemp, noteInfoList):
    """
    Handles a given MIDI note, played by the user.
    Every note is defined by two events: note_on (pressed) and note_off (released).
    The handler stores the times for every individual note. The matching is quite
    easy as both events can only occur alternately per note (at least with regular
    MIDI devices).
    Multiple (different) notes played simultaneously can also be handled.

    @param noteType: Type of the MIDI note (note_on or note_off).
    @param pitch: Pitch of the MIDI note.
    @param velocity: Velocity of the MIDI note.
    @param noteInfoTemp: Temporary list containing each possible note's current state.
    @param noteInfoList: List of all notes played by the user.
    @return: -1 for error, 0 for note_on success, noteInfo for note_off success
    """
    
    # the NoteInfo object before any updates
    note_info = noteInfoTemp[pitch]

    # store note_on time
    if noteType == 'note_on':
        # check if note_on was not set already
        if note_info.note_on_time != -1:
            print("note_on was set twice! Pitch:", pitch)
            return -1

        noteInfoTemp[pitch] = adapt_noteinfo(note_info, pitch=pitch,
                                             note_on_time=getTime(), 
                                             velocity=velocity)
        return 0

    # store note_off time and return difference
    elif noteType == 'note_off':
        # check if note_off was not set already
        if (note_info.note_on_time == -1) or (note_info.note_off_time != -1):
            print("note_off was set twice! Pitch:", pitch)
            return -1

        
        final_note_info = adapt_noteinfo(note_info,
                                         note_off_time=getTime())
        
        # reset entry
        try:
            noteInfoTemp.pop(pitch)
            # same as 
            # del noteInfoTemp[pitch]
        except KeyError:
            print("Error removing from noteInfoTemp")


        noteInfoList.append(final_note_info)
        
        return final_note_info

    else:
        print("noteType error:", noteType)
        return -1
