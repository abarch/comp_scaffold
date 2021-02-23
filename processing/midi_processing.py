def convertToAbsoluteTicks(midi_file):
    singleTrackDict = {}
    for i, track in enumerate(midi_file.tracks):
        print('Track {}: {}'.format(i, track.name))
        time = 0
        for msg in track:
            if msg.type == 'time_signature':
                pass
            elif msg.type == 'key_signature':
                pass
            elif msg.type == 'set_tempo':
                time += msg.time
            elif msg.type == 'note_off':
                time += msg.time
            elif msg.type == 'note_on':
                time += msg.time
            if time not in singleTrackDict:
                singleTrackDict[time] = []
            singleTrackDict[time].append(msg)
    print("Done")
    return singleTrackDict


if __name__ == "__main__":
    import mido
    import pathlib, os
    import processing.time_warping

    root_directory = str(pathlib.Path(os.getcwd()).parent)
    print(root_directory)
    mid1 = mido.MidiFile(root_directory + '/data/beethoven_fur_elise.mid')
    mid2 = mido.MidiFile(root_directory + '/data/pachelbel_canon.mid')
    mid3 = mido.MidiFile(root_directory + '/data/TripletsAndQuarters.mid')
    mid4 = mido.MidiFile(root_directory + '/data/TaQ-Easy.mid')
    mid5 = mido.MidiFile(root_directory + '/data/untitled.mid')
    mid6 = mido.MidiFile(root_directory + '/data/untitled1.mid')
    mid2time = convertToAbsoluteTicks(mid1)
    mid1time = convertToAbsoluteTicks(mid2)
    timestamp1 = sorted(mid1time.keys())
    timestamp2 = sorted(mid2time.keys())
    dtw = processing.time_warping.SparseDTW(timestamp2, timestamp1)
    sumval = 0
    dist = 0
    length = 0
    for coord, value in dtw():
        print(coord, '\t', timestamp2[coord[0]], timestamp1[coord[1]], '\t', value)
        dist += (timestamp2[coord[0]] - timestamp1[coord[1]])**2
        sumval += value
        length += 1
    print('DTW distance: ', sumval)
    print('Euclidean distance: ', dist**0.5)
    print('Normalised Euclidean distance: ', (dist ** 0.5)/length)
    print('Normalised DTW distance: ', sumval/length)

