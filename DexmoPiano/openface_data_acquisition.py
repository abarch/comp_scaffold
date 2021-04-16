import csv
import time
import shutil
import argparse
import pandas as pd
import prompt_toolkit as ptk

# from tqdm import tqdm
from time import sleep
from pathlib import Path
from collections import namedtuple
from openfaceInput import OpenFaceInput

from constants import temp_dir 

from crypto import encrypt_file, decrypt_file

temp_storage_path = temp_dir / "openface_data"
perm_storage_path = Path("openface_data")
perm_storage_toc  = perm_storage_path / "toc.csv"

for d in (temp_storage_path, perm_storage_path):
    d.mkdir(exist_ok=True)


user_data_fields = "name camera_pos face_centered external_light glasses posture".split(" ")
UserData = namedtuple("UserData", user_data_fields)
sess_data_fields = "timestamp scenario".split(" ")
SessData = namedtuple("SessData", sess_data_fields)
# DataEntry = namedtuple("UserData", "name camera_pos external_light glasses posture")


def get_dict_writer(file):
    return csv.DictWriter(file, sess_data_fields + user_data_fields + ["folder"])

# def get_dict_writer(file):
#     return csv.DictWriter(file, sess_data_fields + user_data_fields + ["folder"])


def _init_toc(delete_old=False):
    if perm_storage_toc.exists():
        if not delete_old:
            return
        perm_storage_toc.unlink()
        
    with open(perm_storage_toc, "w") as f:
        writer = get_dict_writer(f)
        writer.writeheader()
    
        
_init_toc()

def _prompt_with_choices(prompt, choices, force_choice=True):
    class MyCustomCompleter(ptk.completion.Completer):
        def get_completions(self, document, complete_event):
            for choice in choices:
                yield ptk.completion.Completion(choice, start_position=-len(document.text))


    #maybe just cycle with tab
    from prompt_toolkit.key_binding import KeyBindings

    bindings = KeyBindings()
    # idx = 0
    @bindings.add('tab')
    def _(event):
        # print(event.current_buffer, dir(event.current_buffer))
        current_sel = event.current_buffer.text
        idx = choices.index(current_sel)
        
        idx += 1
        idx %= len(choices)
        event.current_buffer.text= choices[idx]
        # print("KEY", event)
    
    
    # completer = ptk.completion.WordCompleter(choices)
    completer = MyCustomCompleter()
    text = ptk.prompt(prompt, 
                      # completer=completer, 
                      default=choices[0],
                      key_bindings=bindings)
    
    #todo check force_choice
    
    return text
    
    

def query_user_data(dummy=False):
    if dummy:
        return UserData(name="test", camera_pos="above_screen", external_light=True,
                        glasses=True, posture="sitting")
    
    with open(perm_storage_toc, "r") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        all_names = list( {row["name"] for row in rows} )
        all_camera_positions = list( {row["camera_pos"] for row in rows} )
    
    twidth = shutil.get_terminal_size().columns
    
    print()
    print("Press <tab> to cycle through options".center(twidth, " "))
    print("only write in something yourself if no option fits.".center(twidth, " "))
    print()
    name = _prompt_with_choices("Enter name: ", all_names)
    camera_pos = _prompt_with_choices("Select camera position: ", all_camera_positions)
    face_centered = _prompt_with_choices("Are you going to center your face in the middle of the camera-image? (check instructions): ", ["true", "false"])
    external_light = _prompt_with_choices("Are there lights on in the room? ", ["true", "false"])
    glasses = _prompt_with_choices("Are you wearing glasses? ", ["true", "false"])
    posture = _prompt_with_choices("Select current posture: ", ["sitting", "standing"])
    
    return UserData(name=name, camera_pos=camera_pos, face_centered=face_centered,
                    external_light=external_light,
                    glasses=glasses, posture=posture)



def get_data(dummy=False):
    # TODO maybe make a screenshot of the OpenFace window to get a better picture of the setup
    beep = lambda: print("\a", end="")

    global keyboard_data, screen_data
    global markers, df
    markers = list()
    
    twidth = shutil.get_terminal_size().columns
    
    ofi = OpenFaceInput()
    ofi.start()
    print()
    print("Wait for the openface-window to open,".center(twidth))
    print("adjust the camera or yourself to roughly center / uncenter yourself,".center(twidth))
    print("and click back here for further interaction.".center(twidth))
    print()
    sleep(2)
    classes = ["SCREEN", "KEYBOARD", "AIR"]
    
    for target in classes:
        print(f"LOOK AT {target}")
        print("PRESS ENTER TO START, THEN AGAIN ENTER TO FINISH WITH THIS TARGET")
        # sleep(pause_between)
        if not dummy:
            input()
        else:
            sleep(1)
        print("GO")
        # print("\a")
        beep()
        markers.append(time.time())
        # sleep(length)
        if not dummy:
            input()
        else:
            sleep(3)
        markers.append(time.time())
        
        
        beep()
        sleep(0.1)
        beep()
        
        print("-"*32)
    
    
    sleep(2)
    df = ofi.stop()
    
    start_end_markers = dict()
    
    for target in classes:
        start_end_markers[target] = (markers.pop(0), markers.pop(0))
    
    # print(start_end_markers)
    
    write_class_file(ofi, df, start_end_markers)
    
    return ofi.output_dir


def write_class_file(ofi, df, markers):
    global class_df
    class_file = ofi.output_dir / "classes.csv"
    
    class_df = df.copy()
    class_df["class"] = "None"
    class_df["class_method"] = "acquisition"
    
    for target_class, (start, end) in markers.items():
        post_start_mask = class_df.timestamp > start
        pre_end_mask = class_df.timestamp < end
        mask = post_start_mask & pre_end_mask
        
        # print(class_df["timestamp"].min(), class_df["timestamp"].max())
        # print(start, end)
        # print(post_start_mask, post_start_mask.unique())
        # print(pre_end_mask, pre_end_mask.unique())
        # print(mask, mask.unique())
        
        class_df.loc[mask,"class"] = target_class
        
        # break
    
    # print(class_df.info())
    # print(class_df.head(15))
    
    to_save = class_df[["frame", "class", "class_method"]]
    to_save.to_csv(class_file, index=False)
    
    # can then be put together again with pd.merge(df1, df2)
    
def write_info_file(user_data, sess_data, folder):
    d = dict()
    d.update(user_data._asdict())
    d.update(sess_data._asdict())
    d["folder"] = str(folder)
    
    info_file = folder / "info.csv"
    with open(info_file, "w") as f:
        writer = get_dict_writer(f)
        writer.writeheader()
        writer.writerow(d)
    
    with open(perm_storage_toc, "a") as f:
        writer = get_dict_writer(f)
        # writer.writeheader()
        writer.writerow(d)
    
def get_perm_name(user_data, sess_data):
    u = user_data
    s = sess_data
    return f"{s.timestamp}-{u.name}-{s.scenario}"

def main_acquire_data(dummy=False):
    user_data = query_user_data(dummy=dummy)
    dummy_tag = "_dummy" if dummy else ""
    sess_data = SessData(timestamp=time.strftime("%Y_%m_%d-%H_%M_%S"), 
                         scenario="data_acquisiton_v1" + dummy_tag)
    folder = get_data(dummy=dummy)
    
    print("The acquired data is located at", folder)
    while True:
        print("Do you want to")
        print("\t[a] save your data together with the encrypted images of your face")
        print("\t[d] save only your data, without the images")
        print("\t[c] not save any of the data (maybe something went wrong during recording)")
        choice = input("> ")
        
        if choice.lower() in ["a"]:
            choice = "FULL"
            break
        if choice.lower() in ["d"]:
            choice = "DATA_ONLY"
            break
        if choice.lower() in ["c"]:
            print("The data will not leave your machine.")
            print("Bye")
            return
            # choice = "CANCEL"
            # break
        # TODO rename the folder based on choice?
        print("Unclear input", repr(choice))
    
    # if we are still here, the 
    img_folder = folder / "main_aligned"
    if choice == "DATA_ONLY":
        shutil.rmtree(img_folder)
    if choice == "FULL":
        # zip and encrypt
        archive = shutil.make_archive(folder/"images", "gztar", img_folder)
        shutil.rmtree(img_folder)
        
        enc_file = encrypt_file(archive)
        # decrypt_file(enc_file, delete=False)
        
    perm_name = get_perm_name(user_data, sess_data)
    perm_location = perm_storage_path / perm_name
    perm_location.mkdir(parents=True)
    
    #shutil.copytree(folder, perm_location) # might be risky, what if there are unkown things in here?
    for extension in ["csv", "txt", "enc", "enc.pwd"]:
        for file in folder.glob(f"*.{extension}"):
            shutil.copy(file, perm_location)
    
    
        # import tarfile
        # tar = tarfile.open("sample.tar.gz")
        # tar.extractall()
        # tar.close()
    
    
    write_info_file(user_data, sess_data, perm_location) # only use this when actually coping and with updated folder loc
    

def load_all_saved_data():
    entries = list()
    with open(perm_storage_toc, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            raw_df   = pd.read_csv(Path(row["folder"])/"main.csv")
            class_df = pd.read_csv(Path(row["folder"])/"classes.csv")
            entries.append((raw_df, class_df, row))
    
    return entries


def preprocess_factory(adding_meta_data, class_mapper, feature_filter,
                       ):
    ## this approach has to be ajdusted when using categoricals !
    
    def preprocess(df, verbose=False):
        df = df.copy() # needed to supress warning, and shouldn't be too bad
        
        annotated_data = "class" in df.columns
        
        if annotated_data:
            df.loc[:,"clf_target"] = None
            # you only need to clean classes for training, but not for classification data
            for target in df["class"].unique():
                clf_target = class_mapper(target)
                if not clf_target:
                    if verbose:
                        print("dropping", repr(target))
                        
                    df = df[df["class"] != target]
                    # df.drop(df[df["class"] == target].index)
                else:
                    indicies_to_set = df[df["class"] == target].index
                    df.loc[indicies_to_set, "clf_target"] = clf_target
                    
            if verbose:
                print("cleaned classes")
                print(df.info())
                print(df)
                
            
            
        # return 
            
        clf_cols = [col for col in df.columns if feature_filter(col)]
        
        if annotated_data:
            df = df[clf_cols + ["clf_target"]]
        else:
            df = df[clf_cols]
        
        factorize_map = dict()
        for col, dtype in zip(df.columns, df.dtypes):
            if str(dtype) == 'object':
                assert col == "clf_target" # we don't support other categoricals yet
                df.loc[:,col], vals = pd.factorize(df[col])
                factorize_map[col] = vals
        
        # return
        
        if verbose:
            print("FAC_MAP:", factorize_map)
            
            print("cleaned features")
            print(df.info())
            print(df)
    
    
        # return 
        if annotated_data:
            return df, clf_cols, factorize_map["clf_target"]
        
        else:
            return df
    
    return preprocess
    

def train_classifier_on_saved(camera_pos="above_screen"):
    global df
    data = load_all_saved_data()
    
    full_dfs = list()
    for raw, y, info in data:
        ## FILTER INFO HERE
        if info["camera_pos"] != camera_pos:
            continue
        
        new_df = pd.merge(raw, y)
        
        ## -> this forces us to have all the info for new data
        # for key, val in info.items():
        #     new_df[key] = val
            
        full_dfs.append(new_df)
        
        
    # for df in full_dfs:
    #     print(df.info())
    df = pd.concat(full_dfs)
    df = df.reset_index(drop=True)
    df["clf_target"] = None
    
    print(df.info())
    print(df)
    
    
    def class_mapper(target_class):
        if target_class.lower() in ["screen", "keyboard", "air"]:
            return target_class.lower()
        return None
    
    def feature_filter(feature):
        if feature in ["clf_target", "class", "class_method", "timestamp", "frame"]:
            return False
        # if "pose" in feature:
        #     return True
        # return False
        return True # "p" in feature
    
    
    preprocess = preprocess_factory(adding_meta_data=None, 
                                    class_mapper=class_mapper, 
                                    feature_filter=feature_filter)
    
    
    df, clf_cols, target_classes = preprocess(df)
    
    from sklearn.model_selection import train_test_split
    
    train, test = train_test_split(df, test_size=0.25)
    
    
    from sklearn.tree import DecisionTreeClassifier, export_graphviz
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.svm import LinearSVC

    
    ####
    def df2Xy(df):
        X = df[clf_cols]
        # y = [targets.index(v) for v in df["clf_target"]]
        y = df["clf_target"]
        return X, y
    
    # clf = DecisionTreeClassifier(max_depth=5)
    # clf = RandomForestClassifier()
    clf = LinearSVC(max_iter=1000)
    X, y = df2Xy(train)
    # y = 
    
    pre_fit = time.time()
    clf.fit(X, y)
    print("FITTING TOOK {:.2f}s".format(time.time()-pre_fit))
    
    if hasattr(clf, "feature_importances_"):
        feature_importance = [(v, feat) for v, feat in zip(clf.feature_importances_, X.columns)]
        feature_importance = sorted(feature_importance, reverse=True)
        for v, feat in feature_importance[:16]:
            print(f"{v:.4f}\t", feat)
    
    try:
        export_graphviz(clf, out_file="tree.dot",
                        feature_names=clf_cols, 
                        class_names=target_classes,
                        filled=True,
                        leaves_parallel=True,
                        proportion=True,
                        # rotate=True,
                        rounded=True,
                        impurity=False,
                        )
        
        import subprocess
        subprocess.run("dot -Tpng tree.dot -o tree.png".split(" "))
    except:
        pass
    
    
    train_score = clf.score(X, y)
    print(f"TRAIN SCORE: {train_score:.3f}")
    
    
    ### TEST ###
    
    X, y = df2Xy(test)
    test_score = clf.score(X, y)
    print(f"TEST_SCORE:  {test_score:.3f}")
    
    
    
    
    ###
        
    return clf, target_classes, preprocess


# def save_clfs():
#     clf, target_classes, preprocess = train_classifier_on_saved()
#     import joblib
#     joblib.dump(clf, "clf.joblib.pkl")
#     joblib.dump(target_classes, "target_classes.joblib.pkl")
#     joblib.dump(preprocess, "preprocess.joblib.pkl")
    

def eval_holdout_session():
    global df
    data = load_all_saved_data()
    
    full_dfs = list()
    for raw, y, info in data:
        ## FILTER INFO HERE
        if info["camera_pos"] == "below_screen":
            continue
        
        new_df = pd.merge(raw, y)
        
        ## -> this forces us to have all the info for new data
        # for key, val in info.items():
        #     new_df[key] = val
            
        full_dfs.append((new_df, info))
        
    
    train_scores = list()
    test_scores  = list()
    
        
    for holdout_df, holdout_info in full_dfs:
        df = pd.concat([df for df, i in full_dfs if i != holdout_info])
        
    # for df in full_dfs:
    #     print(df.info())
    # df = pd.concat(full_dfs)
        df = df.reset_index(drop=True)
        df.loc[:,"clf_target"] = None
        
        # print(df.info())
        # print(df)
        
        
        def class_mapper(target_class):
            if target_class.lower() in ["screen", "keyboard"]: #, "air"
                return target_class.lower()
            return None
        
        def feature_filter(feature):
            if feature in ["clf_target", "class", "class_method", "timestamp", "frame"]:
                return False
            if "gaze" in feature: # or "eye" in feature
                return True
            return False
            return True # "p" in feature
        
        
        
        preprocess = preprocess_factory(adding_meta_data=None, 
                                        class_mapper=class_mapper, 
                                        feature_filter=feature_filter)
        
        
        df, _, _ = preprocess(df)
        holdout_df, clf_cols, target_classes = preprocess(holdout_df)
        
        
        from sklearn.model_selection import train_test_split
        
        # train, test = train_test_split(df, test_size=0.25)
        train = df
        test = holdout_df
        
        
        ####
        def df2Xy(df):
            X = df[clf_cols]
            # y = [targets.index(v) for v in df["clf_target"]]
            y = df["clf_target"]
            return X, y
        
        from sklearn.tree import DecisionTreeClassifier, export_graphviz
        from sklearn.ensemble import RandomForestClassifier
        from sklearn.svm import LinearSVC

        
        # clf = DecisionTreeClassifier(max_depth=4)
        # clf = RandomForestClassifier()
        clf = LinearSVC(max_iter=1000)
        
        X, y = df2Xy(train)
        # y = 
        
        sleep(2)
        
        pre_fit_time = time.time()
        clf.fit(X, y)
        print("Fitting took {:.2f}s".format(time.time()-pre_fit_time))
        
        if hasattr(clf, "tree_"):
            export_graphviz(clf, out_file="tree.dot",
                            feature_names=clf_cols, 
                            class_names=target_classes,
                            filled=True,
                            leaves_parallel=True,
                            proportion=True,
                            # rotate=True,
                            rounded=True,
                            impurity=False,
                            )
            
            import subprocess
            subprocess.run("dot -Tpng tree.dot -o tree.png".split(" "))
        
        train_score = clf.score(X, y)
        print("-"*16)
        if hasattr(clf, "feature_importances_"):
            feature_importance = [(v, feat) for v, feat in zip(clf.feature_importances_, X.columns)]
            feature_importance = sorted(feature_importance, reverse=True)
            for v, feat in feature_importance[:16]:
                print(f"{v:.4f}\t", feat)
        
        
        print("holding out", holdout_info)
        print(f"TRAIN SCORE: {train_score:.3f}")
        
        
        ### TEST ###
        
        X, y = df2Xy(test)
        
        test_score = clf.score(X, y)
        print(f"TEST_SCORE:  {test_score:.3f}")
        
        predicted_y = clf.predict(X)
        # print(y.to_numpy().dtype)
        # print(predicted_y.dtype)
        from sklearn.metrics import classification_report, plot_confusion_matrix
        import matplotlib.pyplot as plt
        
        print(classification_report(y.to_numpy(), predicted_y,
                                    target_names=target_classes
                                   ))
        
        plot_confusion_matrix(clf, X, y, display_labels=target_classes)
        plt.show()
        
        print("-"*16)
        
        train_scores.append(train_score)
        test_scores.append( test_score)
     
    import numpy as np
    print("TRAIN MEAN:   {:.3f}".format(np.mean(train_scores)))
    print("TRAIN MEDIAN: {:.3f}".format(np.median(train_scores)))
    print("TEST  MEAN:   {:.3f}".format(np.mean( test_scores)))
    print("TEST  MEDIAN: {:.3f}".format(np.median(test_scores)))
        
    ###
        
    # return clf, target_classes, preprocess

df = None
if __name__ == "__main__":
    
    
    # parser = argparse.ArgumentParser()
    # parser.add_argument(name_or_flags, kwargs)
    
    # main_acquire_data(dummy=False)
    
    # df = train_classifier_on_saved()
    # save_clfs()
    eval_holdout_session()