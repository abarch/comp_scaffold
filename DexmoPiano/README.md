# Learning to play piano

This project teaches a novice to play piano through the use of various practice modes.

If there are any questions/problems feel free to contact Nina.


## Required software/packages
* Python 3.9
* python-rtmidi v1.4.1 (via PIP3, needs Debian/Ubuntu package *libjack-dev*)
* LilyPond [v2.18.2](http://lilypond.org/download/binaries/) (available in ubuntu bionic packages)
* python3-tk v3.6.9-1\~18.04 (available in ubuntu bionic packages)
* Qsynth v0.5.0-2 (available in ubuntu bionic packages) - e.g. if the keyboard does not have its own audio output
* vmpk v0.4.0-3 (available in ubuntu bionic packages) - virtual midi keyboard, if no physical one is available
* Debian/Ubuntu package *libasound-dev* might be required (if error "Cannot find alsa/asoundlib.h" occurs)

### requirements.txt
includes required python packages:
* pianoplayer v2.1.0
* MIDIUtil v1.2.1
* mido v1.2.9
* music21 v6.1.0

in order to install the packages run: 
```
$ pip3 install -r requirements.txt
```

## Prerequisites
* Properly connect keyboard/piano (the ports can be checked with the `aconnect` command)
* If used, Qsynth should be running beforehand


## Running the code
Starting the "main" program:
```
$ python3 DexmoPiano/dexmoPianoGui.py
```

## Recording data for HMM Generation
Each task is started, by clicking on *Start Task* and playing the shown piece.
1) Click on *difficulty scaling* to generate iteratively more difficult pieces and 
   play them until the system tells you to practice this piece more.
2) Play the current piece in different practice modes by clicking *Generate New Task* and then 
   the desired practice mode. For optimal learning use the following order:
   * right hand - left hand - single note - slower - identity
3) You can manually increase your complexity level by clicking *Generate New Task* and then *New Complexity Level*

Your error values and played notes are automatically saved as a csv file in folder hmm_data.


## License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.


## Background
Bachelor Thesis by Nina Ziegenbein (Bielefeld University). Large part of code is based on a previous Masters project.
