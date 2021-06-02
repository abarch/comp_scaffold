# placeholder till code is implemented or adopted properly
import mido
from utils.file_sys import getTime
from utils.custom_logger import
from collections import namedtuple


NoteInfo = namedtuple("NoteInfo", ["pitch", "velocity", "note_on_time", "note_off_time"])
'''
This is a proprietary message type used to store midi messages 'note_on' and 'note_off' by converting them into messages
that can be processed more easily by neural networks and/or other modules of the program. The main purpose is to convert
midi ticks, which can have a variable length to a more standard time measurement system and encode both note on and off
events in the same message. An empty note information would be encoded as follows.
    
    empty_noteinfo = lambda: NoteInfo(-1,-1,-1,-1)

'''

def adaptNoteInfo(source, pitch=None, note_on_time=None, note_off_time=None, velocity=None):
    pass



def handleNote(note_type, pitch, velocity, note_info_temp, note_info_list, timeFunc=getTime):
    """
    Handles a given MIDI note, played by the user.
    Every note is defined by two events: note_on (pressed) and note_off (released).
    The handler stores the times for every individual note. The matching is quite
    easy as both events can only occur alternately per note (at least with regular
    MIDI devices).
    Multiple (different) notes played simultaneously can also be handled.

    @param note_type: Type of the MIDI note (note_on or note_off).
    @param pitch: Pitch of the MIDI note.
    @param velocity: Velocity of the MIDI note.
    @param noteInfoTemp: Temporary list containing each possible note's current state.
    @param note_info_list: List of all notes played by the user.
    @param timeFunc: Function that returns the (absolute) time of the event.
    @return: -1 for error, 0 for note_on success, noteInfo for note_off success
    """

    # the NoteInfo object before any updates
    note_info = note_info_temp[pitch]

    # store note_on time
    if note_type == 'note_on' and velocity > 0:  # in some keyboards return 0 velocity instead of 'note_off'.
        # check if note_on was not set already
        if note_info.note_on_time != -1:
            logger.error(f"note_on was set twice! Pitch: {pitch} | {(note_type, pitch, velocity)}")
            return -1

        note_info_temp[pitch] = adaptNoteInfo(note_info, pitch=pitch,note_on_time=timeFunc(), velocity=velocity)
        return 0

    # store note_off time and return difference
    elif note_type == 'note_off' or (note_type == 'note_on' and velocity == 0):
        # check if note_off was not set already
        if (note_info.note_on_time == -1) or (note_info.note_off_time != -1):
            logger.error(f"note_on was set twice! Pitch: {pitch} | {(noteType, pitch, velocity)}")
            return -1

        final_note_info = adapt_noteinfo(note_info,
                                         note_off_time=timeFunc())

        # reset entry
        try:
            noteInfoTemp.pop(pitch)
            # same as
            # del noteInfoTemp[pitch]
        except KeyError:
            print("Error removing from noteInfoTemp")

        note_info_list.append(final_note_info)

        return final_note_info

    else:
        print("noteType error:", noteType)
        return -1

