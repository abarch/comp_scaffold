

def convertToAbsTime(midi_file):
    for i, track in enumerate(midi_file.tracks):
        print('Track {}: {}'.format(i, track.name))
        for msg in track:
            print(msg)

    # return absTime


















if __name__ == "__main__":
    import mido
    import pathlib, os
    root_directory = str(pathlib.Path(os.getcwd()).parent)
    print(root_directory)
    mid1 = mido.MidiFile(root_directory+'/data/beethoven_fur_elise.mid')
    mid1time = convertToAbsTime(mid1)
    mid2 = mido.MidiFile(root_directory+'/data/pachelbel_canon.mid')
