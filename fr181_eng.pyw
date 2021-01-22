# Author - Bohdan SOKRUT
# https://github.com/bohdansok/Face_Recognition
##
import face_recognition, os, pickle, os.path, glob, shutil
import json
import tkinter as tk
import xlsxwriter
import concurrent.futures
from tkinter import filedialog, simpledialog
from tkinter import messagebox
from tkinter import scrolledtext
from datetime import datetime
from PIL import Image


## Global vars - Start
appcurver = "Faces Recognition 1.81 by Bohdan SOKRUT and Python 3.8, dlib, face_recognition"
Dir_List = {}
fl_Dir_list_Saved = False
fl_Dir_List_Loaded = False
## Global vars - End
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
    if os.path.exists(dlnm):
        try:
            f = open(dlnm, "r")
            dl = json.load(f)
            f.close()
            fl = True
        except (IOError, EOFError) as e:
            tk.messagebox.showwarning("Attention!", "Can't fins/read scanned image folders data file: {}".format(e.args[-1]))
            return
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
        dltmp = json.load(f)
        f.close()
        dl.update(dltmp)
        del(dltmp)
    except:
        pass
    try:
        f = open(dlnm, "w")
        json.dump(dl, f)
        f.close()
    except OSError:
        tk.messagebox.showwarning("Увага!", "Не можу записати дані про скановані теки %s" % dlnm)
        return
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
    sel_dir_path = tk.filedialog.askdirectory(parent=rootwnd, title=Title, mustexist=True)
    if sel_dir_path in [".", "", None]:
        return
    else:
        if sel_dir_path in dl and notskipcheck: # check if selected path is among already scanned list and flag to check is True
            if tk.messagebox.askyesno("Attention!", "The folder %s has been already scanned. Proceed?" % dl.get(sel_dir_path)):
                if subd:
                    dl[sel_dir_path] = str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")) + " (with subfolders)"
                else:
                    dl[sel_dir_path] = str(datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
                return sel_dir_path
            else:
                sel_dir_path = sel_dir(rootwnd, Title, dl, notskipcheck, subd)
                return sel_dir_path
        else:
            if sel_dir_path != None:
                if subd:
                    dl[sel_dir_path] = str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")) + " (with subfolders)"
                else:
                    dl[sel_dir_path] = str(datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
        return sel_dir_path

def dir_load_allimg(parwnd):
    """[Finds all image-type files in a particulr image folder, recognizes faces and adds face' encodings
    and pathes to the images into at dictionary and then saves it at .pkl (Pickle-type) file]
    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """    
    knownEncodings = []
    knownNames = []
    fl_MultyTh = False
    mod = "hog"
    answ = tk.simpledialog.askinteger("Choose a FR Math model", "1 - HOG (faster), 2- CNN (more accurate):",
                               minvalue=1, maxvalue=2, initialvalue=1)
    if answ != None: # choose a Math FR model
        if answ == 1: mod = "hog"
        if answ == 2: mod = "cnn"
    else:
        mod = "hog"
    directory = sel_dir(parwnd, "Select a folder with reference pictures", Dir_List, True, False)
    if directory in [".", "", None]:
        del(knownNames)
        del(knownEncodings)
        return
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        try:
            os.mkdir(knwdbdir)
        except OSError:
            tk.messagebox.showwarning("Attention!", "Can't create working folder %s" % knwdbdir)
            del(knownNames)
            del(knownEncodings)
            return
    fn = os.path.join(knwdbdir, str(datetime.now()).replace(":",".") + ".pkl")
    try:
        f = open(fn, "wb")
    except OSError:
            tk.messagebox.showwarning("Attention!","Can't create face database file %s" % fn)
            del(knownNames)
            del(knownEncodings)
            return
    cnt = 0
    fcnt = 0
    frlif = face_recognition.load_image_file
    frfl = face_recognition.face_locations
    frfe = face_recognition.face_encodings
    #init multythread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    entries = os.scandir(directory)
    for entry in entries:
        parwnd.title(appcurver + " - added %d face(s) from %d pictures..." % (cnt, fcnt))
        if (entry.name.split(".")[-1].lower() in ["bmp", "gif", "jpg", "jpeg", "png"]) and entry.is_file():
            fcnt += 1
            if fl_MultyTh: # trying to use MultyThreads
                image = executor.submit(frlif, entry.path).result()
                boxes = executor.submit(frfl, image, model= mod).result()
            else:
                image = frlif(entry.path)
                boxes = frfl(image, model= mod) # maybe cnn - more accurate and use GPU/CUDA,
            if len(boxes) > 0: #more then 1 face in 1 pic - various face encodds' with the same oic file
                if fl_MultyTh:
                    encies = executor.submit(frfe, image, boxes).result()
                else:
                    encies = frfe(image, boxes)
                for enc in encies:
                    knownEncodings.append(enc)
                    knownNames.append(entry.path)
                    cnt += 1
    del(frlif)
    del(frfl)
    del(frfe)
    del(entries)
    # shutdowm multythread session
    if fl_MultyTh: executor.shutdown(wait=False)
    data = {}
    data = {"encodings": knownEncodings, "names": knownNames}
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    SaveDirList(Dir_List)
    fl_Dir_List_Saved = True
    del(data)
    del(knownNames)
    del(knownEncodings)
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
    allimgf = []
    mod = "hog"
    fl_MultyTh = False
    answ = tk.simpledialog.askinteger("Choose a FR Math model", "1 - HOG (faster), 2- CNN (more accurate):",
                               minvalue=1, maxvalue=2, initialvalue=1)
    if answ != None: # choosing model
        if answ == 1: mod = "hog"
        if answ == 2: mod = "cnn"
    else:
        mod = "hog"
    directory = sel_dir(parwnd, "Select a folder with reference pictures to scan (with subfoders)", Dir_List, True, True)
    if directory in [".", "", None]:
        del(allimgf) #clearing trash
        del(knownNames)
        del(knownEncodings)
        return
    ## creating workin folders
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        try:
            os.mkdir(knwdbdir)
        except OSError:
            tk.messagebox.showwarning("Attention!", "Can't create working folder %s" % knwdbdir)
            del(allimgf) #clearing trash
            del(knownNames)
            del(knownEncodings)
            return
    fn = os.path.join(knwdbdir, str(datetime.now()).replace(":",".") + ".pkl")
    try:
        f = open(fn, "wb")
    except OSError:
            tk.messagebox.showwarning("Attention!","Can't create face database file %s" % fn)
            del(allimgf) #clearing trash
            del(knownNames)
            del(knownEncodings)
            return
    cnt = 0
    fcnt = 0
    # creating local objects - functions
    frlif = face_recognition.load_image_file
    frfl = face_recognition.face_locations
    frfe = face_recognition.face_encodings
    #init multythread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    ## creating list of all images in the dir and subdirs
    allimgf.extend(glob.glob(directory + "/**/*.jpg", recursive = True))
    allimgf.extend(glob.glob(directory + "/**/*.jpeg", recursive = True))
    allimgf.extend(glob.glob(directory + "/**/*.png", recursive = True))
    allimgf.extend(glob.glob(directory + "/**/*.bmp", recursive = True))
    allimgf.extend(glob.glob(directory + "/**/*.gif", recursive = True))
    for entry in allimgf:
        if os.path.isfile(entry):
            parwnd.title(appcurver + " - added %d face(s) from %d pictures..." % (cnt, fcnt))
            fcnt += 1
            if fl_MultyTh:
                image = executor.submit(frlif, entry).result()
                boxes = executor.submit(frfl, image, model= mod).result()
            else:
                image = frlif(entry.path)
                boxes = frfl(image, model= mod) # maybe cnn - more accurate and use GPU/CUDA,
            if len(boxes) > 0: #more then 1 face in 1 pic - various face encodds' with the same oic file
                if fl_MultyTh:
                    encies = executor.submit(frfe, image, boxes).result()
                else:
                    encies = frfe(image, boxes)
                for enc in encies:
                    knownEncodings.append(enc)
                    knownNames.append(entry)
                    cnt += 1
        else:
            continue
    del(allimgf)
    del(frlif)
    del(frfl)
    del(frfe)
    data = {}
    data = {"encodings": knownEncodings, "names": knownNames}
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    del(data)
    del(knownEncodings)
    del(knownNames)
    # shutdowm multythread session
    if fl_MultyTh: executor.shutdown(wait=False)
    SaveDirList(Dir_List)
    fl_Dir_List_Saved = True
    tk.messagebox.showinfo("Information",
                           "Added %d face(s) from %d  pictures at %s. Saving encodings to file..." % (cnt, fcnt, directory)
                           )
    parwnd.title(appcurver)
    return

def dir_load_wantedimg(parwnd): # Loading and encoding wanted people
    """[Finds all image-type files in a particulr dirctory, recognizes faces and adds face' encodings
    and path to image into  temp dictionary and then save it at .pkl (Pickle-type) file]
    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """    
    ### vars - start
    wantedEncodings = []
    wantedNames = []
    mod = "hog" #default for FR mathem. model
    fl_MultyTh = False
    ### vars - end
    answ = tk.simpledialog.askinteger("Choose a FR Math model", "1 - HOG (faster), 2- CNN (more accurate):",
                               minvalue=1, maxvalue=2, initialvalue=1)
    if answ != None: #setting tolerance for facecomp
        if answ == 1: mod = "hog"
        if answ == 2: mod = "cnn"
    directory = sel_dir(parwnd, "Choose a folder with the pistures of wanted individual(s)", Dir_List, False, False)
    if directory in [".", "", None]:
        del(wantedEncodings)
        del(wantedNames)
        return
   ### making local copies of global funcs
    frlif = face_recognition.load_image_file
    frfl = face_recognition.face_locations
    frfe = face_recognition.face_encodings
    #init multythread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    ### check if _wanted folder available
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    if not os.path.exists(wntdbdir):
        try:
            os.mkdir(wntdbdir)
        except OSError:
            tk.messagebox.showwarning("Attention!", "Can't create working foldeг %s" % wntdbdir)
            del(frlif)
            del(frfl)
            del(frfe)
            del(wantedEncodings)
            del(wantedNames)
            return
    fn = os.path.join(wntdbdir, "wanted.pkl")
    if os.path.exists(fn):
        if tk.messagebox.askyesno("Attention!", "Wanted individuals data file already exists. Replace?"):
            try:
                f = open(fn, "wb")
            except OSError:
                tk.messagebox.showwarning("Attention!", "Can't create face database file %s" % fn)
                del(frlif)
                del(frfl)
                del(frfe)
                del(wantedEncodings)
                del(wantedNames)
                return
            cnt = 0
            fcnt = 0
            data = {}
            entries = os.scandir(directory)
            for entry in entries:
                parwnd.title(appcurver + " - added %d face(s) from %d pictures..." % (cnt, fcnt))
                if (entry.name.split(".")[-1].lower() in ["bmp", "gif", "jpg", "jpeg", "png"]) and entry.is_file():
                    fcnt += 1
                    if fl_MultyTh:
                        image = executor.submit(frlif, entry.path).result()
                        boxes = executor.submit(frfl, image, model= mod).result()
                    else:
                        image = frlif(entry.path)
                        boxes = frfl(image, model= mod) # maybe cnn - more accu and use GPU/CUDA,
                    if len(boxes) > 0:
                        if fl_MultyTh:
                            encies = executor.submit(frfe, image, boxes).result()
                        else:
                            encies = frfe(image, boxes)
                        for enc in encies:
                            wantedEncodings.append(enc)
                            wantedNames.append(entry.path)
                            cnt += 1
            data = {"encodings": wantedEncodings, "names": wantedNames}
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
             # writing the search set path to _dir.ini (JSON-type) file
            wssfn = os.path.join(wntdbdir, "_dir.ini")
            try:
                f = open(wssfn, "w")
                json.dump(directory, f)
                f.close()
            except OSError:
                tk.messagebox.showwarning("Attention!", "Can't write search options to file %s. Reports will be saved at the app's working folder" % wssfn)
            del(data)
            del(wantedEncodings)
            del(wantedNames)
            del(frlif)
            del(frfl)
            del(frfe)
            if fl_MultyTh: executor.shutdown(wait=False)
            tk.messagebox.showinfo('Information.',
                           "Added %d face(s) from %d  pistures at %s. Saving encodings to file..." % (cnt, fcnt, directory))
            parwnd.title(appcurver)
            return
        else:
            return
    else:
        try:
            f = open(fn, "wb")
        except OSError:
            tk.messagebox.showwarning("Attention!", "Can't create face database file %s" % fn)
            del(frlif)
            del(frfl)
            del(frfe)
            if fl_MultyTh: executor.shutdown(wait=False)
            return
        cnt = 0
        fcnt = 0
        data = {}
        entries = os.scandir(directory)
        for entry in entries:
            parwnd.title(appcurver + " - added %d face(s) from %d pictures..." % (cnt, fcnt))
            if (entry.name.split(".")[-1].lower() in ["bmp", "gif", "jpg", "jpeg", "png"]) and entry.is_file():
                fcnt += 1
                if fl_MultyTh:
                    image = executor.submit(frlif, entry.path).result()
                    boxes = executor.submit(frfl, image, model= mod).result()
                else:
                    image = frlif(entry.path)
                    boxes = frfl(image, model= mod) # maybe cnn - more accu and use GPU/CUDA,
                if len(boxes) > 0:
                    if fl_MultyTh:
                        encies = executor.submit(frfe, image, boxes).result()
                    else:
                        encies = frfe(image, boxes)
                    for enc in encies:
                        wantedEncodings.append(enc)
                        wantedNames.append(entry.path)
                        cnt += 1
        data = {"encodings": wantedEncodings, "names": wantedNames}
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()
        # writing the search set path to _dir.ini (JSON-type) file
        wssfn = os.path.join(wntdbdir, "_dir.ini")
        try:
            f = open(wssfn, "w")
            json.dump(directory, f)
            f.close()
        except OSError:
            tk.messagebox.showwarning("Attention!", "Can't write search options to file %s. Reports will be saved at the app's working folder" % wssfn)
        del(data)
        del(wantedEncodings)
        del(wantedNames)
        del(frlif)
        del(frfl)
        del(frfe)
        if fl_MultyTh: executor.shutdown(wait=False)
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
        tk.messagebox.showwarning("Attention!", "Can't find/read face encodings data file {}".format(e.args[-1]))
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

## optimization of *.pkl face encodings data files: all 1 k ... 10M files to be cosolidated.
## Less files - faster search
def optim():
    """[optimization of *.pkl face encodings data files: all 1 k ... 10M sized files to be cosolidated.
    Less files - faster search]
    """    
    Encodings = []
    Names = []
    # bigdic = {"enc": Encodings, "nms": Names}
    #const: min and max sizes of data files to be consolidated
    pkl_min_sz = 1000
    pkl_max_sz = 10000000
    ###
    if tk.messagebox.askyesno("Attention", "Small face encodings data files to be consolidated for faster face search. Proceed?"):
        knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
        if not os.path.exists(knwdbdir):
            tk.messagebox.showwarning("Attention!", "Can't find/read working folder %s" % knwdbdir)
            return
        backupdir = os.path.join(os.path.join(knwdbdir, "_backup"))
        if not os.path.exists(backupdir):
            try:
                os.mkdir(backupdir)
            except OSError:
                tk.messagebox.showwarning("Attention!", "Can't creat back-up folder %s" % backupdir)
                return
        bigdic = {}
        fcnt = 0
        entries = os.scandir(knwdbdir)
        for entry in entries:
            if entry.name.lower().endswith(".pkl") and entry.is_file() and os.path.getsize(entry.path) > pkl_min_sz and os.path.getsize(entry.path) < pkl_max_sz:
                td = {}
                td = facedic_load(entry.path) ## Reading facedic
                Encodings.extend(td["encodings"])
                Names.extend(td["names"])
                shutil.move(entry.path, backupdir)
                del(td)
                fcnt += 1
        if fcnt == 0:
            tk.messagebox.showwarning("Attention!", "No small data files found.")
            del(Encodings)
            del(Names)
            return
        fn = os.path.join(knwdbdir, "opt_" + str(datetime.now()).replace(":",".") + ".pkl")
        print(fn)
        try:
            f = open(fn, "wb")
        except OSError:
            tk.messagebox.showwarning("Attention!","Can't write data file %s. Mannualy move data files back from %s to %s." % (fn, backupdir, knwdbdir))
            del(Encodings)
            del(Names)
            return
        bigdic = {"encodings": Encodings, "names": Names}
        pickle.dump(bigdic, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()
        del(bigdic)
        del(Encodings)
        del(Names)
        tk.messagebox.showinfo('Information',
                           "Totally %d face encodings data files have been consolidated in %s. Back-up copies moved to %s." % (fcnt, fn, backupdir))
    return

## Main searcher
#
#
def pic_search(parwnd):
    """[Searches wanted face encoding from WantedFaceDic among known faces in KnownFaceDic, 
    and outputs reports as .txt and .xlsx files]
    Args:
    rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """    
    ### vars
    tmpwlist = []
    tmpetlist = []
    fl_rep_dir_default = False
    fl_MultyTh = False
    ###
    answ = tk.simpledialog.askfloat("Face recognition accuracy", "Less - more accurate (0<x<1, good (default) is 0.45):",
                               minvalue=0.000, maxvalue=1.000, initialvalue=0.45)
    if answ != None: #setting tolerance for facecomp
        tol = answ
    else:
        tol = 0.45    
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        tk.messagebox.showwarning("Attention!", "Can't find/read working folder %s" % knwdbdir)
        return
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    if not os.path.exists(wntdbdir):
        tk.messagebox.showwarning("Attention!", "Can't find/read working folder %s" % wntdbdir)
        return
    fnw = os.path.join(wntdbdir, "wanted.pkl")
    if not os.path.exists(fnw):
        tk.messagebox.showwarning("Attention!", "Can't find/read wanted individuals(s) data file %s. Please, scan the appropriate folder with pictures" % fnw)
        return
    ### defining path to the current reports
    rep_conf_fn = os.path.join(wntdbdir, "_dir.ini")
    if os.path.exists(rep_conf_fn):
        try:
            dcf = open(rep_conf_fn, "r")
            rep_dir = json.load(dcf)
            dcf.close()
            if not os.path.exists(rep_dir): fl_rep_dir_default = True # path to report folder is loaded and is nor blank
        except (IOError, EOFError) as e:
            fl_rep_dir_default = True
            tk.messagebox.showwarning("Attention!", "Can't find/read search options file: {}".format(e.args[-1]))
    else:
        fl_rep_dir_default = True
    ### creatin report's files
    if fl_rep_dir_default:
        try:
            txtfn = "Report_" + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")).replace(":",".") + ".txt"
            txtrep = open(txtfn, "wt")
        except (IOError, EOFError) as e:
            tk.messagebox.showwarning("Attention!", "Не можу записати файл звіту {}".format(e.args[-1]))
            return
        try:    
            xlxfn = "Report_" + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")).replace(":",".") + ".xlsx" #xlsx
            wsx = xlsxwriter.Workbook(xlxfn)
        except (IOError, EOFError) as e:
            tk.messagebox.showwarning("Attention!", "Can't write report file {}".format(e.args[-1]))
            return
    else:
        try:
            txtfn = os.path.join(rep_dir, "Report_" + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")).replace(":",".") + ".txt")
            txtrep = open(txtfn, "wt")
        except (IOError, EOFError) as e:
            tk.messagebox.showwarning("Attention!", "Can't write report file {}".format(e.args[-1]))
            return
        try:    
            xlxfn = os.path.join(rep_dir, "Report_" + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")).replace(":",".") + ".xlsx") #xlsx
            wsx = xlsxwriter.Workbook(xlxfn)
        except (IOError, EOFError) as e:
            tk.messagebox.showwarning("Attention!", "Can't write report file {}".format(e.args[-1]))
            return
    #init multythread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    # xlsx header
    wrksx = wsx.add_worksheet('Report ' + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")))
    wrksx.write(0, 0, "Report created " + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")) + " by %s" % appcurver)
    wrksx.write(1, 0, "Accuracy: " + str(tol))
    wrksx.write(3, 0, "Wanted individual picture file")
    wrksx.write(3, 1, "Wanted individual's picture thumbnail")
    wrksx.write(3, 2, "Reference individual's picture thumbnail")
    wrksx.write(3, 3, "Reference individual's picture file")
    wrksx.set_column(0, 0, 45) #width of columns
    wrksx.set_column(1, 2, 27)
    wrksx.set_column(3, 3, 45)
    ## txt header
    print("Report created ", str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")), " by %s" % appcurver, file=txtrep, end="\n", flush=False)
    print("Accuracy: ", str(tol), file=txtrep, end="\n", flush=False)
    print("Wanted individual picture file", "\t", "Reference individual's picture file", "\t", file=txtrep, end="\n", flush=False)
    ###
    WantedFaceDic = facedic_load(fnw) ## Reading wantedfacedic
    wfdlen = len(WantedFaceDic["encodings"])
    xlcnt = 4
    frcf = face_recognition.compare_faces
    ## перебираємо усі файли .pkl у папці _DB
    dfcnt = 0
    entries = os.scandir(knwdbdir)
    for entry in entries:
        parwnd.title(appcurver + " - found %d face(s) among %d reference data files" % (wfdlen, dfcnt))
        if (entry.name.lower().endswith(".pkl")) and entry.is_file():
            dfcnt +=1
            td = {}
            td = facedic_load(entry.path) ## Reading wantedfacedic
            if td != None:
                 KnownFaceDic = td
                 del(td)
            else:
                del(td)
                continue
            wcnt = 0
            for wcnt in range(wfdlen):# finding wanted encodings at every loaded data file
                wenc = WantedFaceDic["encodings"][wcnt]
                wname = WantedFaceDic["names"][wcnt]
                if fl_MultyTh:
                    match = executor.submit(frcf, KnownFaceDic["encodings"], wenc, tolerance=tol).result()
                else:
                    match = frcf(KnownFaceDic["encodings"], wenc, tolerance=tol)
                if True in match:
                    matchedIdxs = [i for (i, b) in enumerate(match) if b]
                    for i in matchedIdxs:
                        c1 = "file:///" + wname.replace("\\", "/")
                        t1 = os.path.normpath(wname)
                        c2 = "file:///" + str(KnownFaceDic["names"][i]).replace("\\", "/")
                        t2 = os.path.normpath(KnownFaceDic["names"][i])
                        print(os.path.normpath(wname), "\t",  os.path.normpath(KnownFaceDic["names"][i]),
                               "\t", file=txtrep, end="\n", flush=False)
                            #xlsx
                        wrksx.write_url(xlcnt, 0, c1, string=t1)
                        wrksx.write_url(xlcnt, 3, c2, string=t2)
                        wrksx.set_row(xlcnt, 142)
                        try:
                                im = Image.open(t1)
                                im.thumbnail((192, 192))
                                t1t = t1 + "_192.jpg"
                                im.save(t1t)
                                tmpwlist.append(t1t)
                                wrksx.insert_image(xlcnt,
                                                   1,
                                                   t1t,
                                                   {'object_position': 1}
                                                   )
                                #
                        except:
                                wrksx.write(xlcnt,
                                            1,
                                            "Ескізу не буде"
                                            )
                        try:
                                im = Image.open(t2)
                                im.thumbnail((192, 192))
                                t2t = t2 + "_192.jpg"
                                im.save(t2t)
                                tmpetlist.append(t2t)
                                wrksx.insert_image(xlcnt,
                                                   2,
                                                   t2t,
                                                   {'object_position': 1}
                                                   )
                                #
                        except:
                                wrksx.write(xlcnt,
                                            2,
                                            "Ескізу не буде"
                                            )
                        xlcnt += 1
    wsx.close()
    txtrep.flush()
    txtrep.close()
    if fl_MultyTh: executor.shutdown(wait=False)
    del(WantedFaceDic)
    del(KnownFaceDic)
    del(frcf)
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
    tk.messagebox.showinfo('Information', "Done search of %d face(s) among %d reference data file(s). Reports saved at %s and %s" % (wfdlen, dfcnt, txtfn, xlxfn))
    parwnd.title(appcurver)
    return

def showdirlist(fl):
    """[If DirList loaded from file outputs a tkinter window with scrillable text of DirList]

    Args:
        fl ([boolean]): [True if DirList was leaded from _dirlist.ini]
    """    
    if fl:
        f = open("_dirlist.ini", "rt")
        dl = {}
        dl = json.load(f)
        f.close()
        win = tk.Tk()
        win.title("Список сканованих папок з еталонними фото")
        text_area = tk.scrolledtext.ScrolledText(win,  
                                      wrap = tk.WORD,  
                                      width = 126,  
                                      height = 10,  
                                      font = ("Times New Roman", 
                                              12)) 
        for k in dl.keys():
                s = str(k).ljust(65) + str(dl[k]).rjust(23) + "\n"
                text_area.insert(tk.INSERT, s)
        del(dl)
        text_area.configure(state ='disabled') 
        text_area.focus()
        text_area.pack()
        win.mainloop()
    return

## GUI
wnd = tk.Tk(screenName=appcurver)
wnd.title(appcurver)
dl = {}
dl, fl_Dir_List_Loaded = LoadDirList()
if fl_Dir_List_Loaded: Dir_List = dl
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
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: showdirlist(fl_Dir_List_Loaded))
but_opt = tk.Button(master=frame4,
                   text='Face database optimization',
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=optim)
but_ab.pack(side=tk.LEFT)
but_opt.pack(side=tk.RIGHT)
but_dir.pack(side=tk.RIGHT)
frame4.pack()
##
wnd.mainloop()