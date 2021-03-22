
import io
import csv
import time

import shutil
import threading
import subprocess
import pandas as pd
from pathlib import Path
from pprint import pprint
from _setup_data import openface_feature_exctraction_exe as feature_extractor_executable
from _setup_data import webcam_device_id
import matplotlib.pyplot as plt

from constants import temp_dir

openface_output_dir = temp_dir/"openface_data"

default_flags = ["-device", str(webcam_device_id),                        #selects the webcam as input
                 "-of", "main",                         #sets output filenames
                 
                 # "-vis-align",
                 "-simalign",
                 "-nomask",
                 # "-format_vis_aligned", "png",
                 
                 ]

class OpenFaceInput:
    """Class that starts and keeps track of the output of an openface FeatureExtractor"""
    
    def __init__(self):
        self.features = ["-pose", "-gaze", "-aus", "-pdmparams", "-2Dfp", "-3Dfp"] # "-gaze"
        self.exctractor = None
        self.running = False
        self.offset = None
        
        self.output_dir = openface_output_dir / time.strftime("%Y_%m_%d-%H_%M_%S")
        self.output_csv_file = self.output_dir/"main.csv"
        self.features.extend(["-out_dir", str(self.output_dir)])
        
        self.ext_stdout = list()
        
        self.callbacks = list()
        self.intermediate_dfs = list()
        
    def add_callback(self, fun):
        if self.running:
            raise Exception("Callbacks have to be added before the start() call. (Could be changed)")
        self.callbacks.append(fun)
    
    
    def _extract_offset_from_stdout(self):
        target_string = "Attempt"
        while self.offset is None:
            time_of_messages_with_target = [time for time, strlist in 
                        self.ext_stdout if target_string in "".join(strlist)]
            
            if len(time_of_messages_with_target) > 0:
                self.offset = time_of_messages_with_target[0]
                break #not strictly necessary
    
    # def _find_real_time_offset(self):
    #     self.offset = None
        
    #     while True:
    #         time.sleep(0.001)
    #         if self.output_csv_file.exists():
    #             content = self.output_csv_file.read_text()
    #             read_time = time.time()
    #             n_lines = len(content.split("\n"))
    #             if n_lines >= 2: #not just header
    #                 break
        
        
    #     # print("CONTENT")
    #     # print(content)
        
    #     header = content.splitlines()[0]
    #     first_line = content.splitlines()[-1]
    #     first_timestamp = None
    #     for field, value in zip(header.split(","), first_line.split(",")):
    #         if field == "timestamp":
    #             first_timestamp = float(value)
    #             break
        
    #     self.offset = read_time - first_timestamp
    #     print("TIMESTAMP_OFFSET:", self.offset)
    
    def _callback_handler(self):
        if len(self.callbacks) == 0:
            return
        
        last_file_pos = 0
        
        while True:
            if not self.output_csv_file.exists():
                time.sleep(0.1)
                continue
            
            # EXTRACT THE HEADER
            content = self.output_csv_file.read_text()
            if len(content) == 0:
                # print("(CBH) No information yet")
                time.sleep(0.1)
                continue
            
            header = content.splitlines()[0]
            last_file_pos = len(header) + 1 # +1 for the newline
            break
        
        while self.running:
            with open(self.output_csv_file, "r") as file:
                file.seek(last_file_pos)
                content = file.read()
            
            # read_time = time.time()
                
            if len(content) == 0:
                time.sleep(0.05)
                continue    
            
            new_lines = content.split("\n")
            full_lines = new_lines[:-1]
            if len(full_lines) == 0:
                continue
            
            new_content_length = sum(len(line)+1 for line in full_lines) #+1 for the newline
            
            # last_file_pos GET UPDATED HERE!
            last_file_pos += new_content_length
            
            buffer = io.StringIO(header+"\n" + "\n".join(full_lines))
            
            df = pd.read_csv(buffer)
            df.timestamp = df.timestamp + self.offset
            
            latency = time.time() - df.timestamp.min()
            
            self.intermediate_dfs.append(df)
            
            # print("DF_PROCESSING TOOK {:.2f}".format(time.time()-read_time))
            
            for callback in self.callbacks:
                callback(self.intermediate_dfs[-1])

        print(self.intermediate_dfs)
        # print("THREAD_CBH_DIED_"*50)
    
    def _stdout_logger(self):
        # not_init = True
        while self.running:
            # if not not_init and self.exctractor == None:
            #     break
            
            if self.exctractor == None:
                time.sleep(0.001)
                continue
            
            # not_init = False
            
            content = self.exctractor.stdout.readline()
            if content:
                self.ext_stdout.append( (time.time(), content) )
            
        # print("THREAD_STD_DIED_"*50)
            
    def make_screenshot(self):
        assert(self.running)
        
        xwininfo_output = subprocess.run(["import", "-window", "tracking result", "itest.png"])
        
        ## get window id
        xwininfo_output = subprocess.run(["xwininfo", "-name", "tracking result"], 
                                         capture_output=True).stdout
        
        # print(repr(xwininfo_output))
        
        start = xwininfo_output.find(b"id:")+3
        end = xwininfo_output.find(b'"')
        window_id = xwininfo_output[start:end].strip()
        
        print(repr(window_id))
        
        ## actually make the screenshot
        subprocess.run(["convert", b"x:"+window_id, "test.png"])
        print(b" ".join([b"convert", b"x:"+window_id, b"test.png"]))
               
    def print_errors(self, filter_common_ones=True):
        
        if self.exctractor is None:
            print("print_errors called, but there's no exctractor..")
            return
        
        stderr = self.exctractor.stderr.read()
        lines = list()
        for line in stderr.splitlines():
            # print(repr(line))
            if filter_common_ones:
                if "canberra-gtk-module" in line:
                    continue
            
            lines.append(line)
        
        if len(lines) > 0:
            print("FeatureExctractor stderr output:")
            print("\n".join(lines))
    
    def start(self):
        # if openface_output_dir.exists():
        #     shutil.rmtree(openface_output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.running = True
        self.offset = None
        self.ext_stdout = list()
        
        threading.Thread(target=self._stdout_logger).start()
        threading.Thread(target=self._extract_offset_from_stdout).start()
        
        threading.Thread(target=self._callback_handler).start()
        
        self.ext_start_time = time.time()
        self.exctractor = subprocess.Popen(
            [str(feature_extractor_executable)] + default_flags + self.features,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            bufsize=1, close_fds=True,
                   universal_newlines=True,
            
            )
        
        time.sleep(5)
        # self.print_errors() # blocks if there are no errors!!
        
    
        
    def stop(self):
        if self.exctractor:
            self.exctractor.terminate()
        
        self.print_errors()
        
        self.exctractor = None
        self.running = False
        
        return self.get_df()
        
    def get_df(self, plot=False):
        if not self.output_csv_file.exists():
            return None
        
        df = pd.read_csv(self.output_csv_file)
        df.drop(index=df.index[-1], inplace=True)
        df.timestamp = df.timestamp + self.offset #self.ext_start_time
        
        if plot:
            pose = [c for c in df.columns if "pose" in c]
            df.plot("timestamp", pose[:3])
            df.plot("timestamp", pose[3:])
            plt.show()
        
        return df
                
                
if __name__ == "__main__":
    CALLBACK_TEST = False
    
    ofi = OpenFaceInput()
    
    if CALLBACK_TEST:
        def fun(df):
            latency = time.time() - df.timestamp.min()
            print(f"NEW DATA with LATENCY {latency:.2f}s!")
            print(df.info())
            
        ofi.add_callback(fun)
    
    ofi.start()
    time.sleep(10)
    # ofi.make_screenshot()
    # time.sleep(10)
    df = ofi.stop()
    print(df)
    # pprint(ofi.ext_stdout)