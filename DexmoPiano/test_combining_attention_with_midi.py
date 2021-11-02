from openface_data_acquisition import train_classifier_on_saved
from test_openface_tree_classification import ResultVisualizer
import time
import matplotlib.pyplot as plt
from midiInput import MidiInputThread
import numpy as np

if __name__ == "__main__":

    
    clf, class_labels, preprocess = train_classifier_on_saved()
    
    mit = MidiInputThread()
    mit.inputOn()
    
    
    
    live_classifier = ResultVisualizer(clf, class_labels, preprocess)
    mit.inputOff()
    ## RV blocks
    
    df = live_classifier.df.loc[:len(live_classifier.df)-2,:]
    
    X = preprocess(df)
    print(X)
    prediction = clf.predict_proba(X)
    
    
    ax1 = plt.subplot(313)
    
    for i, target in enumerate(class_labels):
        # plt.scatter(df.timestamp, [i]*len(prediction[:,i]), s=prediction[:,i]*10,
        #             label=target)
        plt.plot(df.timestamp, prediction[:,i],
                    label=target)
        
    plt.legend()
    plt.ylabel("Class Probability")
    
    ax3 = plt.subplot(312, sharex=ax1)
    
    top_class = np.argmax(prediction, axis=1)
    for i, target in enumerate(class_labels):
        plt.scatter(df.timestamp[top_class==i], [0]*len(df.timestamp[top_class==i]),
                     label=target)
    
    plt.legend()
    ax2 = plt.subplot(311, sharex=ax1)
    for note in mit.noteInfoList:
        print(note)
        pitch, vel, start, stop = note
        plt.plot([start,stop], [pitch, pitch], c="k")
    
    
    plt.show()
    # print(type(prediction))