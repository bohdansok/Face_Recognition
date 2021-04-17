# -*- coding: utf-8 -*-
__author__ = """Bohdan SOKRUT"""
__www__ = 'https://github.com/bohdansok/Face_Recognition'
__version__ = '1.96'

##
import concurrent.futures
import glob
import json
import os
import tkinter as tk
from datetime import datetime
from tkinter import messagebox, simpledialog
import face_recognition
import xlsxwriter
from PIL import Image, ImageDraw
import myfr

# Global vars - Start
appcurver = "Face Recognition 1.96 (Video&Masks) by Bohdan SOKRUT (powered by dlib)"
Posv_Dir = {}
fl_Posv_Dir_Loaded = False
# Global vars - End
##


def dir_load_allimg(parwnd):
    """[Finds all image-type files in a particulr image folder, recognizes faces and adds face' encodings
    and pathes to the images into at dictionary and then saves it at .pkl (Pickle-type) file]
    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """
    mod = "hog"
    mod5_68 = "large"
    fl_dir_comment = True
    dir_comment = ""
    fl_dir_cmnt_file_created = False
    # Load Dir_list
    dl = {}
    Dir_List = {}
    dl, fl_Dir_List_Loaded = myfr.LoadDirList()
    if fl_Dir_List_Loaded:
        Dir_List = dl
    del(dl)
    # Getting various encoding params
    directory = ""
    try:
        mod, nous, njits, mod5_68, fl_dir_comment, dir_comment = myfr.get_params(
            fl_dir_comment)
    except:
        return
    else:
        # select a target folder
        directory = myfr.sel_dir(
             parwnd, "Оберіть теку з еталонними фото", Dir_List, True, False)
        if directory in [".", "", None]:
            return
    fcmnt = None
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
            if fl_dir_cmnt_file_created:
                fcmnt.close()
            return
    fn = os.path.join(knwdbdir,
                      "v3-F6-" + mod5_68 + "_" + os.path.basename(
                          directory) + "_" + str(datetime.now()).replace(":", ".") + ".pkl")
    cnt = 0
    fcnt = 0
    # collect pictures
    entries = os.scandir(directory)
    # calling face encodings maker
    cnt, fcnt = myfr.make_encodings(parwnd,
                                    entries,
                                    mod,
                                    nous,
                                    njits,
                                    mod5_68,
                                    fn,
                                    fcmnt,
                                    fl_dir_comment,
                                    fl_dir_cmnt_file_created,
                                    dir_comment,
                                    False,
                                    False)
    del(entries)
    if fl_dir_cmnt_file_created:
                fcmnt.close()
    myfr.SaveDirList(Dir_List)
    del(Dir_List)
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
    allimgf = []
    mod = "hog"
    mod5_68 = "large"
    fl_dir_comment = False
    dir_comment = ""
    # Load Dir)list
    Dir_List = {}
    dl = {}
    dl, fl_Dir_List_Loaded = myfr.LoadDirList()
    if fl_Dir_List_Loaded:
        Dir_List = dl
    del(dl)
    # Getting various encoding params
    directory = ""
    try:
        mod, nous, njits, mod5_68, fl_dir_comment, dir_comment = myfr.get_params(
            fl_dir_comment)
    except:
        return
    else:
    # select a target folder
        directory = myfr.sel_dir(
             parwnd, "Оберіть папку з еталонними фото (із вклад. теками)", Dir_List, True, True)
        if directory in [".", "", None]:
            del(allimgf)  # clearing trash
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
            return
    fn = os.path.join(knwdbdir, "v3-F6-" + mod5_68 + "_" + os.path.basename(directory) + "_" + str(datetime.now()).replace(":", ".") + ".pkl")
    cnt = 0
    fcnt = 0
    # creating list of all images in the dir and subdirs
    allimgf.extend(glob.glob(directory + "/**/*.jpg", recursive=True))
    allimgf.extend(glob.glob(directory + "/**/*.jpeg", recursive=True))
    allimgf.extend(glob.glob(directory + "/**/*.png", recursive=True))
    allimgf.extend(glob.glob(directory + "/**/*.bmp", recursive=True))
    allimgf.extend(glob.glob(directory + "/**/*.gif", recursive=True))
    # calling face encodings maker
    cnt, fcnt = myfr.make_encodings(parwnd,
                                    allimgf,
                                    mod,
                                    nous,
                                    njits,
                                    mod5_68,
                                    fn,
                                    None,
                                    False,
                                    False,
                                    dir_comment,
                                    True,
                                    False)
    del(allimgf)
    myfr.SaveDirList(Dir_List)
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
    mod = "hog"  # default for FR mathem. model
    mod5_68 = "large"
    fl_dir_comment = True
    dir_comment = ""
    fl_dir_cmnt_file_created = False
    # Load Dir_list
    Dir_List = {}
    dl = {}
    dl, fl_Dir_List_Loaded = myfr.LoadDirList()
    if fl_Dir_List_Loaded:
        Dir_List = dl
    del(dl)
    ### vars - end
    # Getting various encoding params
    directory = ""
    try:
        mod, nous, njits, mod5_68, fl_dir_comment, dir_comment = myfr.get_params(
            fl_dir_comment)
    except:
        return
    else:
        # select a target folder
        directory = myfr.sel_dir(
            parwnd, "Оберіть теку з еталонними фото", Dir_List, False, False)
        if directory in [".", "", None]:
            return
    fcmnt = None
    if fl_dir_comment:
        cmntfn = os.path.join(directory, "_facrecmnt.ini")
        try:
            fcmnt = open(cmntfn, "wt")
        except:
            fl_dir_cmnt_file_created = False
        else:
            fl_dir_cmnt_file_created = True
    # check if _wanted folder available
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    if not os.path.exists(wntdbdir):
        try:
            os.mkdir(wntdbdir)
        except OSError:
            tk.messagebox.showwarning(
                "Увага!", "Не можу створити робочу теку %s" % wntdbdir)
            if fl_dir_cmnt_file_created:
                fcmnt.close()
            return
    fn = os.path.join(wntdbdir, "wanted.pkl")
    cnt = 0
    fcnt = 0
    entries = os.scandir(directory)
    # calling face encodings maker
    cnt, fcnt = myfr.make_encodings(parwnd,
                                    entries,
                                    mod,
                                    nous,
                                    njits,
                                    mod5_68,
                                    fn,
                                    fcmnt,
                                    fl_dir_comment,
                                    fl_dir_cmnt_file_created,
                                    dir_comment,
                                    False,
                                    True)
     # writing the search set path to _dir.ini (JSON-type) file
    wssfn = os.path.join(wntdbdir, "_dir.ini")
    try:
        f = open(wssfn, "w")
        json.dump(directory, f)
        f.close()
    except OSError:
        tk.messagebox.showwarning(
            "Увага!", "Не можу записати параметри пошуку у файл %s. Звіти зберігатимуться у робочу теку програми" % wssfn)
    if fl_dir_cmnt_file_created:
        fcmnt.close()
    tk.messagebox.showinfo('Інформація',
                            "Додано %d обличь з %d зображень з теки %s. Зберігаю кодування обличь до файлу..." % (cnt, fcnt, directory))
    parwnd.title(appcurver)
    return

# Main searcher
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
    answ = tk.simpledialog.askfloat("Точність розпізнавання обличь", "Менше значення - точніше (0<x<1, непогано 0.45):",
                                    minvalue=0.0, maxvalue=1.0, initialvalue=0.45)
    if answ not in [None, ""]:  # setting tolerance for facecomp
        tol = answ
    else:
        return
    knwdbdir = os.path.join(os.path.join(
        os.getcwd(), "_DB"))  # setting path to _DB
    if not os.path.exists(knwdbdir):
        tk.messagebox.showwarning(
            "Увага!", "Не можу знайти робочу теку %s" % knwdbdir)
        return
    # setting path to _Wanted
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    if not os.path.exists(wntdbdir):
        tk.messagebox.showwarning(
            "Увага!", "Не можу знайтии робочу теку %s" % wntdbdir)
        return
    fnw = os.path.join(wntdbdir, "wanted.pkl")  # trying to load wanted list
    if not os.path.exists(fnw):
        tk.messagebox.showwarning(
            "Увага!", "Файл даних рошукуваних осіб %s відсутній або недоступний. Проскануйте папку!" % fnw)
        return
    wfd = myfr.Face_Dictionary(fnw, "load")  # Reading wantedfacedic
    wfdlen = len(wfd.fd["encodings"])
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
    frcf = face_recognition.compare_faces
    frfd = face_recognition.face_distance
    # перебираємо усі файли .pkl у папці _DB
    dfcnt = 0
    allfound = []
    entries = os.scandir(knwdbdir)
    for entry in entries:
        parwnd.title(
            appcurver + " - проведено пошук %d обличь у %d файлах еталонних даних" % (wfdlen, dfcnt))
        if (entry.name.lower().endswith(".pkl")) and entry.is_file():
            dfcnt += 1
            kfd = myfr.Face_Dictionary(entry.path, "load")
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
                            ''' Here is the right place
                            to add some external DB funcionalyty
                            (some SQL requests, whatever)
                            - to obtain data to be putted in the report
                            by variable <st>'''
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
        #destroying objects
        wfd.destroy()
        kfd.destroy()
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
              "Додатові дані", "\t", "Схожість, %", file=txtrep, end="\n", flush=False)
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
    del(frcf)
    del(frfd)
    del(allfound)
    parwnd.title(appcurver)
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
                    command=lambda: myfr.splitvid(wnd))
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
                   command=myfr.showcurwdir)
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
                   command=lambda: pic_search(wnd))
but_dir = tk.Button(master=frame4,
                    text='Скановані теки...',
                    relief=tk.SUNKEN,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='grey',
                    fg="black",
                    command=lambda: myfr.showdirlist(wnd))
but_opt = tk.Button(master=frame4,
                    text='Оптимізація бази даних',
                    relief=tk.SUNKEN,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='grey',
                    fg="black",
                    command=myfr.optim)
but_help = tk.Button(master=frame4,
                    text='Довідка...',
                    relief=tk.SUNKEN,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='grey',
                    fg="black",
                    command=myfr.showhelp)
but_ab.pack(side=tk.LEFT)
but_opt.pack(side=tk.RIGHT)
but_dir.pack(side=tk.RIGHT)
but_help.pack(side=tk.RIGHT)
frame4.pack()
##
wnd.mainloop()
if fl_Posv_Dir_Loaded:
    del(Posv_Dir)
