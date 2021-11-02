import matplotlib.pyplot as plt
from midiInput import MidiInputThread
from openfaceInput import OpenFaceInput
import time

def test_midi_latency(n_tries=3, countdown=4, pause=1.0):
    target_times = list()
    start_time = time.time()
    
    mit = MidiInputThread()
    mit.inputOn()
    
    for t in range(n_tries):
        for cd in range(countdown):
            cd = countdown - cd - 1
            print('\a')
            if cd == 0:
                print("PRESS NOW")
                target_times.append(time.time())
            else:
                print(f"PRESS ONE KEY IN {cd}")
            time.sleep(pause)
                
    mit.inputOff()
    
    print(target_times)
    print(mit.noteInfoList)
    real_times = [t[2] for t in mit.noteInfoList]
    
    for t in target_times:
        plt.axvline(x=t-start_time, color="k")
    for t in real_times:
        plt.axvline(x=t-start_time, color="r")
    plt.show()
    
    for target, real in zip(target_times, real_times):
        print(real - target)
                
        
"""ofi = OpenFaceInput()
    ofi.start()
    time.sleep(10)
    ofi.stop()"""        

def test_openface_latency(n_tries=3, countdown=4, pause=1.0):
    global df, start_time, target_times
    
    target_times = list()
    start_time = time.time()
    
    mit = OpenFaceInput()
    mit.start() 
    print('\a')
    time.sleep(4)
    
    for t in range(n_tries):
        for cd in range(countdown):
            cd = countdown - cd - 1
            print('\a')
            if cd == 0:
                print("PRESS NOW")
                target_times.append(time.time())
            else:
                print(f"PRESS ONE KEY IN {cd}")
            time.sleep(pause)
                
    df = mit.stop()
    
    # plt.figaspect(size=(1600,900))
    fig, sub_axes = plt.subplots(1,n_tries, figsize=(14,4))
    # fig.xlabel("Time [s]")
    for ax, target in zip(sub_axes, target_times):
        # target = target - start_time
        ax.set_xlim([-0.5, 0.5])
        ax.axvline(x=0, color="k")
        
        ax.plot(df.timestamp-target, df.pose_Rx, "o-")
        # ax.plot(df.timestamp-target, (df.timestamp-target).diff(), "o-")
        ax.set(xlabel='Time [s]')
    
    # for t in target_times:
    #     plt.axvline(x=t-start_time, color="k")
        
    # # times = df.timestamp-start_time
    # plt.plot(df.timestamp-start_time, df.pose_Rx)
    # # for t in real_times:
    # #     plt.axvline(x=t-start_time, color="r")
    # plt.show()
    
    # plt.plot(df.timestamp-start_time, df.pose_Rx.diff())
    # plt.show()
    
    # # for target, real in zip(target_times, real_times):
    # #     print(real - target)

if __name__ == "__main__":
    # test_midi_latency()
    test_openface_latency()
    
    
    