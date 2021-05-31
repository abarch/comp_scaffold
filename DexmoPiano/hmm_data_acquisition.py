import csv
from datetime import datetime


def save_hmm_data(errorVec, errorVecLeft, errorVecRight, task_data, taskParameters, note_errorString):
    """
    Prints the error (observations) for the hmm into the file.
    Prints note specific errors into another file.
    """

    date = datetime.today().strftime('%Y-%m-%d')
    error_file = f"./hmm_data/{date}_error.csv"
    notes_file = f"./hmm_data/{date}_notes.csv"

    if task_data.notes_left == []:
        hand = "right"
    elif task_data.notes_right == []:
        hand = "left"
    else:
        hand = "both"
    complexityLevel = [task_data.note_range, taskParameters.noteValues, hand]

    ef = open(error_file, 'a', newline='')
    ef_writer = csv.writer(ef, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    ef_writer.writerow([complexityLevel, errorVecRight, errorVec])  # task_data is a placeholder
    ef.close()

    nf = open(notes_file, 'a', newline='')
    nf_writer = csv.writer(nf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    nf_writer.writerow(note_errorString)
    nf.close()