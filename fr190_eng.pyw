# Author - Bohdan SOKRUT
# https://github.com/bohdansok/Face_Recognition
##
import face_recognition
import os
import pickle
import os.path
import glob
import shutil
import json
import tkinter as tk
import xlsxwriter
import concurrent.futures
from tkinter import filedialog, simpledialog
from tkinter import messagebox
from tkinter import scrolledtext
from datetime import datetime
from PIL import Image
from PIL import ImageDraw


# Global vars - Start
appcurver = "Faces Recognition 1.90 by Bohdan SOKRUT and Python 3.8, dlib, face_recognition"
# Global vars - End
##


def LoadDirList():
    """[Reading a list of earlier scanned directories from JSON-type file _dirlist.ini]
    Returns:
        [dl]: [dictionary with path:date_time]
        [fl]: [flag is True (loaded) or False (not loaded)]
    """
    dlnm = "_dirlist.ini"
    dl = {}
    fl = False
        try:
            f = open(dlnm, "r")
        except (IOError, EOFError) as e:
            tk.messagebox.showwarning(
                "Attention!", "Can't fins/read scanned image folders data file: {}".format(e.args[-1]))
            return None, fl
        else:
            dl = json.load(f)
            f.close()
            fl = True
            return dl, fl


def SaveDirList(dl):
    """[Saves sсanned folders data - DirList dictionary, to the file JSON-type file _dirlist.ini]

    Args:
        dl ([Dictionary]): [dictionary with path:date_time]
    """
    dlnm = "_dirlist.ini"
    dltmp = {}
    try:
        f = open(dlnm, "r")
    except:
        pass
    else:
        dltmp = json.load(f)
        f.close()
        dl.update(dltmp)
        del(dltmp)
    try:
        f = open(dlnm, "w")
    except OSError:
        tk.messagebox.showwarning(
            "Attention!",
            "Can't save scanned folders data file %s" % dlnm)
        return
    else:
        json.dump(dl, f)
        f.close()
    return


def sel_dir(rootwnd, Title, dl, notskipcheck, subd):
    """[Choose an image folder to scan while checking if it is already in DirList as scanned one]
    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
        Title ([str]): [Title for tkinter.filedialog.askdirectory messagebox]
        dl ([dict]): [DirList]
        notskipcheck ([boolean]): [True to check if a selected folder is alreadu in DirList]
        subd ([boolean]): [True of a selected folder and all it's subfolders should be scanned too]
    Returns:
        [str]: [path to an image folder to be scanned]
    """
    sel_dir_path = tk.filedialog.askdirectory(
        parent=rootwnd, title=Title, mustexist=True)
    if sel_dir_path in [".", "", None]:
        return
    else:
        # check if selected path is among already scanned list and flag to check is True
        if sel_dir_path in dl and notskipcheck:
            if tk.messagebox.askyesno("Attention!", "The folder %s has been already scanned. Proceed?" % dl.get(sel_dir_path)):
                if subd:
                    dl[sel_dir_path] = str(datetime.now().strftime(
                        "%Y-%m-%d %H.%M.%S")) + " (with subfolders)"
                else:
                    dl[sel_dir_path] = str(
                        datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
                return sel_dir_path
            else:
                sel_dir_path = sel_dir(rootwnd, Title, dl, notskipcheck, subd)
                return sel_dir_path
        else:
            if sel_dir_path != None:
                if subd:
                    dl[sel_dir_path] = str(datetime.now().strftime(
                        "%Y-%m-%d %H.%M.%S")) + " (with subfolders)"
                else:
                    dl[sel_dir_path] = str(
                        datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
        return sel_dir_path


def dir_load_allimg(parwnd):
    """[Finds all image-type files in a particulr image folder, recognizes faces and adds face' encodings
    and pathes to the images into at dictionary and then saves it at .pkl (Pickle-type) file]
    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """
    knownEncodings = []
    knownNames = []
    facelocs = []
    fl_MultyTh = False
    mod = "hog"
    mod5_68 = "large"
    fl_dir_comment = True
    fl_dir_cmnt_file_created = False
    # Load Dir_list
    dl = {}
    Dir_List = {}
    dl, fl_Dir_List_Loaded = LoadDirList()
    if fl_Dir_List_Loaded:
        Dir_List = dl
    del(dl)
    ###
    answ = tk.simpledialog.askinteger(
        "Choose a FR Math model",
        "1 - HOG (faster), 2- CNN (more accurate):",
        minvalue=1, maxvalue=2, initialvalue=1
        )
    if answ != None:  # choose a Math FR model
        if answ == 1:
            mod = "hog"
        if answ == 2:
            mod = "cnn"
    else:
        mod = "hog"
           # number of upsamles for face locations nd resample when face encoding
    nous = tk.simpledialog.askinteger("Number of upsamples for face locations",
                                      "1 - 100 (less - faster, bigger - smaller faces to be found)",
                                      minvalue=1, maxvalue=100, initialvalue=1)
    if nous == None:
        nous = 1
    njits = tk.simpledialog.askinteger("Number of upsamples for face encodings",
                                       "1 - 100 (bigger - slower but more accurate)",
                                       minvalue=1, maxvalue=100, initialvalue=1)
    if njits == None:
        njits = 1
    # setting small or large model for face encoding
    answ = tk.simpledialog.askinteger("Face encoding model",
                                      "1 - small (5 points, faster), 2- large (default, 68 points):",
                                      minvalue=1, maxvalue=2, initialvalue=2)
    if answ != None:  # setting tolerance for facecomp
        if answ == 1:
            mod5_68 = "small"
        if answ == 2:
            mod5_68 = "large"
    # setting common comment for all pictures in the folder
    dir_comment = tk.simpledialog.askstring(
        "Additional comment", "Add a comment for all files in folder (Enter if empty)",
        initialvalue="")
    if dir_comment in ["", "None", None]:  #  do not create comments' file if no comments
        fl_dir_comment = False
    directory = sel_dir(
        parwnd, "Select a folder with reference pictures", Dir_List, True, False)
    if directory in [".", "", None]:
        del(knownNames)
        del(knownEncodings)
        del(facelocs)
        return
    if fl_dir_comment:
        cmntfn = os.path.join(directory, "_facrecmnt.ini")
        try:
            fcmnt = open(cmntfn, "wt")
        except:
            fl_dir_cmnt_file_created = False
        else:
            fl_dir_cmnt_file_created = True
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        try:
            os.mkdir(knwdbdir)
        except OSError:
            tk.messagebox.showwarning(
                "Attention!", "Can't create working folder %s" % knwdbdir)
            del(knownNames)
            del(knownEncodings)
            del(facelocs)
            if fl_dir_cmnt_file_created:
                fcmnt.close()
            return
    fn = os.path.join(knwdbdir, "v3-" + mod5_68 + str(datetime.now()).replace(":", ".") + ".pkl")
    try:
        f = open(fn, "wb")
    except OSError:
        tk.messagebox.showwarning(
            "Attention!", "Can't create face database file %s" % fn)
        del(knownNames)
        del(knownEncodings)
        del(facelocs)
        if fl_dir_cmnt_file_created:
                fcmnt.close()
        return
    cnt = 0
    fcnt = 0
    frlif = face_recognition.load_image_file
    frfl = face_recognition.face_locations
    frfe = face_recognition.face_encodings
    # init multithread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    entries = os.scandir(directory)
    for entry in entries:
        parwnd.title(
            appcurver + " - added %d face(s) from %d pictures..." % (cnt, fcnt))
        if (entry.name.split(".")[-1].lower() in ["bmp", "gif", "jpg", "jpeg", "png"]) and entry.is_file():
            if fl_dir_comment and fl_dir_cmnt_file_created:
                print(entry.name, dir_comment, file=fcmnt, sep="\t", end="\n", flush=True)
            fcnt += 1
            if fl_MultyTh:  # trying to use MultyThreads
                try:
                    image = executor.submit(frlif, entry.path).result()
                except:
                    continue
                else:
                    boxes = executor.submit(
                        frfl, image, number_of_times_to_upsample=nous, model=mod).result()
            else:
                try:
                    image = frlif(entry.path)
                except:
                    continue
                else:
                 # maybe cnn - more accu and use GPU/CUDA,
                     boxes = frfl(image, number_of_times_to_upsample=nous, model=mod)
            if len(boxes) > 0:  # 1 or more faces in 1 pic - various face encodds' with the same pic file
                if fl_MultyTh:
                    encies = executor.submit(
                        frfe, image, boxes, num_jitters=njits, model=mod5_68).result()
                else:
                    encies = frfe(image, known_face_locations=boxes, num_jitters=njits, model=mod5_68)
                enccnt = 0
                for enc in encies:
                    knownEncodings.append(enc)
                    knownNames.append(entry.path)
                    facelocs.append(boxes[enccnt])
                    enccnt += 1
                    cnt += 1
                boxes.clear()
    del(frlif)
    del(frfl)
    del(frfe)
    del(entries)
    if fl_dir_cmnt_file_created:
                fcmnt.close()
    # shutdowm multythread session
    if fl_MultyTh:
        executor.shutdown(wait=False)
    data = {}
    data = {"encodings": knownEncodings, "names": knownNames, "locations": facelocs}
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    SaveDirList(Dir_List)
    del(Dir_List)
    del(data)
    del(knownNames)
    del(knownEncodings)
    del(facelocs)
    tk.messagebox.showinfo("Information",
                           "Added %d face(s) from %d  pictures at %s. Saving encodings to file..." % (cnt, fcnt, directory))
    parwnd.title(appcurver)
    return


def dir_load_allimg_sub(parwnd):
    """[Finds all image-type files in a particulr image folder and it's subfolders, recognizes faces and adds face' encodings
    and pathes to the images into at dictionary and then saves it at .pkl (Pickle-type) file]
    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """
    knownEncodings = []
    knownNames = []
    facelocs = []
    allimgf = []
    mod = "hog"
    mod5_68 = "large"
    fl_MultyTh = False
    # Load Dir)list
    Dir_List = {}
    dl = {}
    dl, fl_Dir_List_Loaded = LoadDirList()
    if fl_Dir_List_Loaded:
        Dir_List = dl
    del(dl)
    ###
    answ = tk.simpledialog.askinteger("Choose a FR Math model", "1 - HOG (faster), 2- CNN (more accurate):",
                                      minvalue=1, maxvalue=2, initialvalue=1)
    if answ != None:  # choosing model
        if answ == 1:
            mod = "hog"
        if answ == 2:
            mod = "cnn"
    else:
        mod = "hog"
    nous = tk.simpledialog.askinteger("Проходів пошуку облич",
                                      "1 - 100 (більше - точніше, але довше)",
                                      minvalue=1, maxvalue=100, initialvalue=1)
    if nous == None:
        nous = 1
    njits = tk.simpledialog.askinteger("Проходів при кодуванні обличь",
                                       "1 - 100 (більше - точніше, але довше)",
                                       minvalue=1, maxvalue=100, initialvalue=1)
    if njits == None:
        njits = 1
    answ = tk.simpledialog.askinteger("Оберіть модель кодування обличь", "1 - мала (швидше), 2- велика (точніше):",
                                      minvalue=1, maxvalue=2, initialvalue=2)
    if answ != None:  # setting tolerance for facecomp
        if answ == 1:
            mod5_68 = "small"
        if answ == 2:
            mod5_68 = "large"
    directory = sel_dir(
        parwnd, "Select a folder with reference pictures to scan (with subfoders)", Dir_List, True, True)
    if directory in [".", "", None]:
        del(allimgf)  # clearing trash
        del(knownNames)
        del(knownEncodings)
        del(facelocs)
        return
    # creating workin folders
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        try:
            os.mkdir(knwdbdir)
        except OSError:
            tk.messagebox.showwarning(
                "Attention!", "Can't create working folder %s" % knwdbdir)
            del(allimgf)  # clearing trash
            del(knownNames)
            del(knownEncodings)
            del(facelocs)
            return
    fn = os.path.join(knwdbdir, "v3-" + mod5_68 + str(datetime.now()).replace(":", ".") + ".pkl")
    try:
        f = open(fn, "wb")
    except OSError:
        tk.messagebox.showwarning(
            "Attention!", "Can't create face database file %s" % fn)
        del(allimgf)  # clearing trash
        del(knownNames)
        del(knownEncodings)
        del(facelocs)
        return
    cnt = 0
    fcnt = 0
    # creating local objects - functions
    frlif = face_recognition.load_image_file
    frfl = face_recognition.face_locations
    frfe = face_recognition.face_encodings
    # init multithread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    # creating list of all images in the dir and subdirs
    allimgf.extend(glob.glob(directory + "/**/*.jpg", recursive=True))
    allimgf.extend(glob.glob(directory + "/**/*.jpeg", recursive=True))
    allimgf.extend(glob.glob(directory + "/**/*.png", recursive=True))
    allimgf.extend(glob.glob(directory + "/**/*.bmp", recursive=True))
    allimgf.extend(glob.glob(directory + "/**/*.gif", recursive=True))
    for entry in allimgf:
        if os.path.isfile(entry):
            parwnd.title(
                appcurver + " - added %d face(s) from %d pictures..." % (cnt, fcnt))
            fcnt += 1
            if fl_MultyTh:
                try:
                    image = executor.submit(frlif, entry).result()
                except:
                    continue
                else:
                     boxes = executor.submit(
                        frfl, image, number_of_times_to_upsample=nous, model=mod).result()
            else:
                try:
                    image = frlif(entry.path)
                except:
                    continue
                else:
                    boxes = frfl(image, number_of_times_to_upsample=nous, model=mod) # maybe cnn - more accu and use GPU/CUDA,
            if len(boxes) > 0:  # more then 1 face in 1 pic - various face encodds' with the same oic file
                if fl_MultyTh:
                    encies = executor.submit(
                        frfe, image, known_face_locations=boxes, num_jitters=njits, model=mod5_68).result()
                else:
                    encies = frfe(image, known_face_locations=boxes, num_jitters=njits, model=mod5_68)
                enccnt = 0
                for enc in encies:
                    knownEncodings.append(enc)
                    knownNames.append(entry)
                    facelocs.append(boxes[enccnt])
                    enccnt += 1
                    cnt += 1
                boxes.clear()
        else:
            continue
    del(allimgf)
    del(frlif)
    del(frfl)
    del(frfe)
    data = {}
    data = {"encodings": knownEncodings,
        "names": knownNames,
        "locations": facelocs}
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    del(data)
    del(knownEncodings)
    del(knownNames)
    del(facelocs)
    # shutdowm multythread session
    if fl_MultyTh:
        executor.shutdown(wait=False)
    SaveDirList(Dir_List)
    del(Dir_List)
    tk.messagebox.showinfo("Information",
                           "Added %d face(s) from %d  pictures at %s. Saving encodings to file..." % (
                               cnt, fcnt, directory)
                           )
    parwnd.title(appcurver)
    return


def dir_load_wantedimg(parwnd):  # Loading and encoding wanted people
    """[Finds all image-type files in a particulr dirctory, recognizes faces and adds face' encodings
    and path to image into  temp dictionary and then save it at .pkl (Pickle-type) file]
    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """
    ### vars - start
    wantedEncodings = []
    wantedNames = []
    facelocs = []
    mod = "hog"  # default for FR mathem. model
    mod5_68 = "large"
    fl_dir_comment = True
    fl_dir_cmnt_file_created = False
    # Load Dir)list
    Dir_List = {}
    dl = {}
    dl, fl_Dir_List_Loaded = LoadDirList()
    if fl_Dir_List_Loaded:
        Dir_List = dl
    del(dl)
    ###
    fl_MultyTh = False
    ### vars - end
    answ = tk.simpledialog.askinteger("Choose a FR Math model", "1 - HOG (faster), 2- CNN (more accurate):",
                                      minvalue=1, maxvalue=2, initialvalue=1)
    if answ != None:  # setting tolerance for facecomp
        if answ == 1:
            mod = "hog"
        if answ == 2:
            mod = "cnn"
    nous = tk.simpledialog.askinteger("Проходів пошуку обличь",
                                      "1 - 100 (більше - точніше, але довше)",
                                      minvalue=1, maxvalue=100, initialvalue=1)
    if nous == None:
        nous = 1
    njits = tk.simpledialog.askinteger("Проходів при кодуванні обличь",
                                       "1 - 100 (більше - точніше, але довше)",
                                       minvalue=1, maxvalue=100, initialvalue=1)
    if njits == None:
        njits = 1
    answ = tk.simpledialog.askinteger("Оберіть модель кодування обличь", "1 - мала (швидше), 2- велика (точніше):",
                                      minvalue=1, maxvalue=2, initialvalue=2)
    if answ != None:  # setting tolerance for facecomp
        if answ == 1:
            mod5_68 = "small"
        if answ == 2:
            mod5_68 = "large"
    # setting common comment for all pictures in the folder
    dir_comment = tk.simpledialog.askstring(
        "Додайте коментар", "Коментар буде додано для усіх зображень (якщо немає - Enter)",
        initialvalue="")
    if dir_comment in ["", "None", None]:  #  do not create comments' file if no comments
        fl_dir_comment = False
    # selecting wanted folder
    directory = sel_dir(
        parwnd, "Choose a folder with the pictures of wanted individual(s)", Dir_List, False, False)
    if directory in [".", "", None]:
        del(wantedEncodings)
        del(wantedNames)
        del(facelocs)
        return
    if fl_dir_comment:
        cmntfn = os.path.join(directory, "_facrecmnt.ini")
        try:
            fcmnt = open(cmntfn, "wt")
        except:
            fl_dir_cmnt_file_created = False
        else:
            fl_dir_cmnt_file_created = True
   # making local copies of global funcs
    frlif = face_recognition.load_image_file
    frfl = face_recognition.face_locations
    frfe = face_recognition.face_encodings
    # init multythread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    # check if _wanted folder available
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    if not os.path.exists(wntdbdir):
        try:
            os.mkdir(wntdbdir)
        except OSError:
            tk.messagebox.showwarning(
                "Attention!", "Can't create working foldeг %s" % wntdbdir)
            del(frlif)
            del(frfl)
            del(frfe)
            del(wantedEncodings)
            del(wantedNames)
            del(facelocs)
            if fl_dir_cmnt_file_created:
                fcmnt.close()
            return
    fn = os.path.join(wntdbdir, "wanted.pkl")
    if os.path.exists(fn):
        if tk.messagebox.askyesno("Attention!", "Wanted individuals data file already exists. Replace?"):
            try:
                f = open(fn, "wb")
            except OSError:
                tk.messagebox.showwarning(
                    "Attention!", "Can't create face database file %s" % fn)
                del(frlif)
                del(frfl)
                del(frfe)
                del(wantedEncodings)
                del(wantedNames)
                del(facelocs)
                if fl_dir_cmnt_file_created:
                    fcmnt.close()
                return
            cnt = 0
            fcnt = 0
            data = {}
            entries = os.scandir(directory)
            for entry in entries:
                parwnd.title(
                    appcurver + " - added %d face(s) from %d pictures..." % (cnt, fcnt))
                if (entry.name.split(".")[-1].lower() in ["bmp", "gif", "jpg", "jpeg", "png"]) and entry.is_file():
                        if fl_dir_comment and fl_dir_cmnt_file_created:
                        print(entry.name, dir_comment, file=fcmnt, sep="\t", end="\n", flush=True)                    
                    fcnt += 1
                    if fl_MultyTh:
                        try:
                            image = executor.submit(frlif, entry.path).result()
                        except:
                            continue
                        else:
                            boxes = executor.submit(
                                frfl, image, number_of_times_to_upsample=nous, model=mod).result()
                    else:
                        try:
                            image = frlif(entry.path)
                        except:
                            continue
                        else:
                            boxes = frfl(image, number_of_times_to_upsample=nous, model=mod) # maybe cnn - more accu and use GPU/CUDA,
                    if len(boxes) > 0:
                        if fl_MultyTh:
                            encies = executor.submit(
                                frfe, image, known_face_locations=boxes, num_jitters=njits, model=mod5_68).result()
                        else:
                            encies = frfe(image, known_face_locations=boxes, num_jitters=njits, model=mod5_68)
                        enccnt = 0
                        for enc in encies:
                            wantedEncodings.append(enc)
                            wantedNames.append(entry.path)
                            facelocs.append(boxes[enccnt])
                            enccnt += 1
                            cnt += 1
                        boxes.clear()
            data = {"encodings": wantedEncodings, "names": wantedNames, "locations": facelocs}
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
            # writing the search set path to _dir.ini (JSON-type) file
            wssfn = os.path.join(wntdbdir, "_dir.ini")
            try:
                f = open(wssfn, "w")
                json.dump(directory, f)
                f.close()
            except OSError:
                tk.messagebox.showwarning(
                    "Attention!", "Can't write search options to file %s. Reports will be saved at the app's working folder" % wssfn)
            del(data)
            del(wantedEncodings)
            del(wantedNames)
            del(facelocs)
            del(frlif)
            del(frfl)
            del(frfe)
            if fl_dir_cmnt_file_created:
                fcmnt.close()
            if fl_MultyTh:
                executor.shutdown(wait=False)
            tk.messagebox.showinfo('Information.',
                                   "Added %d face(s) from %d  pistures at %s. Saving encodings to file..." % (cnt, fcnt, directory))
            parwnd.title(appcurver)
            return
        else:
            if fl_dir_cmnt_file_created:
                fcmnt.close()
            return
    else:
        try:
            f = open(fn, "wb")
        except OSError:
            tk.messagebox.showwarning(
                "Attention!", "Can't create face database file %s" % fn)
            del(frlif)
            del(frfl)
            del(frfe)
            if fl_MultyTh:
                executor.shutdown(wait=False)
            return
        cnt = 0
        fcnt = 0
        data = {}
        entries = os.scandir(directory)
        for entry in entries:
            parwnd.title(
                appcurver + " - added %d face(s) from %d pictures..." % (cnt, fcnt))
            if (entry.name.split(".")[-1].lower() in ["bmp", "gif", "jpg", "jpeg", "png"]) and entry.is_file():
                if fl_dir_comment and fl_dir_cmnt_file_created:
                    print(entry.name, dir_comment, file=fcmnt, sep="\t", end="\n", flush=True)                  
                fcnt += 1
                if fl_MultyTh:
                    try:
                        image = executor.submit(frlif, entry.path).result()
                    except:
                        continue
                    else:
                        boxes = executor.submit(
                            frfl, image, number_of_times_to_upsample=nous, model=mod).result()
                else:
                    try:
                        image = frlif(entry.path)
                    except:
                        continue
                    else:
                        boxes = frfl(image, number_of_times_to_upsample=nous, model=mod) # maybe cnn - more accu and use GPU/CUDA,
                if len(boxes) > 0:
                    if fl_MultyTh:
                        encies = executor.submit(
                            frfe, image, known_face_locations=boxes, num_jitters=njits, model=mod5_68).result()
                    else:
                        encies = frfe(image, known_face_locations=boxes, num_jitters=njits, model=mod5_68)
                    enccnt = 0
                    for enc in encies:
                        wantedEncodings.append(enc)
                        wantedNames.append(entry.path)
                        facelocs.append(boxes[enccnt])
                        enccnt += 1
                        cnt += 1
                    boxes.clear()
        data = {"encodings": wantedEncodings, "names": wantedNames, "locations": facelocs}
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()
        # writing the search set path to _dir.ini (JSON-type) file
        wssfn = os.path.join(wntdbdir, "_dir.ini")
        try:
            f = open(wssfn, "w")
            json.dump(directory, f)
            f.close()
        except OSError:
            tk.messagebox.showwarning(
                "Attention!", "Can't write search options to file %s. Reports will be saved at the app's working folder" % wssfn)
        del(data)
        del(wantedEncodings)
        del(wantedNames)
        del(facelocs)
        del(frlif)
        del(frfl)
        del(frfe)
        if fl_dir_cmnt_file_created:
                fcmnt.close()
        if fl_MultyTh:
            executor.shutdown(wait=False)
        tk.messagebox.showinfo('Інформація',
                               "Added %d face(s) from %d  pistures at %s. Saving encodings to file.." % (cnt, fcnt, directory))
        parwnd.title(appcurver)
    return


def facedic_load(dicfilename):
    """[Loads a dictionary with face encodings from Pickle-type file]
    Args:
        dicfilename ([str]): [Pickle-type file *.pkl]
    Returns:
        [dict]: [a dictionary with face encodings : path ti image file]
    """
    try:
        f = open(dicfilename, "rb")
    except (IOError, EOFError) as e:
        tk.messagebox.showwarning(
            "Attention!", "Can't find/read face encodings data file {}".format(e.args[-1]))
        return
    else:
        if os.path.getsize(dicfilename) > 15:
            picdic = {}
            picdic = pickle.load(f)
        else:
            f.close()
            return None
    f.close()
    return picdic

# optimization of *.pkl face encodings data files: all 1 k ... 10M files to be cosolidated.
# Less files - faster search


def optim():
    """[optimization of *.pkl face encodings data files: all 1 k ... 10M sized files to be cosolidated.
    Less files - faster search]
    """
    Encodings = []
    Names = []
    facelocs = []
    # const: min and max sizes of data files to be consolidated
    pkl_min_sz = 1000
    pkl_max_sz = 10000000
    ###
    if tk.messagebox.askyesno("Attention", "Small face encodings data files to be consolidated for faster face search. Proceed?"):
        knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
        if not os.path.exists(knwdbdir):
            tk.messagebox.showwarning(
                "Attention!", "Can't find/read working folder %s" % knwdbdir)
            return
        backupdir = os.path.join(os.path.join(knwdbdir, "_backup"))
        if not os.path.exists(backupdir):
            try:
                os.mkdir(backupdir)
            except OSError:
                tk.messagebox.showwarning(
                    "Attention!", "Can't creat back-up folder %s" % backupdir)
                return
        bigdic = {}
        bigdic = {}
        v3fcnt = 0
        entries = os.scandir(knwdbdir)
        for entry in entries:
            if entry.name.lower().startswith("v3-") and entry.name.lower().endswith(".pkl") and entry.is_file() and os.path.getsize(entry.path) > pkl_min_sz and os.path.getsize(entry.path) < pkl_max_sz:
                td = {}
                td = facedic_load(entry.path)  # Reading facedic
                Encodings.extend(td["encodings"])
                Names.extend(td["names"])
                facelocs.extend(td["locations"])
                try:
                    shutil.move(entry.path, os.path.join(backupdir, entry.name))
                except:
                    pass                   
                del(td)
                v3fcnt += 1
        fn = os.path.join(knwdbdir, "v3-opt_" + str(datetime.now()).replace(":", ".") + ".pkl")
        try:
            f = open(fn, "wb")
        except OSError:
            tk.messagebox.showwarning(
                "Увага!",
                 "Не можу створити файл бази даних %s. Перенесіть файли з даних з теки %s назад до теки %s" % (fn, backupdir, knwdbdir))
            del(Encodings)
            del(Names)
            del(facelocs)
            return
        bigdic = {"encodings": Encodings, "names": Names, "locations": facelocs}
        pickle.dump(bigdic, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()
        bigdic.clear()
        Encodings.clear()
        del(facelocs)
        Names.clear()
        # optimization of old-school data files
        bigdic = {}
        fcnt = 0
        entries = os.scandir(knwdbdir)
        for entry in entries:
            if not entry.name.lower().startswith("v3-") and entry.name.lower().endswith(".pkl") and entry.is_file() and os.path.getsize(entry.path) > pkl_min_sz and os.path.getsize(entry.path) < pkl_max_sz:
                td = {}
                td = facedic_load(entry.path)  # Reading facedic
                Encodings.extend(td["encodings"])
                Names.extend(td["names"])
                try:
                    shutil.move(entry.path, os.path.join(backupdir, entry.name))
                except:
                    pass                   
                del(td)
                fcnt += 1
        fn = os.path.join(knwdbdir, "opt_" + str(datetime.now()).replace(":", ".") + ".pkl")
        try:
            f = open(fn, "wb")
        except OSError:
            tk.messagebox.showwarning(
                "Увага!",
                 "Не можу створити файл бази даних %s. Перенесіть файли з даних з теки %s назад до теки %s" % (fn, backupdir, knwdbdir))
            del(Encodings)
            del(Names)
            del(facelocs)
            return
        bigdic = {"encodings": Encodings, "names": Names}
        pickle.dump(bigdic, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()
        del(bigdic)
        del(Encodings)
        del(Names)    
        tk.messagebox.showinfo('Інформація',
                               "Консолідовано %d файлів кодувань обличь. Резервні копії переміщено до %s." % (v3fcnt + fcnt, backupdir))
    return

# Main searcher
#
#


def pic_search(parwnd):
    """[Searches wanted face encoding from WantedFaceDic among known faces in KnownFaceDic, 
    and outputs reports as .txt and .xlsx files]
    Args:
    rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """
    # vars
    tmpwlist = []
    tmpetlist = []
    fl_rep_dir_default = False
    fl_MultyTh = False
    fl_dir_cmnt_file_loaded = False
    fl_New_knowndir = True
    fl_New_wonteddir = True
    ###
    answ = tk.simpledialog.askfloat("Face recognition accuracy", "Less - more accurate (0<x<1, good (default) is 0.45):",
                                    minvalue=0.000, maxvalue=1.000, initialvalue=0.45)
    if answ != None:  # setting tolerance for facecomp
        tol = answ
    else:
        tol = 0.45
    knwdbdir = os.path.join(os.path.join(
        os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        tk.messagebox.showwarning(
            "Attention!", "Can't find/read working folder %s" % knwdbdir)
        return
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    if not os.path.exists(wntdbdir):
        tk.messagebox.showwarning(
            "Attention!", "Can't find/read working folder %s" % wntdbdir)
        return
    fnw = os.path.join(wntdbdir, "wanted.pkl")
    if not os.path.exists(fnw):
        tk.messagebox.showwarning(
            "Attention!", "Can't find/read wanted individuals(s) data file %s. Please, scan the appropriate folder with pictures" % fnw)
        return
    # defining path to the current reports
    rep_conf_fn = os.path.join(wntdbdir, "_dir.ini")
    if os.path.exists(rep_conf_fn):
        try:
            dcf = open(rep_conf_fn, "r")
            rep_dir = json.load(dcf)
            dcf.close()
            if not os.path.exists(rep_dir):
                fl_rep_dir_default = True  # path to report folder is loaded and is nor blank
        except (IOError, EOFError) as e:
            fl_rep_dir_default = True
            tk.messagebox.showwarning(
                "Attention!", "Can't find/read search options file: {}".format(e.args[-1]))
    else:
        fl_rep_dir_default = True
    # creatin report's files
    if fl_rep_dir_default:
        try:
            txtfn = "Report_" + \
                str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")
                    ).replace(":", ".") + ".txt"
            txtrep = open(txtfn, "wt")
        except (IOError, EOFError) as e:
            tk.messagebox.showwarning(
                "Attention!", "Не можу записати файл звіту {}".format(e.args[-1]))
            return
        try:
            xlxfn = "Report_" + \
                str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")
                    ).replace(":", ".") + ".xlsx"  # xlsx
            wsx = xlsxwriter.Workbook(xlxfn)
        except (IOError, EOFError) as e:
            tk.messagebox.showwarning(
                "Attention!", "Can't write report file {}".format(e.args[-1]))
            return
    else:
        try:
            txtfn = os.path.join(rep_dir, "Report_" + str(
                datetime.now().strftime("%Y-%m-%d %H.%M.%S")).replace(":", ".") + ".txt")
            txtrep = open(txtfn, "wt")
        except (IOError, EOFError) as e:
            tk.messagebox.showwarning(
                "Attention!", "Can't write report file {}".format(e.args[-1]))
            return
        try:
            xlxfn = os.path.join(rep_dir, "Report_" + str(datetime.now().strftime(
                "%Y-%m-%d %H.%M.%S")).replace(":", ".") + ".xlsx")  # xlsx
            wsx = xlsxwriter.Workbook(xlxfn)
        except (IOError, EOFError) as e:
            tk.messagebox.showwarning(
                "Attention!", "Can't write report file {}".format(e.args[-1]))
            return
    # init multythread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
     # xlsx cell formats
    cell_bold = wsx.add_format()
    cell_bold.set_bold()
    cell_wrap = wsx.add_format()
    cell_wrap.set_text_wrap()
    cell_url = wsx.add_format(
        {'underline': True, 'font_color': 'blue', 'text_wrap': True})
    # xlsx header
    wrksx = wsx.add_worksheet(
        'Report ' + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")))
    # width of columns
    wrksx.set_column(0, 0, 37, cell_wrap) 
    wrksx.set_column(1, 4, 33)
    wrksx.set_column(2, 3, 25)
    wrksx.set_column(5, 6, 33, cell_wrap)
    wrksx.write(0, 0, "Report created " + str(datetime.now().strftime(
        "%Y-%m-%d %H.%M.%S")) + " by %s" % appcurver, cell_bold)
    wrksx.write(1, 0, "Accuracy: " + str(tol), cell_bold)
    wrksx.write(3, 0, "Wanted person picture file", cell_bold)
    wrksx.write(3, 1, "Wanted person's photo", cell_bold)
    wrksx.write(3, 2, "Wanted person's face", cell_bold)
    wrksx.write(3, 3, "Found face", cell_bold)
    wrksx.write(3, 4, '"Reference picture', cell_bold)
    wrksx.write(3, 5, "Reference picture's file", cell_bold)
    wrksx.write(3, 6, "Additional data", cell_bold)    # txt header
    print("Report created ", str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")),
          " by %s" % appcurver, file=txtrep, end="\n", flush=False)
    print("Accuracy: ", str(tol), file=txtrep, end="\n", flush=False)
    print("Wanted individual picture file", "\t",
          "Reference individual's picture file", "\t", file=txtrep, end="\n", flush=False)
    ###
    WantedFaceDic = facedic_load(fnw)  # Reading wantedfacedic
    wfdlen = len(WantedFaceDic["encodings"])
    frcf = face_recognition.compare_faces
    # for all .pkl files in _DB
    dfcnt = 0
    allfound = [] # temp list for search results
    entries = os.scandir(knwdbdir)
    for entry in entries:
        parwnd.title(
            appcurver + " - found %d face(s) among %d reference data files" % (wfdlen, dfcnt))
        if (entry.name.lower().endswith(".pkl")) and entry.is_file():
            dfcnt += 1
            td = {}
            td = facedic_load(entry.path)  # Reading wantedfacedic
            if td != None:
                KnownFaceDic = td
                del(td)
            else:
                del(td)
                continue
            wcnt = 0
            # finding wanted encodings at every loaded data file
            for wcnt in range(wfdlen):
                wenc = WantedFaceDic["encodings"][wcnt]
                wname = WantedFaceDic["names"][wcnt]
                try:
                    wloc = WantedFaceDic["locations"][wcnt]
                except:
                    fl_New_wanteddir = False
                    wloc = (0, 0, 0, 0)
                else:
                    fl_New_wanteddir = True
                if fl_MultyTh:
                    match = executor.submit(
                        frcf, KnownFaceDic["encodings"], wenc, tolerance=tol).result()
                else:
                    match = frcf(
                        KnownFaceDic["encodings"], wenc, tolerance=tol)
                if True in match:
                    matchedIdxs = [i for (i, b) in enumerate(match) if b]
                    for i in matchedIdxs:
                        st = ""
                        c1 = "file:///" + wname.replace("\\", "/")
                        t1 = os.path.normpath(wname)
                        c2 = "file:///" + \
                            str(KnownFaceDic["names"][i]).replace("\\", "/")
                        t2 = os.path.normpath(KnownFaceDic["names"][i])
                        try:
                            floc = KnownFaceDic["locations"][i]
                        except:
                            fl_New_knowndir = False
                            floc = (0, 0, 0, 0)
                        else:
                            fl_New_knowndir = True
                        cmntfn = os.path.join(t2.rpartition("\\")[0], "_facrecmnt.ini")
                        try:
                            cmtf = open(cmntfn, "rt")
                        except:
                            fl_dir_cmnt_file_loaded = False
                        else:
                            dir_coms = {}
                            for line in cmtf:
                                dir_coms[line.split("\t")[0]] = line.split("\t")[1]
                            fl_dir_cmnt_file_loaded = True
                            cmtf.close()
                        extst = ""
                        if fl_dir_cmnt_file_loaded:
                            extst = str(dir_coms.get(t2.rpartition("\\")[2]))
                        st = " ".join([st, "Дод. коментар:", extst.replace("\n", "")])
                        if fl_dir_cmnt_file_loaded:
                            del(dir_coms)
                        allfound.append([c1, t1, c2, t2, st, floc, wloc])
    xlcnt = 4  # starting row at XLSX-sheet
    for r in allfound:
        wrksx.set_row(xlcnt, 175) # висота рядка
        wrksx.write(xlcnt, 0, r[0], cell_url)
        wrksx.write(xlcnt, 5, r[2], cell_url)
        wrksx.write(xlcnt, 6, r[4])
        print(r[1] + "\t" + r[3] + "\t" + r[4],
              file=txtrep, end="\n", flush=False)
        # thumbnails:
        try:
            im = Image.open(r[1])
            if fl_New_wanteddir:
                t1t = "".join([r[1], str(r[6]), str(datetime.now()).replace(":", ""),
                               "_241.jpg"])  # ескізу для gif-формату не буде
                t1tcr = "".join([r[1], str(r[6]), str(datetime.now()).replace(":", ""), "_cr1.jpg"])
                imcr = im.crop((r[6][3] - 3, r[6][0] - 3, r[6][1] + 3, r[6][2] + 3))
                draw = ImageDraw.Draw(im)
                # r[5] is tuple (top, right, bottom, left) order
                draw.rectangle((r[6][3] - 3, r[6][0] - 3, r[6][1] + 3, r[6][2] + 3),
                               outline="red", width=4) # top, left, right, bottom
                im.thumbnail((240, 240))
                im.save(t1t)
                imcr.thumbnail((240, 240))
                imcr.save(t1tcr)            
                tmpwlist.append(t1t)
                tmpwlist.append(t1tcr)
                wrksx.insert_image(xlcnt, 1, t1t, {'object_position': 1})
                wrksx.insert_image(xlcnt, 2, t1tcr, {'object_position': 1})
            else:
                t1t = "".join([r[1], str(r[6]), str(datetime.now()).replace(":", ""),
                               "_241.jpg"])  # ескізу для gif-формату не буде
                im.thumbnail((240, 240))
                im.save(t1t)
            tmpwlist.append(t1t)
            wrksx.insert_image(xlcnt, 1, t1t, {'object_position': 1})
        except:
            wrksx.write(xlcnt, 1, "Ескізу не буде")
            wrksx.write(xlcnt, 2, "Ескізу не буде")
        try:
            im = Image.open(r[3])
            if fl_New_knowndir:
                t2t = "".join([r[3], str(r[5]), str(datetime.now()).replace(":", ""),
                               "_242.jpg"])  # ескізу для gif-формату не буде
                t2tcr = "".join([r[3], str(r[5]), str(datetime.now()).replace(":", ""), "_cr2.jpg"])
                imcr = im.crop((r[5][3] - 3, r[5][0] - 3, r[5][1] + 3, r[5][2] + 3))
                draw = ImageDraw.Draw(im)
                # r[5] is tuple (top, right, bottom, left) order
                draw.rectangle((r[5][3] - 3, r[5][0] - 3, r[5][1] + 3, r[5][2] + 3),
                               outline="lightgreen", width=4) # top, left, right, bottom
                im.thumbnail((240, 240))
                im.save(t2t)
                imcr.thumbnail((240, 240))
                imcr.save(t2tcr)            
                tmpetlist.append(t2t)
                tmpetlist.append(t2tcr)
                # wrksx.insert_image(xlcnt, 2, t2t, {'object_position': 1}) # old style w/o cropped thumbs
                wrksx.insert_image(xlcnt, 3, t2tcr, {'object_position': 1})
                wrksx.insert_image(xlcnt, 4, t2t, {'object_position': 1})
            else:
                t2t = "".join([r[3], str(r[5]), str(datetime.now()).replace(":", ""),
                               "_242.jpg"])  # ескізу для gif-формату не буде
                im.thumbnail((240, 240))
                im.save(t2t)
                tmpetlist.append(t2t)
                # wrksx.insert_image(xlcnt, 2, t2t, {'object_position': 1}) # old style w/o cropped thumbs
                wrksx.insert_image(xlcnt, 4, t2t, {'object_position': 1})
        except Exception as e:
            print(e)
            wrksx.write(xlcnt, 3, "Ескізу не буде")
            wrksx.write(xlcnt, 4, "Ескізу не буде")
        xlcnt += 1
    # clear and close
    wsx.close()
    txtrep.flush()
    txtrep.close()
    if fl_MultyTh:
        executor.shutdown(wait=False)
    del(WantedFaceDic)
    del(KnownFaceDic)
    del(frcf)
    del(allfound)
    for fw in tmpwlist:
        try:
            os.remove(fw)
        except:
            continue
    del(tmpwlist)
    for fe in tmpetlist:
        try:
            os.remove(fe)
        except:
            continue
    del(tmpetlist)
    tk.messagebox.showinfo('Information', "Done search of %d face(s) among %d reference data file(s). Reports saved at %s and %s" % (
        wfdlen, dfcnt, txtfn, xlxfn))
    parwnd.title(appcurver)
    return


def showdirlist():
    """[If DirList loaded from file outputs a tkinter window with scrillable text of DirList]

    Args:
        fl ([boolean]): [True if DirList was leaded from _dirlist.ini]
    """
    dl = {}
    fl = False
    dl, fl = LoadDirList()
    if fl:
        win = tk.Tk()
        win.title("Список сканованих папок з еталонними фото")
        text_area = tk.scrolledtext.ScrolledText(win,
                                                 wrap=tk.WORD,
                                                 width=126,
                                                 height=10,
                                                 font=("Times New Roman",
                                                       12))
        for k in dl.keys():
            s = str(k).ljust(65) + str(dl[k]).rjust(23) + "\n"
            text_area.insert(tk.INSERT, s)
        del(dl)
        text_area.configure(state='disabled')
        text_area.focus()
        text_area.pack()
        win.mainloop()
        return
    else:
        return

def showhelp():
    try:
        if os.path.getsize("help.pdf") > 0:
             os.system("start help.pdf")
             return
    except:
        pass
    try:
        if os.path.getsize("help.htm") > 0:
             os.system("start help.htm")
             return
    except:
        tk.messagebox.showwarning(
                "Увага!", "Не можу знайти/прочитати файл довідки")
        return

# GUI
wnd = tk.Tk(screenName=appcurver)
wnd.title(appcurver)
frame1 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=10)
label1 = tk.Label(master=frame1,
                  text="FIND UNKNOWN FACES AMONG KNOWN ONES",
                  font=("Times New Roman", 15),
                  background='green',
                  foreground="white",
                  height=3
                  )
label1.pack()
frame1.pack()
##
frame2 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=8)
label2 = tk.Label(master=frame2,
                  text='''1. Choose folder(s) with the pictures (.jpg, .png, .bmp, .gif) of reference (known, identified) individuals to create a database.
                  Scan only once; any new pictures store at new folder(s) and scan them too''',
                  font=("Times New Roman", 13),
                  background='green',
                  foreground="white",
                  height=3
                  )
label2.pack()
but_lb = tk.Button(master=frame2,
                   text='Scan reference pictures folder',
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: dir_load_allimg(wnd))
but_lbsub = tk.Button(master=frame2,
                      text='Scan reference pictures folder (with subfolders) ',
                      relief=tk.RAISED,
                      height=1,
                      font=("Times New Roman", 16),
                      bg='lightgreen',
                      command=lambda: dir_load_allimg_sub(wnd))
but_lb.pack(side=tk.LEFT)
but_lbsub.pack(side=tk.RIGHT)
frame2.pack()
##
frame3 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=8)
label3 = tk.Label(master=frame3,
                  text='2. Choose a folder with wanted individual(s) pictures',
                  font=("Times New Roman", 13),
                  background='green',
                  foreground="white",
                  height=3
                  )
label3.pack()
but_lw = tk.Button(master=frame3,
                   text='Scan wanted  individual(s) pictures folder',
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: dir_load_wantedimg(wnd))
but_lw.pack()
frame3.pack()
##
frame4 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=8)
label4 = tk.Label(master=frame4,
                  text='3. Push ANALYZE & REPORT to search the faces. Reports will be saved at current app folderї as TXT та XLSX (with thumbnails).',
                  font=("Times New Roman", 13),
                  background='green',
                  foreground="white",
                  height=3
                  )
label4.pack()
but_ab = tk.Button(master=frame4,
                   text='ANALYZE & REPORT',
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: pic_search(wnd))
but_dir = tk.Button(master=frame4,
                    text='List of scanned folders...',
                    relief=tk.SUNKEN,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='grey',
                    fg="white",
                    command=showdirlist)
but_opt = tk.Button(master=frame4,
                    text='Face database optimization',
                    relief=tk.SUNKEN,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='grey',
                    fg="white",
                    command=optim)
but_help = tk.Button(master=frame4,
                    text='Help...',
                    relief=tk.SUNKEN,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='grey',
                    fg="white",
                    command=showhelp)
but_ab.pack(side=tk.LEFT)
but_opt.pack(side=tk.RIGHT)
but_dir.pack(side=tk.RIGHT)
but_help.pack(side=tk.RIGHT)
frame4.pack()
##
wnd.mainloop()
