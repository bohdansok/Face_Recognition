# first attemt to create a rec and comp app
# Author - Bohdan SOKRUT
# https://github.com/bohdansok/Face_Recognition
##
import face_recognition, os, pickle, os.path, glob
import json
import tkinter as tk
from tkinter import filedialog, simpledialog
from tkinter import messagebox
from tkinter import scrolledtext
from datetime import datetime
from PIL import Image
import xlsxwriter

## Global vars - Start
appcurver = "Faces Recognition 1.5 by Bohdan SOKRUT and Python 3.9, dlib, face_recognition"
Dir_List = {}
fl_Dir_list_Saved = False
fl_Dir_List_Loaded = False
## Global vars - End
##
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
    if os.path.exists(dlnm):
        try:
            f = open(dlnm, "r")
            dl = json.load(f)
            f.close()
            fl = True
        except (IOError, EOFError) as e:
            tk.messagebox.showwarning("Увага!", "Не можу знайти/прочитати файл даних сканованих папок: {}".format(e.args[-1]))
            #print("Не можу знайти файл даних сканованих папок: {}".format(e.args[-1]))
            return
    #else:
        # tk.messagebox.showinfo('Інформація','Дані про раніше скановані папки відсутні.')
       # print("Дані про раніше скановані папки відсутні.'")
    return dl, fl

# Записуємо до файлу "_dirlist.ini" дані про скановані каталоги
def SaveDirList(dl):
    """[Saves DirList dictionary to file JSON-type file _dirlist.ini]

    Args:
        dl ([Dictionary]): [dictionary with path:date_time]
    """    
    dlnm = "_dirlist.ini"
    try:
        f = open(dlnm, "w")
        json.dump(dl, f)
        f.close()
    except OSError:
        #print ("Не можу записати список сканованих папок %s" % dlnm)
        tk.messagebox.showwarning("Увага!", "Не можу записати список сканованих папок %s" % dlnm)
        return
    return

# Обираємо каталог для сканування наявності облич у файлах зображень JPG, PNG
def sel_dir(rootwnd, Title, dl, notskipcheck, subd):
    """[GUI choos a directory to scan with check if is already in DirList as scanned one]

    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
        Title ([str]): [Title for tkinter.filedialog.askdirectory messagebox]
        dl ([dict]): [DirList]
        notskipcheck ([boolean]): [True to check if a selected directory is alreadu in DirList]
        subd ([boolean]): [True of a selected directory and all subdirectories to be scanned]

    Returns:
        [str]: [path to a directory to be scanned]
    """    
    sel_dir_path = tk.filedialog.askdirectory(parent=rootwnd, title=Title, mustexist=True)
    if sel_dir_path in [".", "", None]:
        return
    else:
        if sel_dir_path in dl and notskipcheck: # якщо шлях у списку сканованих і є флаг га перевірку
            if tk.messagebox.askyesno("Увага!", "Ця тека вже сканувлась %s. Повторити?" % dl.get(sel_dir_path)):
                if subd:
                    dl[sel_dir_path] = str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")) + " (з вклад. теками)"
                else:
                    dl[sel_dir_path] = str(datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
                return sel_dir_path
            else:
                sel_dir_path = sel_dir(rootwnd, Title, dl, notskipcheck, subd)
                return sel_dir_path
        else:
            if sel_dir_path != None:
                if subd:
                     dl[sel_dir_path] = str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")) + " (з вклад.теками)"
                else:
                    dl[sel_dir_path] = str(datetime.now().strftime("%Y-%m-%d %H.%M.%S"))
        return sel_dir_path

def dir_load_allimg(parwnd):
    """[Finds all image-type files in a particulr dirctory, recognizes faces and adds face' encodings
    and path to image into appropriated dictionary KnownFaceDic]

    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """    
    knownEncodings = []
    knownNames = []
    KnownFaceDic = {"encodings": knownEncodings, "names": knownNames}
    mod = "hog"
    answ = tk.simpledialog.askinteger("Оберіть матем. модель пошуку облич", "1 - HOG (швидше), 2- CNN (точніше):",
                               minvalue=1, maxvalue=2, initialvalue=1)
    if answ != None: # обираємо модель
        if answ == 1: mod = "hog"
        if answ == 2: mod = "cnn"
    else:
        mod = "hog"
    directory = sel_dir(parwnd, "Оберіть теку з еталонними фото", Dir_List, True, False)
    #print(directory)
    if directory in [".", "", None]: return
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        try:
            os.mkdir(knwdbdir)
        except OSError:
            tk.messagebox.showwarning("Увага!", "Не можу створити робочий каталог %s" % knwdbdir)
            #print ("Не можу створити робочий каталог %s" % knwdbdir)
            return
    fn = os.path.join(knwdbdir, str(datetime.now()).replace(":",".") + ".pkl")
    try:
        f = open(fn, "wb")
    except OSError:
            tk.messagebox.showwarning("Увага!","Не можу створити файл бази даних %s" % fn)
            #print ("Не можу створити файл бази даних %s" % fn)
            return
    cnt = 0
    fcnt = 0
    data = {}
    knownEncodings.clear()
    knownNames.clear()
    for entry in os.scandir(directory):
        parwnd.title(appcurver + " - вже додано %d облич(чя) з %d зображень..." % (cnt, fcnt))
        if (entry.name.split(".")[-1] in ["jpg", "jpeg", "png", "JPG", "JPEG", "PNG", "Jpg", "Jpeg", "Png"]) and entry.is_file():
            fcnt += 1
            image = face_recognition.load_image_file(entry.path)
            boxes = face_recognition.face_locations(image, model= mod) # maybe cnn - more accu and use GPU/CUDA,
            if len(boxes) > 0: #more then 1 face in 1 pic - various face encodds' with the same oic file
                        for enc in face_recognition.face_encodings(image, boxes):
                            knownEncodings.append(enc)
                            knownNames.append(entry.path)
                            cnt += 1
                            # print(cnt, entry.path)
                            # print(enc)
            # else:
            #         print(entry.path, 'Облич немає!')
    #print("Додано %d облич з %d зображень. Зберігаю кодування облич до файлу..." % (cnt, fcnt))
    tk.messagebox.showinfo('Інформація', "Додано %d облич з %d зображень. Зберігаю кодування облич до файлу..." % (cnt, fcnt))
    data = {"encodings": knownEncodings, "names": knownNames}
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    parwnd.title(appcurver)
    SaveDirList(Dir_List)
    fl_Dir_List_Saved = True
    return

def dir_load_allimg_sub(parwnd):
    """[Finds all image-type files in a particulr dirctory, recognizes faces and adds face' encodings
    and path to image into appropriated dictionary KnownFaceDic]

    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """    
    knownEncodings = []
    knownNames = []
    allimgf = []
    KnownFaceDic = {"encodings": knownEncodings, "names": knownNames}
    mod = "hog"
    answ = tk.simpledialog.askinteger("Оберіть матем. модель пошуку облич", "1 - HOG (швидше), 2- CNN (точніше):",
                               minvalue=1, maxvalue=2, initialvalue=1)
    if answ != None: # обираємо модель
        if answ == 1: mod = "hog"
        if answ == 2: mod = "cnn"
    else:
        mod = "hog"
    directory = sel_dir(parwnd, "Оберіть папку з еталонними фото (із вклад. теками)", Dir_List, True, True)
    #print(directory)
    if directory in [".", "", None]: return
    ## creating workin folders
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        try:
            os.mkdir(knwdbdir)
        except OSError:
            tk.messagebox.showwarning("Увага!", "Не можу створити робочий каталог %s" % knwdbdir)
            #print ("Не можу створити робочий каталог %s" % knwdbdir)
            return
    fn = os.path.join(knwdbdir, str(datetime.now()).replace(":",".") + ".pkl")
    try:
        f = open(fn, "wb")
    except OSError:
            tk.messagebox.showwarning("Увага!","Не можу створити файл бази даних %s" % fn)
            #print ("Не можу створити файл бази даних %s" % fn)
            return
    cnt = 0
    fcnt = 0
    data = {}
    knownEncodings.clear()
    knownNames.clear()
    ## creating list of all images in the dir and subdirs
    allimgf.extend(glob.glob(directory + "/**/*.jpg", recursive = True))
    allimgf.extend(glob.glob(directory + "/**/*.jpeg", recursive = True))
    allimgf.extend(glob.glob(directory + "/**/*.png", recursive = True))
    for entry in allimgf:
        if os.path.isfile(entry):
            parwnd.title(appcurver + " - вже додано %d облич(чя) з %d зображень..." % (cnt, fcnt))
            fcnt += 1
            image = face_recognition.load_image_file(entry)
            boxes = face_recognition.face_locations(image, model= mod) # maybe cnn - more accu and use GPU/CUDA,
            if len(boxes) > 0: #more then 1 face in 1 pic - various face encodds' with the same oic file
                        for enc in face_recognition.face_encodings(image, boxes):
                            knownEncodings.append(enc)
                            knownNames.append(entry)
                            cnt += 1
                            # print(cnt, entry)
                            # print(enc)
            # else:
            #         print(entry, 'Облич немає!')
        else:
            continue
    allimgf.clear()
   # print("Додано %d облич з %d зображень. Зберігаю кодування облич до файлу..." % (cnt, fcnt))
    tk.messagebox.showinfo('Інформація', "Додано %d облич з %d зображень. Зберігаю кодування облич до файлу..." % (cnt, fcnt))
    data = {"encodings": knownEncodings, "names": knownNames}
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    parwnd.title(appcurver)
    SaveDirList(Dir_List)
    fl_Dir_List_Saved = True
    return

def dir_load_wantedimg(parwnd): # Loading and encoding wanted people
    """[Finds all image-type files in a particulr dirctory, recognizes faces and adds face' encodings
    and path to image into appropriated dictionary KnownFaceDic]

    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """    
    wantedEncodings = []
    wantedNames = []
    WantedFaceDic = {"encodings": wantedEncodings, "names": wantedNames}
    mod = "hog"
    answ = tk.simpledialog.askinteger("Оберіть матем. модель пошуку облич", "1 - HOG (швидше), 2- CNN (точніше):",
                               minvalue=1, maxvalue=2, initialvalue=1)
    if answ != None: #setting tolerance for facecomp
        if answ == 1: mod = "hog"
        if answ == 2: mod = "cnn"
    else:
        mod = "hog"
    directory = sel_dir(parwnd, "Оберіть теку з фото невідомих осіб.", Dir_List, False, False)
    if directory in [".", "", None]: return
    wantedEncodings.clear()
    wantedNames.clear()
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    if not os.path.exists(wntdbdir):
        try:
            os.mkdir(wntdbdir)
        except OSError:
           # print("Не можу створити робочий каталог %s" % wntdbdir)
            tk.messagebox.showwarning("Увага!", "Не можу створити робочий каталог %s" % wntdbdir)
            return
    fn = os.path.join(wntdbdir, "wanted.pkl")
    if os.path.exists(fn):
        if tk.messagebox.askyesno("Увага!", "Файл даних розшукуваних осіб вже існує. Замінити?"):
            try:
                f = open(fn, "wb")
            except OSError:
                #print("Не можу створити файл бази даних %s" % fn)
                tk.messagebox.showwarning("Увага!", "Не можу створити файл бази даних %s" % fn)
                return
            cnt = 0
            fcnt = 0
            data = {}
            for entry in os.scandir(directory):
                parwnd.title(appcurver + " - вже додано %d облич(чя) з %d зображень..." % (cnt, fcnt))
                if (entry.name.split(".")[-1] in ["jpg", "jpeg", "png", "JPG", "JPEG", "PNG", "Jpg", "Jpeg", "Png"]) and entry.is_file():
                    fcnt += 1
                    image = face_recognition.load_image_file(entry.path)
                    boxes = face_recognition.face_locations(image, model=mod) # maybe cnn - more accu and use GPU/CUDA,
                    if len(boxes) > 0:
                                for enc in face_recognition.face_encodings(image, boxes):
                                    wantedEncodings.append(enc)
                                    wantedNames.append(entry.path)
                                    cnt += 1
                                    # print(cnt + 1, entry.path)
                                    # print(enc)
                    # else:
                    #     print(entry.path, 'Облич немає!')
            #print("Додано %d облич з %d зображень. Зберігаю кодування облич до файлу..." % (cnt, fcnt))
            tk.messagebox.showinfo('Інформація', "Додано %d облич з %d зображень. Зберігаю кодування облич до файлу..." % (cnt, fcnt))                   
            data = {"encodings": wantedEncodings, "names": wantedNames}
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
            parwnd.title(appcurver)
            return
        else:
            return
    else:
        try:
            f = open(fn, "wb")
        except OSError:
            #print("Не можу створити файл бази даних %s" % fn)
            tk.messagebox.showwarning("Увага!", "Не можу створити файл бази даних %s" % fn)
            return
        cnt = 0
        fcnt = 0
        data = {}
        for entry in os.scandir(directory):
            parwnd.title(appcurver + " - вже додано %d облич(чя) з %d зображень..." % (cnt, fcnt))
            if (entry.name.split(".")[-1] in ["jpg", "jpeg", "png", "JPG", "JPEG", "PNG", "Jpg", "Jpeg", "Png"]) and entry.is_file():
                fcnt += 1
                image = face_recognition.load_image_file(entry.path)
                boxes = face_recognition.face_locations(image, model=mod) # maybe cnn - more accu and use GPU/CUDA,
                # hog - MUCH faster but less accurate
                if len(boxes) > 0:
                            for enc in face_recognition.face_encodings(image, boxes):
                                wantedEncodings.append(enc)
                                wantedNames.append(entry.path)
                                cnt += 1
                #                 print(cnt + 1, entry.path)
                #                 print(enc)
                # else:
                #         print(entry.path, 'Облич немає!')
        #print("Додано %d облич з %d зображень. Зберігаю кодування облич до файлу..." % (cnt, fcnt))
        tk.messagebox.showinfo('Інформація', "Додано %d облич з %d зображень. Зберігаю кодування облич до файлу..." % (cnt, fcnt))
        data = {"encodings": wantedEncodings, "names": wantedNames}
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()
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
        #print("Не можу знайти/прочитати файл кодувань облич: {}".format(e.args[-1]))
        tk.messagebox.showwarning("Увага!", "Не можу знайти/прочитати файл кодувань облич: {}".format(e.args[-1]))
        return
    else:
        if os.path.getsize(dicfilename) > 15:
            picdic = {}
            picdic = pickle.load(f)
        else:
            f.close()
            return None
    f.close()
    #print("Face encodings loaded from", dicfilename)
    return picdic

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
    knownEncodings = []
    knownNames = []
    KnownFaceDic = {"encodings": knownEncodings, "names": knownNames}
    wantedEncodings = []
    wantedNames = []
    WantedFaceDic = {"encodings": wantedEncodings, "names": wantedNames}
    ###
    answ = tk.simpledialog.askfloat("Точність розпізнавання облич", "Менше значення - точніше (0<x<1, непогано 0.45):",
                               minvalue=0.000, maxvalue=1.000, initialvalue=0.45)
    if answ != None: #setting tolerance for facecomp
        tol = answ
    else:
        tol = 0.45    
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        #print ("Не можу знайти робочий каталог %s" % knwdbdir)
        tk.messagebox.showwarning("Увага!", "Не можу знайти робочий каталог %s" % knwdbdir)
        return
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    if not os.path.exists(wntdbdir):
        #print ("Не можу знайтии робочий каталог %s" % wntdbdir)
        tk.messagebox.showwarning("Увага!", "Не можу знайтии робочий каталог %s" % wntdbdir)
        return
    fnw = os.path.join(wntdbdir, "wanted.pkl")
    if not os.path.exists(fnw):
        #print ("Файл даних рошукуваних осіб %s відсутній або недоступний. Проскануйте папку!" % fnw)
        tk.messagebox.showwarning("Увага!", "Файл даних рошукуваних осіб  %s відсутній або недоступний. Проскануйте папку!" % fnw)
        return
    try:
        txtfn = "Report_" + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")).replace(":",".") + ".txt"
        txtrep = open(txtfn, "wt")
    except (IOError, EOFError) as e:
        #print("Не можу записати файл звіту: {}".format(e.args[-1]))
        tk.messagebox.showwarning("Увага!", "Не можу записати файл звіту {}".format(e.args[-1]))
        return
    xlxfn = "Report_" + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")).replace(":",".") + ".xlsx" #xlsx
    wsx = xlsxwriter.Workbook(xlxfn)
    # xlsx header
    wrksx = wsx.add_worksheet('Report ' + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")))
    wrksx.write(0, 0, "Звіт створено " + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")) + " з використанням %s" % appcurver)
    wrksx.write(1, 0, "Задана точність: " + str(tol))
    wrksx.write(3, 0, "Файл зображення розшукуваної особи")
    wrksx.write(3, 1, "Фото розшук. особи")
    wrksx.write(3, 2, 'Фото "еталонної" особи')
    wrksx.write(3, 3, "Файл еталонного зображення")
    wrksx.set_column(0,0, 60)
    wrksx.set_column(1,2, 27)
    wrksx.set_column(3,3, 60)
    ## txt header
    print("Звіт створено ", str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")), " з використанням %s" % appcurver, file=txtrep, end="\n", flush=False)
    print("Задана точність: ", str(tol), file=txtrep, end="\n", flush=False)
    print("Фото розшукуваної особи", "\t", "Еталонне зображення", file=txtrep, end="\n", flush=False)
    ###
    WantedFaceDic = facedic_load(fnw) ## Reading wantedfacedic
    wfdlen = len(WantedFaceDic["encodings"])
    xlcnt = 4
    ### перебираємо усі файли .pkl у папці _DB
    dfcnt = 0
    for entry in os.scandir(knwdbdir):
        parwnd.title(appcurver + " - проведено пошук %d облич у %d файлах еталонних даних" % (wfdlen, dfcnt))
        if (entry.name.lower().endswith(".pkl")) and entry.is_file():
            dfcnt +=1
            td = {}
            td = facedic_load(entry.path) ## Reading wantedfacedic
            if td != None:
                 KnownFaceDic = td
            else:
                continue
            wcnt = 0
            for wcnt in range(wfdlen): # у кожному файлі даних шукаємо усі розшукувані пики. Так швидше.
                wenc = WantedFaceDic["encodings"][wcnt]
                wname = WantedFaceDic["names"][wcnt]
                match = face_recognition.compare_faces(KnownFaceDic["encodings"], wenc, tolerance=tol)
                if True in match:
                    matchedIdxs = [i for (i, b) in enumerate(match) if b]
                    for i in matchedIdxs:
                        print(os.path.normpath(wname),
                              "\t",  os.path.normpath(KnownFaceDic["names"][i]),
                              file=txtrep, end="\n", flush=False)
                        c1 = "file:///" + wname.replace("\\", "/")
                        t1 = os.path.normpath(wname)
                        c2 = "file:///" + str(KnownFaceDic["names"][i]).replace("\\", "/")
                        t2 = os.path.normpath(KnownFaceDic["names"][i])
                            #xlsx
                        wrksx.write_url(xlcnt, 0, c1, string=t1)
                        wrksx.write_url(xlcnt, 3, c2, string=t2)
                        wrksx.set_row(xlcnt, 142)
                        try:
                                im = Image.open(t1)
                                nim = im.resize((192, 192))
                                t1t = t1 + "_192.jpg"
                                nim.save(t1t)
                                tmpwlist.append(t1t)
                                wrksx.insert_image(xlcnt, 1, t1t,
                                               {'object_position': 1})
                                #
                        except:
                                #print("Ескізу не буде")
                                wrksx.write(xlcnt, 1, "Ескізу не буде")
                        try:
                                im = Image.open(t2)
                                nim = im.resize((192, 192))
                                t2t = t2 + "_192.jpg"
                                nim.save(t2t)
                                tmpetlist.append(t2t)
                                wrksx.insert_image(xlcnt, 2, t2t,
                                               {'object_position': 1})
                                #
                        except:
                                #print("Ескізу не буде")
                                wrksx.write(xlcnt, 2, "Ескізу не буде")
                        xlcnt += 1
                # else:
                #          print("Немає відомих облич")
    wsx.close()
    txtrep.flush()
    txtrep.close()
    for fw in tmpwlist:
        try:
            os.remove(fw)
        except:
            continue
    tmpwlist.clear()
    for fe in tmpetlist:
        try:
            os.remove(fe)
        except:
            continue
    tmpetlist.clear()
    tk.messagebox.showinfo('Інформація', "Звіти збережено до файлів %s та %s" % (txtfn, xlxfn))
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
                                      width = 96,  
                                      height = 10,  
                                      font = ("Times New Roman", 
                                              12)) 
        for k in dl.keys():
                # s = '{:<0}'.format(k) + '{:>90}'.format(str(dl[k])) + "\n"
                s = str(k).ljust(65) + str(dl[k]).rjust(23) + "\n"
                text_area.insert(tk.INSERT, s)
        text_area.configure(state ='disabled') 
        text_area.focus()
        text_area.pack()
        win.mainloop()
    return

## GUI
wnd = tk.Tk(screenName=appcurver)
wnd.title(appcurver)
# NormTolerance = 0.45 # face distance by default
dl = {}
dl, fl_Dir_List_Loaded = LoadDirList()
if fl_Dir_List_Loaded: Dir_List = dl
frame1 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=10)
label1 = tk.Label(master=frame1,
                  text="Пошук облич у файлах зображень (невідомі серед відомих, краще - 1 фото = 1 обличчя, але не обов'язково!)",
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
                  text='''1. Оберіть теки (по одній) з еталонними фото для наповнення бази даних.
                  Скануйте тільки один раз, а нові еталонні фото кладіть 
                  у нові теки (із наступним їх скануванням)''',
                  font=("Times New Roman", 13),
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
but_lb.pack(side=tk.LEFT)
but_lbsub.pack(side=tk.RIGHT)
frame2.pack()
##
frame3 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=8)
label3 = tk.Label(master=frame3,
                  text='2. Оберіть теку з фото невідомих осіб.',
                  font=("Times New Roman", 13),
                  background='green',
                  foreground="white",
                  height=3
                  )
label3.pack()
but_lw = tk.Button(master=frame3,
                   text='Сканувати фото невідомих осіб.',
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
                  text='3. Натисніть кнопку для початку пошуку. Результати буде збережено в теці з файлом даної програми у форматах TXT та XLSX (з ескізами).',
                  font=("Times New Roman", 13),
                  background='green',
                  foreground="white",
                  height=3
                  )
label4.pack()
but_ab = tk.Button(master=frame4,
                   text='АНАЛІЗ ТА ЗВІТ',
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: pic_search(wnd))
but_dir = tk.Button(master=frame4,
                   text='Скановані папки...',
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: showdirlist(fl_Dir_List_Loaded))
but_ab.pack(side=tk.LEFT)
but_dir.pack(side=tk.RIGHT)
frame4.pack()
##
wnd.mainloop()
if not fl_Dir_list_Saved: SaveDirList(Dir_List)