import copy
import csv
from collections import namedtuple
from datetime import datetime

import pandas as pd


def save_hmm_data(errorVecLeft, errorVecRight, task_data, taskParameters, note_errorString):
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
    complexityLevel = (task_data.note_range, taskParameters.noteValues, hand)


    #ef = open(error_file, 'a', newline='')
    #ef_writer = csv.writer(ef, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    #ef_writer.writerow([task_data.practice_mode, complexityLevel, errorVecRight, errorVecLeft])
    #ef.close()

    nf = open(notes_file, 'a', newline='')
    nf_writer = csv.writer(nf, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
    nf_writer.writerow(note_errorString)
    nf.close()

    dic_error = {}
    dic_error['practice_mode'] = task_data.practice_mode
    dic_error['complexityLevel'] = str(complexityLevel)
    for hand in ['_right', '_left']:
        if hand == '_right':
            error = errorVecRight
        else:
            error = errorVecLeft
        dic_error['pitch'+hand] = error.pitch
        dic_error['note_hold_time'+hand] = error.note_hold_time
        dic_error['timing'+hand] = error.timing
        dic_error['n_missing_notes'+hand] = error.n_missing_notes
        dic_error['n_extra_notes'+hand] = error.n_extra_notes
        dic_error['Summed'+hand] = error.pitch + error.note_hold_time + error.timing + error.n_missing_notes + error.n_extra_notes

    print("5", errorVecRight)
    print("dic", dic_error)
    df = pd.Series(dic_error)
    print("df", df)
    df.to_csv(error_file, mode='a', header=False, index=False)

    #thresholds(df_error)
    return df

def get_number(string, value):
    end = string.partition(value + "=")[2]
    num = end.partition(",")[0]
    return float(num)

def preprocessing(filename):
    df = pd.read_csv(filename, sep=',', header=None)
    values = ["pitch", "note_hold_time", "timing", "n_missing_notes", "n_extra_notes"]

    for hand in range(2):
        numbers = [[], [], [], [], []]
        for index, row in df.iterrows():
            error = row[hand + 1]
            for i in range(len(values)):
                numbers[i].append(get_number(error, values[i]))
        for i in range(len(values)):
            if hand == 0:
                hand_name = "_right"
            else:
                hand_name = "_left"
            df[values[i] + hand_name] = numbers[i]

    last_comp = df.iloc[0, 0]
    complexity_level = 1
    complexity = []
    for index, row in df.iterrows():
        if row[0] != last_comp:
            last_comp = row[0]
            complexity_level += 1
        complexity.append(complexity_level)
    df["ComplexityLevel"] = complexity

    df.drop([0, 1, 2], axis=1, inplace=True)

    # move complexity level to front
    cols = df.columns.tolist()
    cols = cols[-1:] + cols[:-1]
    df = df[cols]

    # compute summed error values
    sum_left = []
    sum_right = []
    for index, row in df.iterrows():
        summed_left = 0
        summed_right = 0
        for i in range(1, len(row)):
            if i < 6:
                summed_right += row[i]
            else:
                summed_left += row[i]
        sum_right.append(summed_right)
        sum_left.append(summed_left)
    df["SummedLeft"] = sum_left
    df["SummedRight"] = sum_right

    return df

