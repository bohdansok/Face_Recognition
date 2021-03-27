# -*- coding: utf-8 -*-
__author__ = """Bohdan SOKRUT"""
__www__ = 'https://github.com/bohdansok/Face_Recognition'
__version__ = '1.92'

##
import concurrent.futures
import glob
import json
import os
import os.path
import pickle
import shutil
import subprocess
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
import cv2
import face_recognition
import psutil
import xlsxwriter
from PIL import Image, ImageDraw
from face_recognition import api as frapi
import numpy as np
import dlib


# Global vars - Start
appcurver = "Face Recognition 1.92 (Video&Masks) by Bohdan SOKRUT (powered by dlib)"
Posv_Dir = {}
fl_Posv_Dir_Loaded = False
# Global vars - End
##


class Full_object_detection_masked(dlib.full_object_detection):
    def part(self, idx:int):
        if idx in range(2, 15) or idx in range(48, 68) or idx in range(29, 36):
            return (0, 0)
        return super().part(idx)
    
    def parts(self):
        lst = []
        # eyes, brows and midnose only
        for idx in range(0, 2):
            lst.append(super().part(idx))
        for idx in range(2, 15):
            lst.append(dlib.point(0, 0))
        for idx in range(15, 29):
            lst.append(super().part(idx))
        for idx in range(29, 36):
            lst.append(dlib.point(0, 0))
        for idx in range(36, 48):
            lst.append(super().part(idx))    
        for idx in range(48, 68):
            lst.append(dlib.point(0, 0))
        return lst
    
    
def face_encodings_masked(face_image, known_face_locations=None, num_jitters=1, model="large"):
    """
    Given an image, return the 128-dimension face encoding for each face in the image, 
    zeroing points for the parts of a face, covered by a medical mask

    :param face_image: The image that contains one or more faces
    :param known_face_locations: Optional - the bounding boxes of each face if you already know them.
    :param num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
    :param model: Optional - which model to use. "large" (default) or "small" which only returns 5 points but is faster.
    :return: A list of 128-dimensional face encodings (one for each face in the image)
    """
    raw_landmarks = frapi._raw_face_landmarks(face_image,
                                        known_face_locations,
                                        model)
    masked_raw_landmarks = []
    for lm in raw_landmarks:
        masked_raw_landmarks.append(Full_object_detection_masked(lm.rect, lm.parts()))
    return [np.array(frapi.face_encoder.compute_face_descriptor(face_image,
                                                          raw_landmark_set,
                                                          num_jitters)) for raw_landmark_set in raw_landmarks]


# Читаємо дані про раніше скановані каталоги з файлу "_dirlist.ini", якщо він є
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
                "Увага!", "Не можу знайти/прочитати файл даних сканованих папок: {}".format(e.args[-1]))
            return None, fl
    else:
        dl = json.load(f)
        f.close()
        fl = True
        return dl, fl

# Записуємо до файлу "_dirlist.ini" дані про скановані каталоги


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
            "Увага!", "Не можу записати дані про скановані теки %s" % dlnm)
        return
    else:
        json.dump(dl, f)
        f.close()
    return

# Обираємо теку для сканування наявності обличь у файлах зображень JPG, PNG


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
        if sel_dir_path in dl and notskipcheck:  # якщо шлях у списку сканованих і є флаг га перевірку
            if tk.messagebox.askyesno("Увага!", "Ця тека вже сканувлась %s. Повторити?" % dl.get(sel_dir_path)):
                if subd:
                    dl[sel_dir_path] = str(datetime.now().strftime(
                        "%Y-%m-%d %H.%M.%S")) + " (з вклад. теками)"
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
                        "%Y-%m-%d %H.%M.%S")) + " (з вклад.теками)"
                else:
                    dl[sel_dir_path] = str(
                        datetime.now().strftime(
                            "%Y-%m-%d %H.%M.%S"))
        return sel_dir_path


def dir_load_allimg(parwnd):
    """[Finds all image-type files in a particulr image folder, recognizes faces and adds face' encodings
    and pathes to the images into at dictionary and then saves it at .pkl (Pickle-type) file]

    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """
    knownEncodings = []
    knownMaskedEncodings = []
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
        "Оберіть матем. модель пошуку обличь",
        "1 - HOG (швидше), 2- CNN (точніше):",
        minvalue=1, maxvalue=2, initialvalue=1
        )
    if answ != None:  # обираємо модель
        if answ == 1:
            mod = "hog"
        if answ == 2:
            mod = "cnn"
    else:
        mod = "hog"
        # number of upsamles for face locations nd resample when face encoding
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
    # setting small or large model for face encoding
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
    # select a target folder
    directory = sel_dir(
        parwnd, "Оберіть теку з еталонними фото", Dir_List, True, False)
    if directory in [".", "", None]:
        del(knownNames)
        del(knownEncodings)
        del(knownMaskedEncodings)
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
                "Увага!", "Не можу створити робочу теку %s" % knwdbdir)
            del(knownNames)
            del(knownEncodings)
            del(knownMaskedEncodings)
            del(facelocs)
            if fl_dir_cmnt_file_created:
                fcmnt.close()
            return
    fn = os.path.join(knwdbdir, "v4-" + mod5_68 + str(datetime.now()).replace(":", ".") + ".pkl")
    try:
        f = open(fn, "wb")
    except OSError:
        tk.messagebox.showwarning(
            "Увага!", "Не можу створити файл бази даних %s" % fn)
        del(knownNames)
        del(knownEncodings)
        del(knownMaskedEncodings)
        del(facelocs)
        if fl_dir_cmnt_file_created:
                fcmnt.close()
        return
    cnt = 0
    fcnt = 0
    frlif = face_recognition.load_image_file
    frfl = face_recognition.face_locations
    frfland = face_recognition.face_landmarks
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
            appcurver + " - вже додано %d обличь(чя) з %d зображень..." % (cnt, fcnt))
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
                 # may be cnn - more accu and use GPU/CUDA,
                    boxes = frfl(image, number_of_times_to_upsample=nous, model=mod)
            if len(boxes) > 0:  # 1 or more faces in 1 pic - various face encodds' with the same pic file
                if fl_MultyTh:
                    encies = executor.submit(
                        frfe, image, boxes, num_jitters=njits, model=mod5_68).result()
                    masked_encies = executor.submit(face_encodings_masked,
                                             image, boxes, num_jitters=njits, model="large").result()
                else:
                    encies = frfe(image, known_face_locations=boxes, num_jitters=njits, model=mod5_68)
                    masked_encies = face_encodings_masked(image, known_face_locations=boxes,
                                                          num_jitters=njits, model="large")
                enccnt = 0
                for enc in encies:
                    knownEncodings.append(enc)
                    knownMaskedEncodings.append(masked_encies[enccnt])
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
    data = {"encodings": knownEncodings, "masked": knownMaskedEncodings, "names": knownNames, "locations": facelocs}
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    SaveDirList(Dir_List)
    del(Dir_List)
    del(data)
    del(knownNames)
    del(knownEncodings)
    del(knownMaskedEncodings)
    del(facelocs)
    tk.messagebox.showinfo('Інформація',
                           "Додано %d обличь з %d зображень з теки %s. Зберігаю кодування обличь до файлу..." % (cnt, fcnt, directory))
    parwnd.title(appcurver)
    return


def dir_load_allimg_sub(parwnd):
    """[Finds all image-type files in a particulr image folder and it's subfolders, recognizes faces and adds face' encodings
    and pathes to the images into at dictionary and then saves it at .pkl (Pickle-type) file]

    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """
    knownEncodings = []
    knownMaskedEncodings = []
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
    answ = tk.simpledialog.askinteger("Оберіть матем. модель пошуку обличь", "1 - HOG (швидше), 2- CNN (точніше):",
                                      minvalue=1, maxvalue=2, initialvalue=1)
    if answ != None:  # обираємо модель
        if answ == 1:
            mod = "hog"
        if answ == 2:
            mod = "cnn"
    else:
        mod = "hog"
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
    directory = sel_dir(
        parwnd, "Оберіть папку з еталонними фото (із вклад. теками)", Dir_List, True, True)
    if directory in [".", "", None]:
        del(allimgf)  # clearing trash
        del(knownNames)
        del(knownEncodings)
        del(knownMaskedEncodings)
        del(facelocs)
        return
    # creating workin folders
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        try:
            os.mkdir(knwdbdir)
        except OSError:
            tk.messagebox.showwarning(
                "Увага!", "Не можу створити робочу теку %s" % knwdbdir)
            del(allimgf)  # clearing trash
            del(knownNames)
            del(knownEncodings)
            del(knownMaskedEncodings)
            del(facelocs)
            return
    fn = os.path.join(knwdbdir, "v4-" + mod5_68 + str(datetime.now()).replace(":", ".") + ".pkl")
    try:
        f = open(fn, "wb")
    except OSError:
        tk.messagebox.showwarning(
            "Увага!", "Не можу створити файл бази даних %s" % fn)
        del(allimgf)  # clearing trash
        del(knownNames)
        del(knownEncodings)
        del(knownMaskedEncodings)
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
                appcurver + " - вже додано %d обличь(чя) з %d зображень..." % (cnt, fcnt))
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
                    # maybe cnn - more accu and use GPU/CUDA,
                    boxes = frfl(image, number_of_times_to_upsample=nous, model=mod) # maybe cnn - more accu and use GPU/CUDA,
            if len(boxes) > 0:  # more then 1 face in 1 pic - various face encodds' with the same oic file
                if fl_MultyTh:
                    encies = executor.submit(
                        frfe, image, boxes, num_jitters=njits, model=mod5_68).result()
                    masked_encies = executor.submit(face_encodings_masked,
                                             image, boxes, num_jitters=njits, model="large").result()
                else:
                    encies = frfe(image, known_face_locations=boxes, num_jitters=njits, model=mod5_68)
                    masked_encies = face_encodings_masked(image, known_face_locations=boxes,
                                                          num_jitters=njits, model="large")
                enccnt = 0
                for enc in encies:
                    knownEncodings.append(enc)
                    knownMaskedEncodings.append(masked_encies[enccnt])
                    knownNames.append(entry)
                    facelocs.append(boxes[enccnt])
                    enccnt += 1
                    cnt += 1
                boxes.clear()                
        else:
            continue
    if fl_MultyTh:
        executor.shutdown(wait=False)
    del(allimgf)
    del(frlif)
    del(frfl)
    del(frfe)
    data = {}
    data = {"encodings": knownEncodings, "masked": knownMaskedEncodings, "names": knownNames, "locations": facelocs}
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    del(data)
    del(knownEncodings)
    del(knownMaskedEncodings)
    del(knownNames)
    del(facelocs)
    # shutdowm multithread session
    if fl_MultyTh:
        executor.shutdown(wait=False)
    SaveDirList(Dir_List)
    del(Dir_List)
    tk.messagebox.showinfo('Інформація',
                           "Додано %d обличь з %d зображень з теки %s та вкладених тек. Зберігаю кодування обличь до файлу..." % (
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
    wantedMaskedEncodings = []
    wantedNames = []
    facelocs = []
    mod = "hog"  # default for FR mathem. model
    mod5_68 = "large"
    fl_dir_comment = True
    fl_dir_cmnt_file_created = False
    # Load Dir_list
    Dir_List = {}
    dl = {}
    dl, fl_Dir_List_Loaded = LoadDirList()
    if fl_Dir_List_Loaded:
        Dir_List = dl
    del(dl)
    ###
    fl_MultyTh = False
    ### vars - end
    answ = tk.simpledialog.askinteger("Оберіть матем. модель пошуку обличь", "1 - HOG (швидше), 2- CNN (точніше):",
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
    njits = tk.simpledialog.askinteger("Проходів при кодуванні облич",
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
        parwnd, "Оберіть теку з фото невідомих осіб.", Dir_List, False, False)
    if directory in [".", "", None]:
        del(wantedEncodings)
        del(wantedMaskedEncodings)
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
    # init multithread session
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
                "Увага!", "Не можу створити робочу теку %s" % wntdbdir)
            del(frlif)
            del(frfl)
            del(frfe)
            del(wantedEncodings)
            del(wantedMaskedEncodings)
            del(wantedNames)
            del(facelocs)
            if fl_dir_cmnt_file_created:
                fcmnt.close()
            return
    fn = os.path.join(wntdbdir, "wanted.pkl")
    if os.path.exists(fn):
        if not tk.messagebox.askyesno("Увага!", "Файл даних розшукуваних осіб вже існує. Замінити?"):
            del(frlif)
            del(frfl)
            del(frfe)
            del(wantedEncodings)
            del(wantedMaskedEncodings)
            del(wantedNames)
            del(facelocs)
            if fl_dir_cmnt_file_created:
                fcmnt.close()
            return
    try:
        f = open(fn, "wb")
    except OSError:
        tk.messagebox.showwarning(
                    "Увага!", "Не можу створити файл бази даних %s" % fn)
        del(frlif)
        del(frfl)
        del(frfe)
        del(wantedEncodings)
        del(wantedMaskedEncodings)
        del(wantedNames)
        del(facelocs)
        if fl_dir_cmnt_file_created:
            fcmnt.close()
        if fl_MultyTh:
            executor.shutdown(wait=False)
        return
    cnt = 0
    fcnt = 0
    data = {}
    entries = os.scandir(directory)
    for entry in entries:
        parwnd.title(appcurver + " - вже додано %d обличь(чя) з %d зображень..." % (cnt, fcnt))
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
                    boxes = executor.submit(frfl, image, number_of_times_to_upsample=nous, model=mod).result()
            else:
                try:
                    image = frlif(entry.path)
                except:
                    continue
                else:
                    # may be cnn - more accu and use GPU/CUDA,
                    boxes = frfl(image, number_of_times_to_upsample=nous, model=mod) # maybe cnn - more accu and use GPU/CUDA,
            if len(boxes) > 0:
                if fl_MultyTh:
                    encies = executor.submit(
                        frfe, image, boxes, num_jitters=njits, model=mod5_68).result()
                    masked_encies = executor.submit(face_encodings_masked,
                                             image, boxes, num_jitters=njits, model="large").result()
                else:
                    encies = frfe(image, known_face_locations=boxes, num_jitters=njits, model=mod5_68)
                    masked_encies = face_encodings_masked(image, known_face_locations=boxes,
                                                          num_jitters=njits, model="large")
                enccnt = 0
                for enc in encies:
                    wantedEncodings.append(enc)
                    wantedMaskedEncodings.append(masked_encies[enccnt])
                    wantedNames.append(entry.path)
                    facelocs.append(boxes[enccnt])
                    enccnt += 1
                    cnt += 1
                boxes.clear()
    if fl_MultyTh:
        executor.shutdown(wait=False)
    data = {"encodings": wantedEncodings, "masked": wantedMaskedEncodings, "names": wantedNames, "locations": facelocs}
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
            "Увага!", "Не можу записати параметри пошуку у файл %s. Звіти зберігатимуться у робочу теку програми" % wssfn)
    del(data)
    del(wantedEncodings)
    del(wantedMaskedEncodings)
    del(wantedNames)
    del(facelocs)
    del(frlif)
    del(frfl)
    del(frfe)
    if fl_dir_cmnt_file_created:
        fcmnt.close()
    tk.messagebox.showinfo('Інформація',
                            "Додано %d обличь з %d зображень з теки %s. Зберігаю кодування обличь до файлу..." % (cnt, fcnt, directory))
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
            "Увага!", "Не можу знайти/прочитати файл кодувань обличь: {}".format(e.args[-1]))
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

# optimization of *.pkl face encodings data files: all 1 k ... 10M files to be cosolidated
# Less files - faster search


def optim():
    """[optimization of *.pkl face encodings data files: all 1 k ... 10M sized files to be consolidated.
    Less files - faster search]
    """
    Encodings = []
    masks = []
    Names = []
    facelocs = []
    # const: min and max sizes of data files to be consolidated
    pkl_min_sz = 1000
    pkl_max_sz = 10000000
    ###
    if not tk.messagebox.askyesno("Увага!",
                                  "Дрібні файли даних кодувань обличь буде консолідовано для прискорення пошуку. Продовжити?"):
        return
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        tk.messagebox.showwarning("Увага!", "Не можу знайти робочу теку %s" % knwdbdir)
        return
    backupdir = os.path.join(os.path.join(knwdbdir, "_backup"))
    if not os.path.exists(backupdir):
        try:
            os.mkdir(backupdir)
        except OSError:
            tk.messagebox.showwarning(
                "Увага!", "Не можу створити теку резервних копій %s" % backupdir)
            return
    # optimization of v4 data files
    bigdic = {}
    v4fcnt = 0
    entries = os.scandir(knwdbdir)
    for entry in entries:
        if entry.name.lower().startswith("v4-") and entry.name.lower(
            ).endswith(".pkl") and entry.is_file(
                ) and os.path.getsize(entry.path) > pkl_min_sz and os.path.getsize(entry.path) < pkl_max_sz:
            td = {}
            td = facedic_load(entry.path)  # Reading facedic
            Encodings.extend(td["encodings"])
            masks.extend(td["masked"])
            Names.extend(td["names"])
            facelocs.extend(td["locations"])
            try:
                shutil.move(entry.path, os.path.join(backupdir, entry.name))
            except:
                pass                   
            del(td)
            v4fcnt += 1
    if len(Encodings) > 0:
        fn = os.path.join(knwdbdir, "v4-opt_" + str(datetime.now()).replace(":", ".") + ".pkl")
        try:
            f = open(fn, "wb")
        except OSError:
            tk.messagebox.showwarning(
                "Увага!",
                "Не можу створити файл бази даних %s. Перенесіть файли з даних з теки %s назад до теки %s" % (fn, backupdir, knwdbdir))
            del(Encodings)
            del(masks)
            del(Names)
            del(facelocs)
            return
        bigdic = {"encodings": Encodings, "masked": masks, "names": Names, "locations": facelocs}
        pickle.dump(bigdic, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()
    del(bigdic)
    del(masks)
    Encodings.clear()
    facelocs.clear()
    Names.clear()
    # Optimization of v3 data files
    bigdic = {}
    v3fcnt = 0
    entries = os.scandir(knwdbdir)
    for entry in entries:
        if entry.name.lower().startswith("v3-") and entry.name.lower(
            ).endswith(".pkl") and entry.is_file(
                ) and os.path.getsize(entry.path) > pkl_min_sz and os.path.getsize(entry.path) < pkl_max_sz:
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
    if len(Encodings) > 0:
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
    del(bigdic)
    Encodings.clear()
    del(facelocs)
    Names.clear()
        # optimization of old-school data files
    bigdic = {}
    fcnt = 0
    entries = os.scandir(knwdbdir)
    for entry in entries:
        if (not entry.name.lower().startswith("v3-")) and entry.name.lower().endswith(".pkl") and entry.is_file(
            ) and os.path.getsize(entry.path) > pkl_min_sz and os.path.getsize(entry.path) < pkl_max_sz:
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
    if len(Encodings) > 0:
        fn = os.path.join(knwdbdir, "opt_" + str(datetime.now()).replace(":", ".") + ".pkl")
        try:
            f = open(fn, "wb")
        except OSError:
            tk.messagebox.showwarning("Увага!",
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
                            "Консолідовано %d файлів кодувань обличь. Резервні копії переміщено до %s." % (v4fcnt + v3fcnt + fcnt, backupdir))
    return

# Main searcher
def pic_search(parwnd, mask=False):
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
    answ = tk.simpledialog.askfloat("Точність розпізнавання обличь", "Менше значення - точніше (0<x<1, непогано 0.45):",
                                    minvalue=0.000, maxvalue=1.000, initialvalue=0.45)
    if answ != None:  # setting tolerance for facecomp
        tol = answ
    else:
        tol = 0.45
    knwdbdir = os.path.join(os.path.join(
        os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        tk.messagebox.showwarning(
            "Увага!", "Не можу знайти робочу теку %s" % knwdbdir)
        return
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    if not os.path.exists(wntdbdir):
        tk.messagebox.showwarning(
            "Увага!", "Не можу знайтии робочу теку %s" % wntdbdir)
        return
    fnw = os.path.join(wntdbdir, "wanted.pkl")
    if not os.path.exists(fnw):
        tk.messagebox.showwarning(
            "Увага!", "Файл даних рошукуваних осіб  %s відсутній або недоступний. Проскануйте папку!" % fnw)
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
                "Увага!", "Не можу знайти/прочитати файл даних сканованих папок: {}".format(e.args[-1]))
    else:
        fl_rep_dir_default = True
    # init multythread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    WantedFaceDic = facedic_load(fnw)  # Reading wantedfacedic
    wfdlen = len(WantedFaceDic["encodings"])
    frcf = face_recognition.compare_faces
    frfd = face_recognition.face_distance
    # перебираємо усі файли .pkl у папці _DB
    dfcnt = 0
    allfound = []
    double_mask = mask
    entries = os.scandir(knwdbdir)
    for entry in entries:
        parwnd.title(
            appcurver + " - проведено пошук %d обличь у %d файлах еталонних даних" % (wfdlen, dfcnt))
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
            mask = double_mask
            try:
                t = KnownFaceDic["masked"][0]
            except:
                nmask = False
            try:
                t = WantedFaceDic["masked"][0]
            except:
                wmask = False
            if nmask and wmask:
                mask = double_mask
            else:
                mask = False
            # у кожному файлі даних шукаємо усі розшукувані пики. Так швидше.
            for wcnt in range(wfdlen):
                ### Here the mask state should be played for the Wenc.
                if mask:
                    wenc = WantedFaceDic["masked"][wcnt]
                else:
                    wenc = WantedFaceDic["encodings"][wcnt]
                ##########
                wname = WantedFaceDic["names"][wcnt]
                try:
                    wloc = WantedFaceDic["locations"][wcnt]
                except:
                    fl_New_wanteddir = False
                    wloc = (0, 0, 0, 0)
                else:
                    fl_New_wanteddir = True
                if fl_MultyTh:
                    if mask:
                        match = executor.submit(frcf, KnownFaceDic["masked"], wenc, tolerance=tol).result()
                    else:
                        match = executor.submit(frcf, KnownFaceDic["encodings"], wenc, tolerance=tol).result()
                else:
                    if mask:
                        match = frcf(KnownFaceDic["masked"], wenc, tolerance=tol)
                    else:
                        match = frcf(KnownFaceDic["encodings"], wenc, tolerance=tol)
                if True in match:
                    matchedIdxs = [i for (i, b) in enumerate(match) if b]
                    for i in matchedIdxs:
                        st = ""
                        c1 = "file:///" + wname.replace("\\", "/")
                        t1 = os.path.normpath(wname)
                        c2 = "file:///" + \
                            str(KnownFaceDic["names"][i]).replace("\\", "/")
                        t2 = os.path.normpath(KnownFaceDic["names"][i])
                        # calculating distance between the faces. First arg should be a list
                        if fl_MultyTh:
                            if mask:
                                distance = executor.submit(frfd, [wenc], KnownFaceDic["masked"][i]).result()
                            else:
                                distance = executor.submit(frfd, [wenc], KnownFaceDic["encodings"][i]).result()
                        else:
                            if mask:
                                distance = frfd([wenc], KnownFaceDic["masked"][i])
                            else:
                                distance = frfd([wenc], KnownFaceDic["encodings"][i])
                        try:
                            floc = KnownFaceDic["locations"][i]
                        except:
                            fl_New_knowndir = False
                            floc = (0, 0, 0, 0)
                        else:
                            fl_New_knowndir = True
                        cmntfn = os.path.join(os.path.dirname(t2), "_facrecmnt.ini")
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
                        allfound.append([c1, t1, c2, t2, st, floc, wloc,
                                         "".join([str(100 - int(distance[0] * 100)), "%"])])
    if fl_MultyTh:
        executor.shutdown(wait=False)
    if len(allfound) > 0:
         # creatin report's files
        if fl_rep_dir_default:
            try:
                txtfn = "Report_" + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")
                                        ).replace(":", ".") + ".txt"
                txtrep = open(txtfn, "wt")
            except (IOError, EOFError) as e:
                tk.messagebox.showwarning(
                    "Увага!", "Не можу записати файл звіту {}".format(e.args[-1]))
                return
            try:
                xlxfn = "Report_" + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")
                                    ).replace(":", ".") + ".xlsx"  # xlsx
                wsx = xlsxwriter.Workbook(xlxfn)
            except (IOError, EOFError) as e:
                tk.messagebox.showwarning(
                "Увага!", "Не можу записати файл звіту {}".format(e.args[-1]))
                return
        else:
            try:
                txtfn = os.path.join(rep_dir, "Report_" + str(
                    datetime.now().strftime("%Y-%m-%d %H.%M.%S")).replace(":", ".") + ".txt")
                txtrep = open(txtfn, "wt")
            except (IOError, EOFError) as e:
                tk.messagebox.showwarning(
                    "Увага!", "Не можу записати файл звіту {}".format(e.args[-1]))
                return
            try:
                xlxfn = os.path.join(rep_dir, "Report_" + str(datetime.now().strftime(
                    "%Y-%m-%d %H.%M.%S")).replace(":", ".") + ".xlsx")  # xlsx
                wsx = xlsxwriter.Workbook(xlxfn)
            except (IOError, EOFError) as e:
                tk.messagebox.showwarning(
                    "Увага!", "Не можу записати файл звіту {}".format(e.args[-1]))
                return
         # xlsx cell formats
        cell_bold = wsx.add_format()
        cell_bold.set_bold()
        cell_wrap = wsx.add_format(
            {'text_wrap': True, 'valign': 'vcenter'})
        cell_url = wsx.add_format(
            {'underline': True, 'font_color': 'blue', 'text_wrap': True, 'valign': 'vcenter'})
        # xlsx header
        wrksx = wsx.add_worksheet(
            'Report ' + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")))
        # width of columns
        wrksx.set_column(0, 0, 30, cell_wrap) 
        wrksx.set_column(1, 4, 33)
        wrksx.set_column(2, 3, 27)
        wrksx.set_column(5, 6, 30, cell_wrap)
        wrksx.set_column(7, 7, 11, cell_wrap)
        wrksx.write(0, 0, "Звіт створено " + str(datetime.now().strftime(
            "%Y-%m-%d %H.%M.%S")) + " з використанням %s" % appcurver, cell_bold)
        if mask:
            wrksx.write(1, 0, "Задана точність: " + str(tol) + " (маски)", cell_bold)
        else:
            wrksx.write(1, 0, "Задана точність: " + str(tol), cell_bold)
        wrksx.write(1, 0, "Задана точність: " + str(tol), cell_bold)
        wrksx.write(3, 0, "Файл зображення розшук. особи", cell_bold)
        wrksx.write(3, 1, "Фото розшук. особи", cell_bold)
        wrksx.write(3, 2, "Обличчя розшук. особи", cell_bold)
        wrksx.write(3, 3, '"Еталонне" обличчя', cell_bold)
        wrksx.write(3, 4, '"Еталонне" зображення', cell_bold)
        wrksx.write(3, 5, "Файл еталонного зображення", cell_bold)
        wrksx.write(3, 6, "Додаткові дані", cell_bold)
        wrksx.write(3, 7, "Схожість, %", cell_bold)
        # txt header
        print("Звіт створено ", str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")),
              " з використанням %s" % appcurver, file=txtrep, end="\n", flush=False)
        print("Задана точність: ", str(tol), file=txtrep, end="\n", flush=False)
        print("Фото розшукуваної особи", "\t", "Еталонне зображення", "\t",
              "Дані АІДС 'НАУТІЛУС та інш.'", "\t", "Схожість, %", file=txtrep, end="\n", flush=False)
        ###
        xlcnt = 4  # starting row at XLSX-sheet
        for r in allfound:
            wrksx.set_row(xlcnt, 175) # висота рядка
            wrksx.write(xlcnt, 0, r[0], cell_url)
            wrksx.write(xlcnt, 5, r[2], cell_url)
            wrksx.write(xlcnt, 6, r[4])
            wrksx.write(xlcnt, 7, r[7])
            print(r[1] + "\t" + r[3] + "\t" + r[4] + "\t" + r[7],
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
                    imcr.thumbnail((192, 192))
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
                    imcr.thumbnail((192, 192))
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
        tk.messagebox.showinfo('Інформація',
                           "Проведено пошук %d обличь у %d файлах еталонних даних. Звіти збережено до файлів %s та %s" % (
        wfdlen, dfcnt, txtfn, xlxfn))
    else:
        tk.messagebox.showinfo('Інформація',
                           "Проведено пошук %d обличь у %d файлах еталонних даних. Збігів не знайдено"  % (wfdlen, dfcnt))
    del(WantedFaceDic)
    del(KnownFaceDic)
    del(frcf)
    del(frfd)
    del(allfound)
    del(LOCWANTED)
    parwnd.title(appcurver)
    return


def showdirlist(root):
    """[If DirList loaded from file outputs a tkinter window with scrillable text of DirList]

    Args:
        fl ([boolean]): [True if DirList was leaded from _dirlist.ini]
    """
    dl = {}
    fl = False
    dl, fl = LoadDirList()
    if fl:
        win = tk.Toplevel(root)
        win.title("Список сканованих папок з еталонними фото")
        text_area = tk.scrolledtext.ScrolledText(win,
                                                 wrap=tk.WORD,
                                                 width=126,
                                                 height=10,
                                                 bg = "lightgrey",
                                                 font=("Times New Roman", 12)
                                                 )
        for k in dl.keys():
            s = str(k).ljust(65) + str(dl[k]).rjust(23) + "\n"
            text_area.insert(tk.INSERT, s)
        del(dl)
        text_area.configure(state='disabled')
        text_area.pack()
        win.focus()
        return
    else:
        return


def splitvid(root):
    """[Splits choosen video file into separate frames with face(s) for further face encoding.]

    Args:
        root ([tkinter.Tk]): [tkinter.Tk parent widget window]
    """    
    fl_MultyTh = False
    frfl = face_recognition.face_locations
    vidfile = tk.filedialog.askopenfilename(master=root, title="Обеоіть файл відео для обробки",
                           filetypes=[('Файли відео', ['.mpeg', '.mpg', '.mp4', '.avi',
                                                       '.mkv'])])
    if vidfile in [".", "", None]:
        return
    framedir = os.path.join(os.path.dirname(vidfile), "frames")
    print(framedir)
    if not os.path.exists(framedir):
        try:
            os.mkdir(framedir)
        except OSError:
            framedir = os.path.dirname(vidfile)
    framecnt = 0
    faceframecnt = 0
    input_movie = cv2.VideoCapture(vidfile)
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    while True:
        ret, frame = input_movie.read()
        framecnt += 1
        if not ret:
            break
        rgb_frame = frame[:, :, ::-1]
        if fl_MultyTh:
            boxes = executor.submit(frfl, rgb_frame).result()
        else:
            boxes = frfl(rgb_frame)
        if len(boxes) > 0:
            filename = os.path.normpath(os.path.join(framedir, "frame" + str(framecnt) + ".jpg"))
            wrtn = cv2.imwrite(filename, rgb_frame)
            if not wrtn:
                tk.messagebox.showinfo('Увага!',
                           "Розмістить відео у теці, шлях до якої та назва не містять кіриличних символів, та повторіть спробу.")
                del(frfl)
                if fl_MultyTh:
                    executor.shutdown(wait=False)
                return
            faceframecnt += 1
    del(frfl)
    if fl_MultyTh:
        executor.shutdown(wait=False)
    tk.messagebox.showinfo('Інформація',
                           "Збережено %d кадрів з обличчами з %d кадрів відео %s." % (faceframecnt,
                                                                                      framecnt, vidfile))
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

def showcurwdir():
    rep_dir = ""
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    rep_conf_fn = os.path.join(wntdbdir, "_dir.ini")
    try:
        dcf = open(rep_conf_fn, "r")
        rep_dir = json.load(dcf)
        dcf.close()
    except (IOError, EOFError) as e:
        tk.messagebox.showwarning("Увага!", "Дані про поточну пошукову теку відсутны.")
    else:
        tk.messagebox.showinfo('Інформація',
                           "Поточна пошукова тека %s" % rep_dir)        
        FILEBRWPATH = os.path.join(os.getenv("WINDIR"), "explorer.exe")
        subprocess.run([FILEBRWPATH, os.path.normpath(rep_dir)])
    return


# GUI
wnd = tk.Tk(screenName=appcurver)
wnd.title(appcurver)
frame1 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=10)
label1 = tk.Label(master=frame1,
                  text="ПОШУК ОБЛИЧЬ У ФАЙЛАХ ЗОБРАЖЕНЬ (НЕВІДОМІ СЕРЕД ВІДОМИХ))",
                  font=("Times New Roman", 16),
                  background='green',
                  foreground="white",
                  height=3
                  )
label1.pack()
frame1.pack()
##
frame2 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=8)
label2 = tk.Label(master=frame2,
                  text='''1. Оберіть теки (по одній) з еталонними фото (.jpg, .png, .bmp, .gif) для наповнення бази даних.
                  Скануйте тільки один раз, а нові еталонні фото кладіть 
                  у нові теки (із наступним їх скануванням). Для виділення кадрів з обличчями з відeофрагменту натисніть кнопку "Обробка відео..."''',
                  font=("Times New Roman", 15),
                  background='green',
                  foreground="white",
                  height=3
                  )
label2.pack()
but_lb = tk.Button(master=frame2,
                   text='Сканувати еталонні фото ',
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: dir_load_allimg(wnd))
but_lbsub = tk.Button(master=frame2,
                      text='Сканувати еталонні фото (із вклад. теками) ',
                      relief=tk.RAISED,
                      height=1,
                      font=("Times New Roman", 16),
                      bg='lightgreen',
                      command=lambda: dir_load_allimg_sub(wnd))
but_video = tk.Button(master=frame2,
                    text='Обробка відео...',
                    relief=tk.RAISED,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='lightgreen',
                    command=lambda: splitvid(wnd))
but_lb.pack(side=tk.LEFT)
but_lbsub.pack(side=tk.RIGHT)
but_video.pack(side=tk.BOTTOM)
frame2.pack()
##
frame3 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=8)
label3 = tk.Label(master=frame3,
                  text='2. Оберіть теку з фото невідомих осіб.',
                  font=("Times New Roman", 15),
                  background='green',
                  foreground="white",
                  height=3
                  )
label3.pack()
but_lw = tk.Button(master=frame3,
                   text='Сканувати фото невідомих осіб',
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: dir_load_wantedimg(wnd))
but_curwdir = tk.Button(master=frame3,
                   text='Поточна тека пошуку...',
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='grey',
                   fg="black",
                   command=showcurwdir)
but_lw.pack(side=tk.LEFT)
but_curwdir.pack(side=tk.RIGHT)
frame3.pack()
##
frame4 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=8)
label4 = tk.Label(master=frame4,
                  text='3. Натисніть кнопку для початку пошуку. Результати буде збережено в теці з файлами фото невідомих осіб у форматах TXT та XLSX (з ескізами).',
                  font=("Times New Roman", 13),
                  background='green',
                  foreground="white",
                  height=3
                  )
label4.pack()
but_ab = tk.Button(master=frame4,
                   text='АНАЛІЗ & ЗВІТ',
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: pic_search(wnd, mask=False))
but_ab_mask = tk.Button(master=frame4,
                   text='АНАЛІЗ & ЗВІТ (МАСКИ)',
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: pic_search(wnd, mask=True))
but_dir = tk.Button(master=frame4,
                    text='Скановані теки...',
                    relief=tk.SUNKEN,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='grey',
                    fg="black",
                    command=lambda: showdirlist(wnd))
but_opt = tk.Button(master=frame4,
                    text='Оптимізація бази даних',
                    relief=tk.SUNKEN,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='grey',
                    fg="black",
                    command=optim)
but_help = tk.Button(master=frame4,
                    text='Довідка...',
                    relief=tk.SUNKEN,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='grey',
                    fg="black",
                    command=showhelp)
but_ab.pack(side=tk.LEFT)
but_ab_mask.pack(side=tk.LEFT)
but_opt.pack(side=tk.RIGHT)
but_dir.pack(side=tk.RIGHT)
but_help.pack(side=tk.RIGHT)
frame4.pack()
##
wnd.mainloop()
if fl_Posv_Dir_Loaded:
    del(Posv_Dir)
