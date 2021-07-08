# -*- coding: utf-8 -*-
"""Special thanks to:
-	face_recognition by Adam Geitgey (https://github.com/ageitgey/face_recognition) under MIT License;
-	dlib by Davis E. King (https://github.com/davisking/dlib ) under BSL-1.0 License;
-	Mediapipe by Google (https://github.com/google/mediapipe) under Apache-2.0 License.
"""
__author__ = "Bohdan SOKRUT"
__www__ = 'https://github.com/bohdansok/Face_Recognition'
__version__ = '1.02'


import concurrent.futures
import os
import glob
from math import ceil
import pickle
from datetime import datetime
import mediapipe as mp
import face_recognition
import dlib
import xlsxwriter
from PIL import Image, ImageDraw
import numpy as np
import sqlite3
from shutil import copyfile


# making local copies of global funcs
frlif = face_recognition.load_image_file
frfl = face_recognition.face_locations
frfe = face_recognition.face_encodings
frfland = face_recognition.face_landmarks
frcf = face_recognition.compare_faces
frfd = face_recognition.face_distance
mp_face_detection = mp.solutions.face_detection

max_size = (1024, 768) # Maximum demensions of an image

    
class Face_Dictionary():
    """[The class contains all data structures to store in memory as well as load and save to file
    face encodings data, including picture file full path and face location for each face on every picture]
    """    
    def __init__(self, dicfilename="", mode="load"): #Create all data objects
        #dicfilename = self.dicfilename
        self.mode = mode
        self.dicfilename = dicfilename
        self.fl_Loaded = False
        self.fl_Saved = False
        self.Encodings = []
        self.Names = []
        self.facelocs = []
        self.fd = {"encodings": self.Encodings, "names": self.Names, "locations": self.facelocs}
        if bool(self.dicfilename) and self.mode == "load":
            self.fl_Loaded = self.load()
    
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
                print(f"Не можу знайти/прочитати файл кодувань обличь: {e}")
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
                print(f"Не можу створити файл бази даних {self.dicfilename}")
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
                print(f"Не можу створити файл бази даних {filename}")
                return False
            pickle.dump(self.fd, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
            self.fl_Saved = True
            return True   


"""
 Start of API section
"""

def API(input_image_path, user_ip, common_dir, dir_comment="", fl_use_dlib=True, confid=0.5, tol=0.45):
    """[Finds all image-type files in a particulr dirctory, recognizes faces and adds face' encodings
    and path to image into  temp dictionary and then save it at .pkl (Pickle-type) file]

    Args:
        fl_use_dlib ([bool]): [should be True to use dlib instead of Mediapipe frameworks]
    """
    ### vars - start
    fl_dir_comment = False
    if dir_comment:
        fl_dir_comment = True
    fl_dir_cmnt_file_created = False
    directory = input_image_path
    njits = 1
    fcmnt = None
    ### vars - end
    if fl_dir_comment:
        cmntfn = os.path.join(directory, "_facrecmnt.ini")
        try:
            fcmnt = open(cmntfn, "at")
        except:
            fl_dir_cmnt_file_created = False
        else:
            fl_dir_cmnt_file_created = True
    # check if _wanted folder available
    wntdbdir = input_image_path
    fn = os.path.join(wntdbdir, "wanted.pkl")
    entries = []
    entries.extend(glob.glob(directory + "/*.*", recursive=False))
    # calling face encodings maker. Vars cnt and fcnt are for compatability so far
    api_make_encodings(entries,
                       confid,
                        njits,
                        fn,
                        fcmnt,
                        fl_dir_comment,
                        fl_dir_cmnt_file_created,
                        dir_comment,
                        fl_use_dlib)
    if fl_dir_cmnt_file_created:
        fcmnt.close()
    """
    Search section: Searches wanted face encoding from WantedFaceDic among known faces in KnownFaceDic, 
    and outputs report as .xlsx file
    """    
    tmpwlist = []
    tmpetlist = []
    # internal wanted indiviuals
    vardescr_dic = {}

    fl_MultyTh = False
    fl_dir_cmnt_file_loaded = False
    fl_New_knowndir = True
    fl_vardescr_dic_Loaded = False
    # Configuring
    knwdbdir = os.path.join(os.path.join(
        os.getcwd(), "_DB"))  # setting path to _DB  CHANGE!!!
    # setting path to _Wanted
    fnw = os.path.join(wntdbdir, "wanted.pkl")  # trying to load wanted list
    wfd = Face_Dictionary(fnw, "load")  # Reading wantedfacedic
    if wfd.fl_Loaded:
        print("[INFO] WFD loaded")
    else:
        print("[INFO] WFD is not loaded!")
    wfdlen = len(wfd.fd["encodings"])
    # defining path to the current reports
    rep_dir = wntdbdir
    # init multythread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    #check if SQLite DB file is present
    fn_SQLite_DB = os.path.join(knwdbdir, "_LOCWANTED", "fr.db")
    if not os.path.exists(fn_SQLite_DB):
        print(f"[ERR] Відсутня база даних <fr.db> у теці {knwdbdir}")
    try:
        sqlite_connection = sqlite3.connect(fn_SQLite_DB)
        cursor = sqlite_connection.cursor()
    except Exception as error:
        print("[ERR] Error during SQLite connection", error)
        if (sqlite_connection):
            sqlite_connection.close()
            print("[INFO] SQLite connection is closed.")
    # loading various descriptions data
    vardescr = os.path.join(knwdbdir, "_LOCWANTED", "vardesc.ini")
    try:
        with open(vardescr, "rt") as f:
            for line in f:
                k = line.split("\t")[0]
                v = line.split("\t")[1]
                vardescr_dic[k] = v
            fl_vardescr_dic_Loaded = True
            #print(len(vardescr_dic))
    except:
        print("vardescr is not loaded")
        fl_vardescr_dic_Loaded = False
    #
    # перебираємо усі файли .pkl у папці _DB
    dfcnt = 0
    allfound = []
    entries = os.scandir(knwdbdir)
    for entry in entries:
        if (entry.name.lower().endswith(".pkl")) and (
            entry.name.lower() != "wanted.pkl") and (
            entry.name.lower() != "wantedall.pkl") and entry.is_file():
            dfcnt += 1
            kfd = Face_Dictionary(entry.path, "load")
            if kfd.fl_Loaded:
                print(f"[INFO] KFD {entry.name} loaded by {user_ip}")
            else:
                print(f"[INFO] KFD is not loaded by {user_ip}!")
            wcnt = 0
            # у кожному файлі даних шукаємо усі розшукувані пики. Так швидше.
            for wcnt in range(wfdlen):
                wenc = wfd.fd["encodings"][wcnt]
                wname = wfd.fd["names"][wcnt]
                try:
                    wloc = wfd.fd["locations"][wcnt]
                except:
                    fl_New_wanteddir = False
                    wloc = (0, 0, 0, 0)
                else:
                    fl_New_wanteddir = True
                if fl_MultyTh:
                    match = executor.submit(
                        frcf, kfd.fd["encodings"], wenc, tolerance=tol).result()
                else:
                    match = frcf(
                        kfd.fd["encodings"], wenc, tolerance=tol)
                if True in match:
                    matchedIdxs = [i for (i, b) in enumerate(match) if b]
                    for i in matchedIdxs:
                        st = ""
                        c1 = "file:///" + wname.replace("\\", "/")
                        t1 = os.path.normpath(wname)
                        c2 = "file:///" + \
                            str(kfd.fd["names"][i]).replace("\\", "/")
                        t2 = os.path.normpath(kfd.fd["names"][i])
                        # calculating distance between the faces. First arg should be a list
                        if fl_MultyTh:
                            distance = executor.submit(
                                frfd, [wenc], kfd.fd["encodings"][i]).result()
                        else:
                            distance = frfd(
                                [wenc], kfd.fd["encodings"][i])
                        try:
                            floc = kfd.fd["locations"][i]
                        except:
                            fl_New_knowndir = False
                            floc = (0, 0, 0, 0)
                        else:
                            fl_New_knowndir = True
                        # load additional comments FROM REFEREMCE photo folder
                        cmntfn = os.path.join(
                            os.path.dirname(t2), "_facrecmnt.ini")
                        try:
                            cmtf = open(cmntfn, "rt")
                        except:
                            fl_dir_cmnt_file_loaded = False
                        else:
                            dir_coms = {}
                            for line in cmtf:
                                dir_coms[line.split("\t")[0]] = line.split("\t")[
                                    1]
                            fl_dir_cmnt_file_loaded = True
                            cmtf.close()
                        #gathering data from different data sources
                        if (t2.find("Pics_Folders") != -1) or (t2.find("Nautil_Photo_ID1") != -1):
                            # reading from loaded Posv_Dir
                            sqln = str(os.path.split(t2)[1]).removesuffix(".jpg")
                            try:
                                cursor.execute(
                                "SELECT * FROM Personal_data WHERE fileid=:qustr",
                                {"qustr": sqln})
                                sqlite_connection.commit()
                                rows = cursor.fetchall()
                                if rows:
                                    for row in rows:
                                        st = " ".join([st, row[2]]).replace("^", "'").replace("&", '"')
                            except Exception as edb:
                                print(f"[ERR] Error while getting SQL data: {edb}")
                                st = "Дані відсутні."
            # get data from various descriptions
                        if fl_vardescr_dic_Loaded:
                            for k in vardescr_dic.keys():
                                if (t2.find(k) != -1):
                                    vardescr_st = vardescr_dic.get(k)
                                    if not vardescr_st in ["", "None", None]:
                                        st = " ".join([st, vardescr_st])
                        if not st:
                            st = "Дані відсутні."
                        extst = ""
                        if fl_dir_cmnt_file_loaded:
                            extst = str(dir_coms.get(t2.rpartition("\\")[2]))
                        st = " ".join(
                            [st, "Дод. коментар:", extst.replace("\n", "")])
                        if fl_dir_cmnt_file_loaded:
                            del(dir_coms)
                        allfound.append([c1, t1, c2, t2, st, floc, wloc,
                                         "".join([str(100 - int(distance[0] * 100)), "%"])])
    if (sqlite_connection):
        sqlite_connection.close()
    if fl_MultyTh:
        executor.shutdown(wait=False)
    if len(allfound) > 0:
        #destroying objects
        wfd.destroy()
        kfd.destroy()
        os.remove(fnw)
        # creatin report's files
        xlxfn = os.path.join(rep_dir, "Report_" + str(datetime.now()).replace(
            ":", "").replace(" ", "").replace(".", "") + ".xlsx")  # xlsx
        xlxfn_copy = os.path.join(common_dir, os.path.split(xlxfn)[1])
        wsx = xlsxwriter.Workbook(xlxfn)
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
        wrksx.set_column(0, 0, 33, cell_wrap)
        wrksx.set_column(1, 3, 33)
        #wrksx.set_column(2, 3, 27)
        wrksx.set_column(4, 4, 30, cell_wrap)
        wrksx.set_column(5, 5, 11, cell_wrap)
        wrksx.write(0, 0, "Звіт створено " + str(datetime.now().strftime(
            "%Y-%m-%d %H.%M.%S")) + f" з використанням FR Lan client {__version__}", cell_bold)
        wrksx.write(1, 0, "Задана точність: " + str(tol), cell_bold)
        #wrksx.write(3, 0, "Файл зображення розшук. особи", cell_bold)
        wrksx.write(3, 0, "Фото розшук. особи", cell_bold)
        wrksx.write(3, 1, "Обличчя розшук. особи", cell_bold)
        wrksx.write(3, 2, '"Еталонне" обличчя', cell_bold)
        wrksx.write(3, 3, '"Еталонне" зображення', cell_bold)
        #wrksx.write(3, 5, "Файл еталонного зображення", cell_bold)
        wrksx.write(3, 4, "Інформація про особу.", cell_bold)
        wrksx.write(3, 5, "Схожість, %", cell_bold)
        ###
        xlcnt = 4  # starting row at XLSX-sheet
        for r in allfound:
            wrksx.set_row(xlcnt, 175)  # висота рядка
            #wrksx.write(xlcnt, 0, r[0], cell_url)
            #wrksx.write(xlcnt, 5, r[2], cell_url)
            wrksx.write(xlcnt, 4, r[4])
            wrksx.write(xlcnt, 5, r[7])
            # thumbnails:
            try:
                im = Image.open(r[1])
                im = im.convert("RGB")
                im.thumbnail(max_size)
                if fl_New_wanteddir:
                    t1t = "".join([r[1], str(r[6]), str(datetime.now()).replace(":", ""),
                                   "_241.jpg"])  # ескізу для gif-формату не буде
                    t1tcr = "".join([r[1], str(r[6]), str(
                        datetime.now()).replace(":", ""), "_cr1.jpg"])
                    imcr = im.crop((r[6][3] - 3, r[6][0] - 3,
                                   r[6][1] + 3, r[6][2] + 3))
                    draw = ImageDraw.Draw(im)
                    # r[5] is tuple (top, right, bottom, left) order
                    draw.rectangle((r[6][3] - 3, r[6][0] - 3, r[6][1] + 3, r[6][2] + 3),
                                   outline="red", width=4)  # top, left, right, bottom
                    im.thumbnail((240, 240))
                    im.save(t1t)
                    imcr.thumbnail((192, 192))
                    imcr.save(t1tcr)
                    tmpwlist.append(t1t)
                    tmpwlist.append(t1tcr)
                    wrksx.insert_image(xlcnt, 0, t1t, {'object_position': 1})
                    wrksx.insert_image(xlcnt, 1, t1tcr, {'object_position': 1})
                else:
                    t1t = "".join([r[1], str(r[6]), str(datetime.now()).replace(":", ""),
                                   "_241.jpg"])  # ескізу для gif-формату не буде
                    im.thumbnail((240, 240))
                    im.save(t1t)
                    tmpwlist.append(t1t)
                    wrksx.insert_image(xlcnt, 0, t1t, {'object_position': 1})
            except:
                wrksx.write(xlcnt, 0, "Ескізу не буде")
                wrksx.write(xlcnt, 1, "Ескізу не буде")
            try:
                im = Image.open(r[3])
                im = im.convert("RGB")
                if fl_New_knowndir:
                    t2t = "".join([r[3], str(r[5]), str(datetime.now()).replace(":", ""),
                                   "_242.jpg"])  # ескізу для gif-формату не буде
                    t2tcr = "".join([r[3], str(r[5]), str(
                        datetime.now()).replace(":", ""), "_cr2.jpg"])
                    imcr = im.crop((r[5][3] - 3, r[5][0] - 3,
                                   r[5][1] + 3, r[5][2] + 3))
                    draw = ImageDraw.Draw(im)
                    # r[5] is tuple (top, right, bottom, left) order
                    draw.rectangle((r[5][3] - 3, r[5][0] - 3, r[5][1] + 3, r[5][2] + 3),
                                   outline="lightgreen", width=4)  # top, left, right, bottom
                    im.thumbnail((240, 240))
                    im.save(t2t)
                    imcr.thumbnail((192, 192))
                    imcr.save(t2tcr)
                    tmpetlist.append(t2t)
                    tmpetlist.append(t2tcr)
                    # wrksx.insert_image(xlcnt, 2, t2t, {'object_position': 1}) # old style w/o cropped thumbs
                    wrksx.insert_image(xlcnt, 2, t2tcr, {'object_position': 1})
                    wrksx.insert_image(xlcnt, 3, t2t, {'object_position': 1})
                else:
                    t2t = "".join([r[3], str(r[5]), str(datetime.now()).replace(":", ""),
                                   "_242.jpg"])  # ескізу для gif-формату не буде
                    im.thumbnail((240, 240))
                    im.save(t2t)
                    tmpetlist.append(t2t)
                    # wrksx.insert_image(xlcnt, 2, t2t, {'object_position': 1}) # old style w/o cropped thumbs
                    wrksx.insert_image(xlcnt, 3, t2t, {'object_position': 1})
            except Exception as e:
                print(e)
                wrksx.write(xlcnt, 2, "Ескізу не буде")
                wrksx.write(xlcnt, 3, "Ескізу не буде")
            xlcnt += 1
    # clear and close
        wsx.close()
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
        if wfdlen > 1:
            wfdlen = ceil(wfdlen / 2)
        print(f"[INFO] Searched for {wfdlen} face(s) at {dfcnt} data files. Report saved to {xlxfn}")
        copyfile(xlxfn, xlxfn_copy)
        return True, f"Проведено пошук {wfdlen} моделей обличя(чь) у {dfcnt} файлах даних.", xlxfn
    
    else:
        del(allfound)
        if wfdlen > 1:
            wfdlen = ceil(wfdlen / 2)
        print(f"[INFO] Searched for {wfdlen} face(s) at {dfcnt} data files. Found nothing")
        return False, f"Проведено пошук {wfdlen} моделей обличя(чь) у {dfcnt} файлах даних. Збігів не знайдено", ""
    
    

def api_make_encodings(entries,
                   confid,
                   njits,
                   f_pkl,
                   fcmnt,
                   fl_dir_comment,
                   fl_dir_cmnt_file_created,
                   dir_comment,
                   fl_use_dlib):
    """[makes face encodings. Returns number of faces found (cnt) and number of pictures proceeded (fcnt)]

    Args:
        entries ([list]): [Face pictures. List of path-like entries]
        confid ([float]): [Face detection confidence]
        njits ([int]): [number of jitters during face encodings]
        f_pkl ([file]): Full path for PKL-data file.]
        fcmnt ([file]): [OPENED! (wt) ini-file for comments]
        fl_dir_comment ([bool]): [True if additional comment is present]
        fl_dir_cmnt_file_created ([bool]): [True if ini-file for comments being created]
        dir_comment ([str]): [string of additional comment]
        fl_use_dlib ([bool]): [should be True to use dlib instead of Mediapipe frameworks]
    """ 
    # init multithread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    mod5_68 = "large"
    facedic = Face_Dictionary(f_pkl, "save")
    # encoding cycle
    for entry in entries:
        if (entry.rsplit(".", 1)[-1].lower() in ["bmp", "gif", "jpg", "jpeg", "png"]) and os.path.isfile(entry):
                imfile = entry
                imfile_comment = os.path.split(entry)[1]
        else:
            continue
        if fl_dir_comment and fl_dir_cmnt_file_created:
                    print(imfile_comment, dir_comment, file=fcmnt, sep="\t", end="\n", flush=True)                    
        if fl_MultyTh:
            try:
                image = executor.submit(Image.open, imfile).result()
                image.thumbnail(max_size)
                image = np.array(image)
                #crop to image tp 1024x768
            except Exception as e:
                print("[ERR]", e)
        else:
            try:
                image = Image.open(imfile)
                image.thumbnail(max_size)
                image = np.array(image)
                #crop to image tp 1024x768
            except Exception as e:
                print("[ERR]", e)
        # making list of images: origin
        boxes = mp_boxes(image, confid=confid, fl_use_dlib=fl_use_dlib)
        if boxes:
            for box in boxes:
                if fl_MultyTh:
                    facedic.Encodings.append(executor.submit(
                                frfe, image, known_face_locations=[box],
                                num_jitters=njits, model=mod5_68).result()[0])
                else:
                    facedic.Encodings.append(frfe(image, known_face_locations=[box],
                                           num_jitters=njits, model=mod5_68)[0])
                facedic.Names.append(imfile)
                facedic.facelocs.append(box)
                # encodimg all gaves on image
        boxes.clear()
    if fl_MultyTh:
        executor.shutdown(wait=False)
    facedic.save()
    facedic.destroy()
    del(facedic)
    return
"""
 End of API section
"""


def mp_boxes(image, confid=0.5, fl_use_dlib=True):
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
    boxes = []
    if fl_use_dlib:
        if dlib.DLIB_USE_CUDA: #tryin to use CNN on GPU first
            try:
                boxes = frfl(image, number_of_times_to_upsample=1, model="cnn")
                print(f"[INFO] dlib CNN being used and found {len(boxes)} face box")
            except:
                boxes = frfl(image, number_of_times_to_upsample=1, model="hog")
                print(f"[INFO] dlib HOG being used and found {len(boxes)} face box")
        else:
                boxes = frfl(image, number_of_times_to_upsample=1, model="hog")
                print(f"[INFO] dlib HOG being used and found {len(boxes)} face box")
    
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=confid)
    iheigth, iwidth = image.shape[:2]
    results = face_detection.process(image)
    if results.detections:
    # further with  results.detections:
        for d in results.detections:
            xmin = int(iwidth * d.location_data.relative_bounding_box.xmin)
            ymin = int(iheigth * d.location_data.relative_bounding_box.ymin)
            ymax = ymin + int(iheigth * d.location_data.relative_bounding_box.height)
            xmax = xmin + int(iwidth * d.location_data.relative_bounding_box.width)
            boxes.append([ymin, xmax, ymax, xmin])
    del(face_detection)
    if boxes:
        print(f"[INFO] Mediapipe addded some and now found {len(boxes)} face boxes")
        print(boxes)
        return boxes
    else:
        return None
