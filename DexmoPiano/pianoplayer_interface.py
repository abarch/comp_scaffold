from music21 import converter
from pianoplayer.hand import Hand
from pianoplayer.scorereader import reader, PIG2Stream


# based on pianoplayer https://github.com/marcomusy/pianoplayer/blob/master/bin/pianoplayer
class PianoplayerInterface:

    def __init__(self, filename):
        self.sf = converter.parse(filename)
        self.bpm = self.sf.parts[0].metronomeMarkBoundaries()[0][2].getQuarterBPM()
        tmp = self.sf.parts[0].makeMeasures()
        self.measures = len(tmp.elements)

    # left_only whether fingering should be generated for left hand only
    # right_only whether fingering should be generated for right hand only
    # rbeam right hand beam number
    # lbeam left hand beam number
    # n_measures number of score measures to scan
    # optional depth of combinatorial search, [4-9] (default autodepth)
    # optional hand size (default M)
    def generate_fingernumbers(self, left_only, right_only, rbeam, lbeam, n_measures, depth=0, hand_size='M'):

        if not left_only:
            rh = Hand("right", hand_size)
            rh.verbose = False
            if depth == 0:
                rh.autodepth = True
            else:
                rh.autodepth = False
                rh.depth = depth
            rh.lyrics = False
            rh.handstretch = False

            rh.noteseq = reader(self.sf, beam=rbeam)
            rh.generate(1, n_measures)

        if not right_only:
            lh = Hand("left", hand_size)
            lh.verbose = False
            if depth == 0:
                lh.autodepth = True
            else:
                lh.autodepth = False
                lh.depth = depth
            lh.lyrics = False
            lh.handstretch = False

            lh.noteseq = reader(self.sf, beam=lbeam)
            lh.generate(1, n_measures)

    def get_score(self):
        return self.sf

    def get_bpm(self):
        return self.bpm

    def get_measure_number(self):
        return self.measures

    def write_output(self, outputfile):
        self.sf.write('xml', fp=outputfile)
