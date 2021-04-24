# -*- coding: utf-8 -*-
__author__ = "Bohdan SOKRUT"
__www__ = 'https://github.com/bohdansok/Face_Recognition'
__version__ = '1/2.96'

##
import concurrent.futures
import json
import os
import os.path
import pickle
import shutil
import subprocess
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, simpledialog
from datetime import datetime
import cv2
import face_recognition
import numpy as np
import mediapipe as mp
import myfrlang
import face_recognition as fr
import dlib


class Face_Dictionary():
    """[The class contains all data structures to store in memory as well as load and save to file
    face encodings data, including picture file full path and face location for each face on every picture]
    """    
    def __init__(self, dicfilename="", mode="load", lang="ukr"): #Create all data objects
        #dicfilename = self.dicfilename
        self.mode = mode
        self.lang = lang
        self.dicfilename = dicfilename
        self.fl_Loaded = False
        self.fl_Saved = False
        self.Encodings = []
        self.Names = []
        self.facelocs = []
        self.fd = {"encodings": self.Encodings, "names": self.Names, "locations": self.facelocs}
        if bool(self.dicfilename) and self.mode == "load":
            self.fl_loaded = self.load()
    
    def destroy(self): #Delete all data objects
        del(self.Encodings)
        del(self.Names)
        del(self.facelocs)
        del(self.fd)
    
    def load(self):
        """
        [Loads a dictionary with face encodings from Pickle-type file into self.fd]

        Args:
            dicfilename ([str]): [Pickle-type file *.pkl]

        Returns:
            [bool]: [True if loaded. Also sets self.fl_Loaded as True]
        """
        if bool(self.dicfilename) and self.mode == "load":
            try:
                f = open(self.dicfilename, "rb")
            except (IOError, EOFError) as e:
                tk.messagebox.showwarning(
                myfrlang.lang[self.lang]["load"][0],
                myfrlang.lang[self.lang]["load"][1].format(e.args[-1]))
                return False
            else:
                if os.path.getsize(self.dicfilename) > 15:
                    self.fd = pickle.load(f)
                    self.fl_Loaded = True
                else:
                    f.close()
                    return  False
            f.close()
            return True
        else:
            return False
    
    def save(self):
        """
        [Saves dictionary with face encodings to Pickle-type file]

        Args:
            None

        Returns:
            [bool]: [True if self.fd has been saved to the original <self.dicfilename.pkl>.
            Also sets self.fl_Saved as True]
        """
        if bool(self.dicfilename) and self.mode == "save":
            try:
                f = open(self.dicfilename, "wb")
            except OSError:
                tk.messagebox.showwarning(
                    myfrlang.lang[self.lang]["save"][0],
                    myfrlang.lang[self.lang]["save"][1] % self.dicfilename)
                return False
            pickle.dump(self.fd, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
            self.fl_Saved = True
            return True
    
    def save_as(self, filename):
        """
        [Saves dictionary with face encodings to Pickle-type file with specified name]

        Args:
            filename ([str]): [Pickle-type file *.pkl]

        Returns:
            [bool]: [True if self.fd has been saved to the original <self.dicfilename.pkl>.
            Also sets self.fl_Saved as True]
        """
        if bool(filename):
            try:
                f = open(filename, "wb")
            except OSError:
                tk.messagebox.showwarning(
                    myfrlang.lang[self.lang]["save"][0],
                    myfrlang.lang[self.lang]["save"][1] % filename)
                return False
            pickle.dump(self.fd, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
            self.fl_Saved = True
            return True   
    

def mp_boxes(image, confid=0.5):
    """[Function uses Medipipe CNN to find out all faces boxes on the given image. 
    It's about 50 times faster even on CPU 
    then original dlib / Face_recognition functions.]
    If Mediapipe found no face boxes (it's possible and depends of image features,
    the function consequently tries to use dlib CNN and HOG models for that.)

    Args:
        image ([np.array]): [image in memory to be proccessed]

    Returns:
        [list]: [list of coordinates of face boundaries boxes]
    """    
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=confid)
    boxes = []
    iheigth, iwidth = image.shape[:2]
    results = face_detection.process(image)
    if not results.detections:
        if dlib.DLIB_USE_CUDA:
            try:
                boxes = fr.face_locations(image, number_of_times_to_upsample=1, model="cnn")
                print("INFO: dlib CNN used instead of Mediapipe")
            except:
                boxes = fr.face_locations(image, number_of_times_to_upsample=1, model="hog")
                print("INFO: dlib HOG used instead of Mediapipe")
                if boxes:
                    return boxes
                else:
                    return None
            if boxes:
                return boxes
            else:
                return None
        else:
            boxes = fr.face_locations(image, number_of_times_to_upsample=1, model="hog")
            print("INFO: dlib HOG used instead of Mediapipe")
            if boxes:
                return boxes
            else:
                return None
    for d in results.detections:
        xmin = int(iwidth * d.location_data.relative_bounding_box.xmin)
        ymin = int(iheigth * d.location_data.relative_bounding_box.ymin)
        ymax = ymin + int(iheigth * d.location_data.relative_bounding_box.height)
        xmax = xmin + int(iwidth * d.location_data.relative_bounding_box.width)
        boxes.append([ymin, xmax, ymax, xmin])
    del(face_detection)
    return boxes

def LoadDirList(lang="ukr"):
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
            myfrlang.lang[lang]["LoadDirList"][0],
            myfrlang.lang[lang]["LoadDirList"][1].format(e.args[-1]))
        return None, fl
    else:
        dl = json.load(f)
        f.close()
        fl = True
        return dl, fl

# Записуємо до файлу "_dirlist.ini" дані про скановані каталоги


def SaveDirList(dl, lang="ukr"):
    """[Saves sсanned folders data - DirList dictionary, to the file JSON-type file _dirlist.ini]
    Legacy function

    Args:
        dl ([Dictionary]): [dictionary with path:date_time]
        lang : lang
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
            myfrlang.lang[lang]["SaveDirList"][0],
            myfrlang.lang[lang]["SaveDirList"][1] % dlnm)
        return
    else:
        json.dump(dl, f)
        f.close()
    return

# Обираємо теку для сканування наявності обличь у файлах зображень JPG, PNG


def sel_dir(rootwnd, Title, dl, notskipcheck, subd, lang="ukr"):
    """[Choose an image folder to scan while checking if it is already in DirList as scanned one]

    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
        Title ([str]): [Title for tkinter.tk.filedialog.askdirectory tk.messagebox]
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
            if tk.messagebox.askyesno(
                myfrlang.lang[lang]["sel_dir"][0],
                myfrlang.lang[lang]["sel_dir"][1] % dl.get(sel_dir_path)):
                if subd:
                    dl[sel_dir_path] = str(datetime.now().strftime(
                        "%Y-%m-%d %H.%M.%S")) + myfrlang.lang[lang]["sel_dir"][2]
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
                        "%Y-%m-%d %H.%M.%S")) + myfrlang.lang[lang]["sel_dir"][2]
                else:
                    dl[sel_dir_path] = str(
                        datetime.now().strftime(
                        "%Y-%m-%d %H.%M.%S"))
        return sel_dir_path

 
def put_virt_mask(image_basic, confid, mod5_68, executor, fl_MultyTh=False, fl_wanted_scan=False):
    """[Applying virtual medical masks of 4 types]

    Args:
        image_basic ([type]): [description]
        mod ([type]): [description]
        executor ([type]): [description]
        fl_MultyTh (bool, optional): [description]. Defaults to False.

    Returns:
        images [list]: [list of 5 images (np.array)]
        boxes [list]: [list of face boxes found on basic image]
    """    
    #make local functions - just to be stylish
    frfl = face_recognition.face_locations
    frfland = face_recognition.face_landmarks
    images = []
    #
    if fl_MultyTh:
        boxes = executor.submit(mp_boxes, image_basic, confid).result()
    else:
        boxes = mp_boxes(image_basic, confid)
    if not boxes:
        images.append([image_basic])
        return images, boxes
    if fl_wanted_scan:
        for box in boxes:
            images.append([image_basic])
        return images, boxes
    #convert BGR into RGB-colour
    rgb_image_basic_basic = cv2.cvtColor(image_basic, cv2.COLOR_BGR2RGB)
    #run on all boxes found at the image_basic
    #setting up colors
    blue_mask = (237, 234, 101)
    blue_mask_stripes = (242, 249, 170)
    black_mask = (17, 17, 17)
    black_mask_stripes = (42, 42, 42)
    white_resp_stripes = (220, 220, 220)
    white_resp = (250, 250, 250)
    resp_valve = (44, 191, 218)
    for box in boxes:
        image_6 = []
        rgb_image_basic = rgb_image_basic_basic.copy()
        image_6.append(rgb_image_basic.copy())
        basic_landmarks = frfland(rgb_image_basic,
                        [box],
                        mod5_68)
        #Making a simple mask model
        mask_list = []
        mask_list.extend([basic_landmarks[0].get("chin")[x] for x in range(1, 16)])
        mask_list.append(basic_landmarks[0]["nose_bridge"][1])
        mask = np.array(mask_list, np.int32)
        stripe_0_list = []
        stripe_0_list.append(basic_landmarks[0]["chin"][1])
        stripe_0_list.append(basic_landmarks[0]["nose_bridge"][1])
        stripe_0_list.append(basic_landmarks[0]["chin"][15])
        stripe_0 = np.array(stripe_0_list, np.int32)
        stripe_1_list = []
        stripe_1_list.append(basic_landmarks[0]["chin"][3])
        stripe_1_list.append(basic_landmarks[0]["nose_tip"][2])
        stripe_1_list.append(basic_landmarks[0]["chin"][13])
        stripe_1 = np.array(stripe_1_list, np.int32)
        stripe_2_list = []
        stripe_2_list.append(basic_landmarks[0]["chin"][4])
        stripe_2_list.append(basic_landmarks[0]["bottom_lip"][4])
        stripe_2_list.append(basic_landmarks[0]["chin"][12])
        stripe_2 = np.array(stripe_2_list, np.int32)
        valve_left_center = basic_landmarks[0]["top_lip"][6]
        valve_right_center = basic_landmarks[0]["top_lip"][0]
        valve_main_axes = int(
            (basic_landmarks[0]["bottom_lip"][4][1] - basic_landmarks[0]["nose_tip"][2][1]) * 0.8
            )
        valve_min_axes = int(valve_main_axes // 2)
        stripe_0_width = int((basic_landmarks[0]["nose_bridge"][2][1] - basic_landmarks[0]["nose_bridge"][1][1]) * 0.4)
        stripe_1_width = int((basic_landmarks[0]["nose_bridge"][3][1] - basic_landmarks[0]["nose_bridge"][1][1]) * 0.6)
        stripe_2_width = stripe_0_width
    #Applying digital blue mask
        image_blue_mask = cv2.drawContours(rgb_image_basic, [mask], -1, blue_mask, thickness=cv2.FILLED)
        image_blue_mask = cv2.polylines(image_blue_mask, [stripe_0], False, blue_mask_stripes, thickness=stripe_0_width)
        image_blue_mask = cv2.polylines(image_blue_mask, [stripe_1], False, blue_mask_stripes, thickness=stripe_1_width)
        image_blue_mask = cv2.polylines(image_blue_mask, [stripe_2], False, blue_mask_stripes, thickness=stripe_2_width)
        image_6.append(image_blue_mask.copy())
    #Applying digital black mask
        image_black_mask = cv2.drawContours(rgb_image_basic, [mask], -1, black_mask, thickness=cv2.FILLED)
        image_black_mask = cv2.polylines(image_black_mask, [stripe_0], False, black_mask_stripes, thickness=stripe_0_width)
        image_black_mask = cv2.polylines(image_black_mask, [stripe_1], False, black_mask_stripes, thickness=stripe_1_width)
        image_black_mask = cv2.polylines(image_black_mask, [stripe_2], False, black_mask_stripes, thickness=stripe_2_width)
        image_6.append(image_black_mask.copy())
     #Applying digital white mask
        image_white_mask = cv2.drawContours(rgb_image_basic, [mask], -1, white_resp, thickness=cv2.FILLED)
        image_white_mask = cv2.polylines(image_white_mask, [stripe_0], False, white_resp_stripes, thickness=stripe_0_width)
        image_white_mask = cv2.polylines(image_white_mask, [stripe_1], False, white_resp_stripes, thickness=stripe_1_width)
        image_white_mask = cv2.polylines(image_white_mask, [stripe_2], False, white_resp_stripes, thickness=stripe_2_width)
        image_6.append(image_white_mask.copy())
    #Applying digital respirator with left-side valve
        image_resp_left = cv2.drawContours(rgb_image_basic, [mask], -1, white_resp, thickness=cv2.FILLED)
        image_resp_left = cv2.polylines(image_resp_left, [stripe_0], False, white_resp_stripes, thickness=stripe_0_width)
        image_resp_left = cv2.polylines(image_resp_left, [stripe_1], False, white_resp_stripes, thickness=stripe_1_width)
        image_resp_left = cv2.polylines(image_resp_left, [stripe_2], False, white_resp_stripes, thickness=stripe_2_width)
        image_resp_left = cv2.ellipse(image_resp_left, valve_left_center, (valve_main_axes, valve_min_axes), 285, 0, 360, resp_valve, -1)
        image_6.append(image_resp_left.copy())
    #Applying digital respirator with right-side valve
        image_resp_right = cv2.drawContours(rgb_image_basic, [mask], -1, white_resp, thickness=cv2.FILLED)
        image_resp_right = cv2.polylines(image_resp_right, [stripe_0], False, white_resp_stripes, thickness=stripe_0_width)
        image_resp_right = cv2.polylines(image_resp_right, [stripe_1], False, white_resp_stripes, thickness=stripe_1_width)
        image_resp_right = cv2.polylines(image_resp_right, [stripe_2], False, white_resp_stripes, thickness=stripe_0_width)
        image_resp_right = cv2.ellipse(image_resp_right, valve_right_center,
                (valve_main_axes, valve_min_axes), 255, 0, 360, resp_valve, -1)
        image_6.append(image_resp_right.copy())
        #adding list of 6 images to the common images list
        images.append(image_6.copy())
        del(image_6)
        del(rgb_image_basic)
        del(image_blue_mask)
        del(image_black_mask)
        del(image_white_mask)
        del(image_resp_left)
        del(image_resp_right)
    del(frfl)
    del(frfland)
    return images, boxes


def make_encodings(parwnd,
                   entries,
                   confid,
                   njits,
                   f_pkl,
                   fcmnt,
                   fl_dir_comment,
                   fl_dir_cmnt_file_created,
                   dir_comment,
                   fl_sub_folders=False,
                   fl_wanted_scan=False,
                   lang="ukr"):
    """[makes face encodings. Returns number of faces found (cnt) and number of pictures proceeded (fcnt)]

    Args:
        parwnd ([Tkinter]): [Tkinter parent window]
        entries ([list]): [Face pictures. List of path-like entries]
        confid ([float]): [Face detection confidence]
        njits ([int]): [number of jitters during face encodings]
        f_pkl ([file]): Full path for PKL-data file.]
        fcmnt ([file]): [OPENED! (wt) ini-file for comments]
        fl_dir_comment ([boolean]): [True of additional comment is present]
        fl_dir_cmnt_file_created ([boolean]): [True if ini-file for comments being created]
        dir_comment ([str]): [string of additional comment]
        fl_sub_folders ([boolean]): [should be True if subfolder are included in scan]
        fl_wanted_scan ([boolean]): [should be True if "wanted" person scan is running]
        lang : lang
    """ 
    if os.path.exists(f_pkl):
        if not tk.messagebox.askyesno(
            myfrlang.lang[lang]["make_encodings"][0],
            myfrlang.lang[lang]["make_encodings"][1]):
            return 
    # making local copies of global funcs
    frlif = face_recognition.load_image_file
    # frfl = face_recognition.face_locations
    frfe = face_recognition.face_encodings
    # init multithread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    mod5_68 = "large"
    cnt = 0
    fcnt = 0
    appcurver = parwnd.title()
    facedic = Face_Dictionary(f_pkl, "save")
    # encoding cycle
    for entry in entries:
        parwnd.title(appcurver + myfrlang.lang[lang]["make_encodings"][2] % (cnt, fcnt))
        if fl_sub_folders:
            if not os.path.isfile(entry):
                continue
            else:
                imfile = entry
                imfile_comment = ""
        else:
            if (entry.name.split(".")[-1].lower() in ["bmp", "gif", "jpg", "jpeg", "png"]) and entry.is_file():
                imfile = entry.path
                imfile_comment = entry.name
            else:
                continue
        if fl_dir_comment and fl_dir_cmnt_file_created:
                print(imfile_comment, dir_comment, file=fcmnt, sep="\t", end="\n", flush=True)                    
        fcnt += 1
        if fl_MultyTh:
            try:
                image = executor.submit(frlif, imfile).result()
            except:
                continue
        else:
            try:
                image = frlif(imfile)
            except:
                continue
        # making list of images: original and 4 masked virtually
        images = []
        encies = []
        images, boxes = put_virt_mask(image, confid, mod5_68, executor, fl_MultyTh, fl_wanted_scan)
        if boxes:
            for box_index in range(len(boxes)):
                for image in images[box_index]:
                    if fl_MultyTh:
                        encies.extend(executor.submit(
                                frfe, image, known_face_locations=[boxes[box_index]],
                                num_jitters=njits, model=mod5_68).result())
                    else:
                        encies.extend(frfe(image, known_face_locations=[boxes[box_index]],
                                           num_jitters=njits, model=mod5_68))
                    for enc in encies:
                        facedic.Encodings.append(enc)
                        facedic.Names.append(imfile)
                        facedic.facelocs.append(boxes[box_index])
                    encies.clear()
                cnt += 1            
            boxes.clear()
    if fl_MultyTh:
        executor.shutdown(wait=False)
    facedic.save()
    facedic.destroy()
    del(facedic)
    del(frlif)
    del(frfe)
    return cnt, fcnt


def get_params(fl_dir_comment=True, lang="ukr"):
    #Defaults
    confid = 0.5
    njits = 1
    dir_comment = ""
    #
    answ = tk.simpledialog.askfloat(myfrlang.lang[lang]["get_params"][10],
                                    myfrlang.lang[lang]["get_params"][11],
                                    minvalue=0.0, maxvalue=1.0, initialvalue=confid)
    if answ not in [None, ""]:  # setting cobfidence for facecomp
        confid = answ
    else:
        return
    njits = tk.simpledialog.askinteger(myfrlang.lang[lang]["get_params"][4],
                                       myfrlang.lang[lang]["get_params"][5],
                                       minvalue=1, maxvalue=100, initialvalue=1)
    if not njits:
        return None
    # setting common comment for all pictures in the folder
    if fl_dir_comment:
        dir_comment = tk.simpledialog.askstring(
        myfrlang.lang[lang]["get_params"][8],
        myfrlang.lang[lang]["get_params"][9],
        initialvalue="")
        if dir_comment in ["", "None", None]:  #  do not create comments' file if no comments
            fl_dir_comment = False
    else:
        dir_comment = ""
    return confid, njits, fl_dir_comment, dir_comment

   
def facedic_load(dicfilename, lang="ukr"):
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
            myfrlang.lang[lang]["facedic_load"][0],
            myfrlang.lang[lang]["facedic_load"][1].format(e.args[-1]))
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
def optim(lang="ukr"):
    """[optimization of *.pkl face encodings data files: all 1 k ... 10M sized files to be consolidated.
    Less files - faster search]
    """
    # const: min and max sizes of data files to be consolidated
    pkl_min_sz = 1000
    pkl_max_sz = 10000000
    ###
    if not tk.messagebox.askyesno(
        myfrlang.lang[lang]["optim"][0],
        myfrlang.lang[lang]["optim"][1]):
        return
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        tk.messagebox.showwarning(myfrlang.lang[lang]["optim"][2],
                                  myfrlang.lang[lang]["optim"][3] % knwdbdir)
        return
    backupdir = os.path.join(os.path.join(knwdbdir, "_backup"))
    if not os.path.exists(backupdir):
        try:
            os.mkdir(backupdir)
        except OSError:
            tk.messagebox.showwarning(
                myfrlang.lang[lang]["optim"][4],
                myfrlang.lang[lang]["optim"][5] % backupdir)
            return
    # Optimization of v3 data files
    v3fd = Face_Dictionary()
    v3fcnt = 0
    entries = os.scandir(knwdbdir)
    for entry in entries:
        if entry.name.lower().startswith("v3-") and entry.name.lower(
            ).endswith(".pkl") and entry.is_file(
                ) and os.path.getsize(entry.path) > pkl_min_sz and os.path.getsize(entry.path) < pkl_max_sz:
            temp_fd = Face_Dictionary(entry.path, "load")  # Reading facedic
            v3fd.fd["encodings"].extend(temp_fd.fd["encodings"])
            v3fd.fd["names"].extend(temp_fd.fd["names"])
            v3fd.fd["locations"].extend(temp_fd.fd["locations"])
            try:
                shutil.move(entry.path, os.path.join(backupdir, entry.name))
            except:
                pass                   
            temp_fd.destroy()
            v3fcnt += 1
    if len(v3fd.fd["encodings"]) > 0:
        fn = os.path.join(knwdbdir, "v3-opt_" + str(datetime.now()).replace(":", ".") + ".pkl")
        v3fd.save_as(fn)
    v3fd.destroy()
        # optimization of old-school data files
    fd = Face_Dictionary()
    fcnt = 0
    entries = os.scandir(knwdbdir)
    for entry in entries:
        if (not entry.name.lower().startswith("v3-")) and entry.name.lower().endswith(".pkl") and entry.is_file(
            ) and os.path.getsize(entry.path) > pkl_min_sz and os.path.getsize(entry.path) < pkl_max_sz:
            temp_fd = Face_Dictionary(entry.path, "load")  # Reading facedic
            fd.fd["encodings"].extend(temp_fd.fd["encodings"])
            fd.fd["names"].extend(temp_fd.fd["names"])
            try:
                shutil.move(entry.path, os.path.join(backupdir, entry.name))
            except:
                pass                   
            temp_fd.destroy()
            fcnt += 1
    if len(fd.fd["encodings"]) > 0:
        fn = os.path.join(knwdbdir, "opt_" + str(datetime.now()).replace(":", ".") + ".pkl")
        fd.save_as(fn)
    fd.destroy()
    tk.messagebox.showinfo(myfrlang.lang[lang]["optim"][10],
                            myfrlang.lang[lang]["optim"][11] % (v3fcnt + fcnt, backupdir))
    return


def showdirlist(root, lang="ukr"):
    """[If DirList loaded from file outputs a tkinter window with scrillable text of DirList]

    Args:
        fl ([boolean]): [True if DirList was leaded from _dirlist.ini]
    """
    dl = {}
    fl = False
    dl, fl = LoadDirList()
    if fl:
        win = tk.Toplevel(root)
        win.title(myfrlang.lang[lang]["showdirlist"][0])
        text_area = scrolledtext.ScrolledText(win,
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


def splitvid(root, lang="ukr"):
    """[Splits chosen video file into separate frames with face(s) for further face encoding.]

    Args:
        root ([tkinter.Tk]): [tkinter.Tk parent widget window]
    """    
    fl_MultyTh = False
    frfl = face_recognition.face_locations
    vidfile = tk.filedialog.askopenfilename(master=root, title=myfrlang.lang[lang]["splitvid"][0],
                           filetypes=[(myfrlang.lang[lang]["splitvid"][1], ['.mpeg', '.mpg', '.mp4', '.avi',
                                                       '.mkv'])])
    if vidfile in [".", "", None]:
        return
    framedir = os.path.join(os.path.dirname(vidfile), "frames")
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
                tk.messagebox.showinfo(myfrlang.lang[lang]["splitvid"][2],
                           myfrlang.lang[lang]["splitvid"][3])
                del(frfl)
                if fl_MultyTh:
                    executor.shutdown(wait=False)
                return
            faceframecnt += 1
    del(frfl)
    if fl_MultyTh:
        executor.shutdown(wait=False)
    tk.messagebox.showinfo(myfrlang.lang[lang]["splitvid"][4],
                           myfrlang.lang[lang]["splitvid"][5] % (faceframecnt, framecnt, vidfile))
    return
    

def showhelp(lang="ukr"):
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
                myfrlang.lang[lang]["showhelp"][0],
                myfrlang.lang[lang]["showhelp"][1])
        return

def showcurwdir(lang="ukr"):
    rep_dir = ""
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    rep_conf_fn = os.path.join(wntdbdir, "_dir.ini")
    try:
        dcf = open(rep_conf_fn, "r")
        rep_dir = json.load(dcf)
        dcf.close()
    except (IOError, EOFError) as e:
        tk.messagebox.showwarning(myfrlang.lang[lang]["showcurwdir"][0],
        myfrlang.lang[lang]["showcurwdir"][1])
    else:
        tk.messagebox.showinfo(myfrlang.lang[lang]["showcurwdir"][2],
                           myfrlang.lang[lang]["showcurwdir"][3] % rep_dir)        
        FILEBRWPATH = os.path.join(os.getenv("WINDIR"), "explorer.exe")
        subprocess.run([FILEBRWPATH, os.path.normpath(rep_dir)])
    return
