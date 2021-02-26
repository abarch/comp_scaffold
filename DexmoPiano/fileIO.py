import xml.etree.ElementTree as ET
from xml.dom import minidom


def createXML(path, midiPrefix, options, targetNotes):
    """
    Creates a new XML tree containing the necessary nodes.

    @param path: Directory of the XML file.
    @param midiPrefix: Prefix of the XML file (i.e. timestamp).
    @param options: Current task's options set by the user.
    @param targetNotes: List of notes that the user is supposed to play.
    @return: None
    """

    root = ET.Element("MIDI", midiNo=midiPrefix)

    targets = ET.SubElement(root, "target_notes")
    ET.SubElement(targets, "notes", name="Note List").text = str(targetNotes)
    ET.SubElement(targets, "options", name="Option List").text = str(options)

    ET.SubElement(root, "trials")

    tree = ET.ElementTree(root)
    tree.write(path + midiPrefix + ".xml")


def createTrialEntry(path, midiPrefix, timestamp, guidanceMode, actualNotes, error):
    """
    Creates a new trial entry in an existing XML file.
    The trial number will be the file's current max trial number plus one.

    @param path: Directory of the XML file.
    @param midiPrefix: Prefix of the XML file (i.e. timestamp).
    @param timestamp: Timestamp of the trial.
    @param guidanceMode: Guidance Mode (Dexmo) used for the task.
    @param actualNotes: List of notes that the user actually played in the trial.
    @param error: Computed error value.
    @return: None
    """

    # parse XML file
    file = path + midiPrefix + ".xml"
    try:
        tree = ET.parse(file)
    except:
        print("Cannot open", file)
        return None

    root = tree.getroot()
    trials = root.find("trials")

    trialNo = len(trials.getchildren()) + 1

    trial = ET.SubElement(trials, "trial", trial_no=str(trialNo), timestamp=str(timestamp))
    ET.SubElement(trial, "notes", name="Played Notes").text = str(actualNotes)
    ET.SubElement(trial, "guidance", name="Guidance Mode").text = str(guidanceMode)
    ET.SubElement(trial, "error", name="Error value").text = str(error)

    tree.write(file)


###TODO: remove?
def prettifyXML(elem):
    """
    Returns a pretty-printed XML string for the Element.

    @param elem: Element of the XML tree.
    @return: Pretty-printed XML string for the Element.
    """
    rough_string = ET.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")


###TODO: remove?
def printXML(filepath, pretty):
    """
    Prints a given XML file, either directly or prettified (formatted).

    @param filepath: Path of the XML file.
    @param pretty: True for having the output prettified.
    @return: None
    """

    tree = ET.parse(filepath)
    root = tree.getroot()

    if pretty:
        print(prettifyXML(root))
    else:
        print(ET.tostring(root))



if __name__ == "__main__":

    outpath = "./output/"
    midiPrefix = "midi001"   # without .mid
    outfile = outpath + midiPrefix + ".xml"
    options = [1, True, "bla"]
    targetNotes = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
    actualNotes = [[11, 22, 33, 44], [55, 66, 77, 88], [99, 0, 0, 0]]

    createXML(outpath, midiPrefix, options, targetNotes)
    printXML(outfile, True)
    print("\n\n")
    createTrialEntry(outpath, midiPrefix, "01-11-1999", "guidance1", actualNotes, "123")
    createTrialEntry(outpath, midiPrefix, "22-02-2222", "guidance2", actualNotes, "42.666")
    printXML(outfile, True)