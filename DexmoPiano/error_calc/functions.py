try:
    from error_calc.explanation import get_explanation
except:
    from explanation import get_explanation


##TODO make this real
from collections import namedtuple
TaskInfos = namedtuple("TaskInfos", ["bpm", "beats_per_measure"])
FAKE_TASK_INFO = TaskInfos(bpm=120, beats_per_measure=4)


def computeErrorOld(targetNoteInfoList, actualNoteInfoList,
                    openface_data=None,
                    inject_explanation=False,
                    plot=False):
    """
    Naive example for error computation.
    Adds up all milliseconds where notes where pressed in either case.
    Pitch, velocity etc. are not taken into account.

    @param targetNoteInfoList: List of notes that the user is supposed to play.
    @param actualNoteInfoList: List of notes that the user actually played.
    @return: timeSums (time sums of target and actual notes), error difference
    """
    # assert(plot==False), "dummy attr, to have same as other functions"
    # assert(inject_explanation==False), "dummy attr, to have same as other functions"
    
    timeSums = []

    for noteInfoList in [targetNoteInfoList, actualNoteInfoList]:

        tempSum = 0

        for noteInfo in noteInfoList:
            tempSum += noteInfo.note_off_time - noteInfo.note_on_time

        timeSums.append(round(tempSum, 3))

    errorDiff = round(timeSums[1] - timeSums[0], 3)

    return timeSums, errorDiff

def computeErrorLV(targetNoteInfoList, actualNoteInfoList, 
                   openface_data=None,
                   inject_explanation=True,
                   plot=False):
    
    from error_calc.mappingLevenshtein import get_mapping
    
    mapping = get_mapping(targetNoteInfoList, actualNoteInfoList)
    
    error = get_explanation(targetNoteInfoList, actualNoteInfoList, 
                            mapping,
                            task_infos=FAKE_TASK_INFO,
                            inject_explanation=inject_explanation,
                            plot=plot
                            )
    
    return error

def computeErrorEvo(targetNoteInfoList, actualNoteInfoList, 
                    openface_data=None,
                   inject_explanation=True,
                   plot=False,
                   interactive=False):
    
    from error_calc.mappingEvo import get_mapping
    
    mapping = get_mapping(targetNoteInfoList, actualNoteInfoList,
                          interactive=interactive)
    
    error = get_explanation(targetNoteInfoList, actualNoteInfoList, 
                            mapping,
                            task_infos=FAKE_TASK_INFO,
                            inject_explanation=inject_explanation,
                            plot=plot
                            )
    
    return error

    