from openfaceInput import OpenFaceInput
from sklearn.tree import DecisionTreeClassifier, export_graphviz
import time
import threading
import pandas as pd
from time import sleep

beep = lambda: print("\a", end="")


class ResultVisualizer:
    def __init__(self, clf):
        self.clf = clf
        
        import tkinter as tk
        self.root = tk.Tk()
        self.root.geometry('400x300+100+100')
        
        self.start()
        
    def _analyze(self, df):
        pose_cols = [c for c in df.columns if "pose" in c]
        
        latest_datapoint = df[pose_cols].iloc[-1,:]
        
        predicted_class = self.clf.predict([latest_datapoint])[0]
        
        new_color = ["white", "red"]
        
        self.root["bg"] = new_color[predicted_class]
    
        
        
    def start(self):
        ofi = OpenFaceInput()
        ofi.add_callback(self._analyze)
        ofi.start()
        
        def kill_main():
            sleep(20)
            self.root.destroy()
        
        threading.Thread(target=kill_main).start()
        
        self.root.mainloop()
        
        ofi.stop()
        
        

def get_data(length=7, repeat=2, pause_between=3):
    global keyboard_data, screen_data
    global markers, df
    markers = list()
    
    ofi = OpenFaceInput()
    ofi.start()
    

    
    for target in ["KEYBOARD", "SCREEN"]:
        print(f"LOOK AT {target}")
        sleep(pause_between)
        
        print("GO")
        # print("\a")
        beep()
        markers.append(time.time())
        sleep(length)
        markers.append(time.time())
        
        
        beep()
        sleep(0.1)
        beep()
    
    
    sleep(2)
    df = ofi.stop()
    
    print(markers)
    
    screen_data = list()
    keyboard_data = list()
    
    # tmp_markers = markers[:]
    
    for i in range(len(markers)//4):
        s1, e1, s2, e2 = markers[i*4:(i+1)*4]
        
        
        keyboard_data.append(df[(df.timestamp > s1) & (df.timestamp < e1)])
        screen_data.append(  df[(df.timestamp > s2) & (df.timestamp < e2)])
        
    # print("SCREEN")
    for d in screen_data:
        d.plot("timestamp", "pose_Rx", title="SCREEN")
    
    # print("KEYBOARD")
    for d in keyboard_data:
        d.plot("timestamp", "pose_Rx", title="KEYBOARD")
    
    
    return keyboard_data, screen_data

def live_prediction(train_data_key, train_data_screen):
    clf = DecisionTreeClassifier(max_depth=2)
    Y = [1]*len(train_data_key) + [0]*len(train_data_screen)
    
    pose_cols = [c for c in train_data_key.columns if "pose" in c]
    
    tKEY = train_data_key[pose_cols]
    tSCREEN = train_data_screen[pose_cols]
    
    X = pd.concat([tKEY, tSCREEN])
    
    clf.fit(X, Y)
    
    export_graphviz(clf, out_file="tree.dot",
                    feature_names=pose_cols, class_names=["SCREEN", "KEYBOARD"])
    
    import subprocess
    subprocess.run("dot -Tpng tree.dot -o tree.png".split(" "))
    
    return clf
    
    
    
if __name__ == "__main__":
    # d_key, d_screen = get_data()
    clf = live_prediction(keyboard_data[0], screen_data[0])
    
    live_classifier = ResultVisualizer(clf)