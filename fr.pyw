# -*- coding: utf-8 -*-
"""Special thanks to:
-	face_recognition by Adam Geitgey (https://github.com/ageitgey/face_recognition) under MIT License;
-	dlib by Davis E. King (https://github.com/davisking/dlib ) under BSL-1.0 License;
-	Mediapipe by Google (https://github.com/google/mediapipe) under Apache-2.0 License.
"""
__author__ = "Bohdan SOKRUT"
__www__ = 'https://github.com/bohdansok/Face_Recognition'
__version__ = '1.98'

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
import myfr1
import myfrlang


#################################
inter_language = "eng"  # default Language selector
#################################
# Global vars - Start
appcurver = f"Face Recognition {__version__} by {__author__}."
# Global vars - End
##
# making local copies of global funcs
frcf = face_recognition.compare_faces
frfd = face_recognition.face_distance
## Main Application GUI class
class Mainapp(tk.Tk):
    """[Main Application GUI class]

    Args:
        tk ([type]): [Tkeinter Frame object]
    """    
    def __init__(self, inter_language, appcurver):
        """[Initiates application's GUI]

        Args:
            lang ([str]): [language id from myfrlang.py]
            appcurver ([str]): [global var appcurver = current app version and author information]
        """        
        self.lang = inter_language
        super().__init__(screenName=appcurver)
        self.title(appcurver)
        # creat interface language menu
        self.OPTION_TUPLE = tuple(myfrlang.lang.keys())
        self.lang_choice = tk.StringVar(self)
        self.lang_choice.set(myfrlang.lang[self.lang]["GUI"][13])
        option_menu = tk.OptionMenu(
            self,
            self.lang_choice,
            *self.OPTION_TUPLE,
            command=self.switch_GUI)
        option_menu.configure(width=9)
        option_menu.pack()
        frame1 = tk.Frame(master=self, relief=tk.RAISED, borderwidth=10)
        label1 = tk.Label(master=frame1,
                  text=myfrlang.lang[self.lang]["GUI"][0],
                  font=("Times New Roman", 16),
                  background='green',
                  foreground="white",
                  height=3
                  )
        label1.pack(side=tk.TOP)
        frame1.pack()
        ##
        frame2 = tk.Frame(master=self, relief=tk.RAISED, borderwidth=8)
        label2 = tk.Label(master=frame2,
                  text=myfrlang.lang[self.lang]["GUI"][1],
                  font=("Times New Roman", 15),
                  background='green',
                  foreground="white",
                  height=3
                  )
        label2.pack()
        but_lb = tk.Button(master=frame2,
                   text=myfrlang.lang[self.lang]["GUI"][2],
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: dir_load_allimg(self))
        but_lbsub = tk.Button(master=frame2,
                      text=myfrlang.lang[self.lang]["GUI"][3],
                      relief=tk.RAISED,
                      height=1,
                      font=("Times New Roman", 16),
                      bg='lightgreen',
                      command=lambda: dir_load_allimg_sub(self))
        but_video = tk.Button(master=frame2,
                    text=myfrlang.lang[self.lang]["GUI"][4],
                    relief=tk.RAISED,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='lightgreen',
                    command=lambda: myfr1.splitvid(self, self.lang))
        but_lb.pack(side=tk.LEFT)
        but_lbsub.pack(side=tk.RIGHT)
        but_video.pack(side=tk.BOTTOM)
        frame2.pack()
        ##
        frame3 = tk.Frame(master=self, relief=tk.RAISED, borderwidth=8)
        label3 = tk.Label(master=frame3,
                  text=myfrlang.lang[self.lang]["GUI"][5],
                  font=("Times New Roman", 15),
                  background='green',
                  foreground="white",
                  height=3
                  )
        label3.pack()
        but_lw = tk.Button(master=frame3,
                   text=myfrlang.lang[self.lang]["GUI"][6],
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: dir_load_wantedimg(self))
        but_curwdir = tk.Button(master=frame3,
                   text=myfrlang.lang[self.lang]["GUI"][7],
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='grey',
                   fg="black",
                   command=lambda: myfr1.showcurwdir(self.lang))
        but_lw.pack(side=tk.LEFT)
        but_curwdir.pack(side=tk.RIGHT)
        frame3.pack()
        ##
        frame4 = tk.Frame(master=self, relief=tk.RAISED, borderwidth=8)
        label4 = tk.Label(master=frame4,
                  text=myfrlang.lang[self.lang]["GUI"][8],
                  font=("Times New Roman", 13),
                  background='green',
                  foreground="white",
                  height=3
                  )
        label4.pack()
        but_ab = tk.Button(master=frame4,
                   text=myfrlang.lang[self.lang]["GUI"][9],
                   relief=tk.RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: pic_search(self))
        but_dir = tk.Button(master=frame4,
                    text=myfrlang.lang[self.lang]["GUI"][10],
                    relief=tk.SUNKEN,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='grey',
                    fg="black",
                    command=lambda: myfr1.showdirlist(self, self.lang))
        but_opt = tk.Button(master=frame4,
                    text=myfrlang.lang[self.lang]["GUI"][11],
                    relief=tk.SUNKEN,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='grey',
                    fg="black",
                    command=lambda: myfr1.optim(self.lang))
        but_help = tk.Button(master=frame4,
                    text=myfrlang.lang[self.lang]["GUI"][12],
                    relief=tk.SUNKEN,
                    height=1,
                    font=("Times New Roman", 16),
                    bg='grey',
                    fg="black",
                    command=lambda: myfr1.showhelp(self.lang))
        but_ab.pack(side=tk.LEFT)
        but_opt.pack(side=tk.RIGHT)
        but_dir.pack(side=tk.RIGHT)
        but_help.pack(side=tk.RIGHT)
        frame4.pack()
        ## mainloop
        #self.mainloop()
    
    def switch_GUI(self, *args):
        """[switch GUI language by destroyong the old app frame and re-init new one]
        """        
        self.destroy()
        self.lang = self.lang_choice.get()
        print(self.lang)
        self.__init__(self.lang, appcurver)

## Main Application GUI class - END   


def dir_load_allimg(parwnd):
    """[Finds all image-type files in a particulr image folder, recognizes faces and adds face' encodings
    and pathes to the images into at dictionary and then saves it at .pkl (Pickle-type) file]
    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """
    lang = app.lang
    confid = 0.5
    mod5_68 = "large"
    fl_dir_comment = True
    dir_comment = ""
    fl_dir_cmnt_file_created = False
    # Load Dir_list
    dl = {}
    Dir_List = {}
    dl, fl_Dir_List_Loaded = myfr1.LoadDirList(lang)
    if fl_Dir_List_Loaded:
        Dir_List = dl
    del(dl)
    # Getting various encoding params
    directory = ""
    try:
        confid, njits, fl_dir_comment, dir_comment = myfr1.get_params(
            fl_dir_comment, lang)
    except:
        return
    else:
        # select a target folder
        directory = myfr1.sel_dir(
             parwnd,
             myfrlang.lang[lang]["dir_load_allimg"][0],
             Dir_List, True, False, lang)
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
    knwdbdir = os.path.join(os.getcwd(), "_DB")
    if not os.path.exists(knwdbdir):
        try:
            os.mkdir(knwdbdir)
        except OSError:
            messagebox.showwarning(
                myfrlang.lang[lang]["dir_load_allimg"][1], myfrlang.lang[lang]["dir_load_allimg"][2] % knwdbdir)
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
    cnt, fcnt = myfr1.make_encodings(parwnd,
                   entries,
                   confid,
                   njits,
                   fn,
                   fcmnt,
                   fl_dir_comment,
                   fl_dir_cmnt_file_created,
                   dir_comment,
                   False,
                   False,
                   lang)
    del(entries)
    if fl_dir_cmnt_file_created:
                fcmnt.close()
    myfr1.SaveDirList(Dir_List, lang)
    del(Dir_List)
    messagebox.showinfo(myfrlang.lang[lang]["dir_load_allimg"][3],
                           myfrlang.lang[lang]["dir_load_allimg"][4] % (cnt, fcnt, directory))
    parwnd.title(appcurver)
    return


def dir_load_allimg_sub(parwnd):
    """[Finds all image-type files in a particulr image folder and it's subfolders, recognizes faces and adds face' encodings
    and pathes to the images into at dictionary and then saves it at .pkl (Pickle-type) file]
    Args:
        rootwnd ([Tkinter widget]): [parent Tkinter widget]
    """
    lang = app.lang
    allimgf = []
    confid = 0.5
    mod5_68 = "large"
    fl_dir_comment = False
    dir_comment = ""
    # Load Dir)list
    Dir_List = {}
    dl = {}
    dl, fl_Dir_List_Loaded = myfr1.LoadDirList()
    if fl_Dir_List_Loaded:
        Dir_List = dl
    del(dl)
    # Getting various encoding params
    directory = ""
    try:
        confid, njits, fl_dir_comment, dir_comment = myfr1.get_params(
            fl_dir_comment, lang)
    except:
        return
    else:
    # select a target folder
        directory = myfr1.sel_dir(
             parwnd, myfrlang.lang[lang]["dir_load_allimg_sub"][0], Dir_List, True, True, lang)
        if directory in [".", "", None]:
            del(allimgf)  # clearing trash
            return
    # creating workin folders
    knwdbdir = os.path.join(os.getcwd(), "_DB")
    if not os.path.exists(knwdbdir):
        try:
            os.mkdir(knwdbdir)
        except OSError:
            messagebox.showwarning(
                myfrlang.lang[lang]["dir_load_allimg_sub"][1],
                myfrlang.lang[lang]["dir_load_allimg_sub"][2] % knwdbdir)
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
    cnt, fcnt = myfr1.make_encodings(parwnd,
                   allimgf,
                   confid,
                   njits,
                   fn,
                   None,
                   False,
                   False,
                   dir_comment,
                   True,
                   False,
                   lang)
    del(allimgf)
    myfr1.SaveDirList(Dir_List)
    del(Dir_List)
    messagebox.showinfo(myfrlang.lang[lang]["dir_load_allimg_sub"][3],
                           myfrlang.lang[lang]["dir_load_allimg_sub"][4] % (
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
    lang = app.lang
    confid = 0.5
    fl_dir_comment = True
    dir_comment = ""
    fl_dir_cmnt_file_created = False
    # Load Dir_list
    Dir_List = {}
    dl = {}
    dl, fl_Dir_List_Loaded = myfr1.LoadDirList()
    if fl_Dir_List_Loaded:
        Dir_List = dl
    del(dl)
    ### vars - end
    # Getting various encoding params
    directory = ""
    try:
        confid, njits, fl_dir_comment, dir_comment = myfr1.get_params(
            fl_dir_comment, lang)
    except:
        return
    else:
        # select a target folder
        directory = myfr1.sel_dir(
            parwnd, myfrlang.lang[lang]["dir_load_wantedimg"][0], Dir_List, False, False, lang)
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
    wntdbdir = os.path.join(os.getcwd(), "_Wanted")
    if not os.path.exists(wntdbdir):
        try:
            os.mkdir(wntdbdir)
        except OSError:
            messagebox.showwarning(
                myfrlang.lang[lang]["dir_load_wantedimg"][1],
                myfrlang.lang[lang]["dir_load_wantedimg"][2] % wntdbdir)
            if fl_dir_cmnt_file_created:
                fcmnt.close()
            return
    fn = os.path.join(wntdbdir, "wanted.pkl")
    cnt = 0
    fcnt = 0
    entries = os.scandir(directory)
    # calling face encodings maker
    cnt, fcnt = myfr1.make_encodings(parwnd,
                                    entries,
                                    confid,
                                    njits,
                                    fn,
                                    fcmnt,
                                    fl_dir_comment,
                                    fl_dir_cmnt_file_created,
                                    dir_comment,
                                    False,
                                    True,
                                    lang)
     # writing the search set path to _dir.ini (JSON-type) file
    wssfn = os.path.join(wntdbdir, "_dir.ini")
    try:
        f = open(wssfn, "w")
        json.dump(directory, f)
        f.close()
    except OSError:
        messagebox.showwarning(
            myfrlang.lang[lang]["dir_load_wantedimg"][3],
            myfrlang.lang[lang]["dir_load_wantedimg"][4] % wssfn)
    if fl_dir_cmnt_file_created:
        fcmnt.close()
    messagebox.showinfo(myfrlang.lang[lang]["dir_load_wantedimg"][5],
                            myfrlang.lang[lang]["dir_load_wantedimg"][6] % (cnt, fcnt, directory))
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
    lang = app.lang
    tmpwlist = []
    tmpetlist = []
    fl_rep_dir_default = False
    fl_MultyTh = False
    fl_dir_cmnt_file_loaded = False
    fl_New_knowndir = True
    ###
    answ = simpledialog.askfloat(myfrlang.lang[lang]["pic_search"][0],
                                    myfrlang.lang[lang]["pic_search"][1],
                                    minvalue=0.0, maxvalue=1.0, initialvalue=0.45)
    if answ not in [None, ""]:  # setting tolerance for facecomp
        tol = answ
    else:
        return
    knwdbdir = os.path.join(os.getcwd(), "_DB")  # setting path to _DB
    if not os.path.exists(knwdbdir):
        messagebox.showwarning(
            myfrlang.lang[lang]["pic_search"][2],
            myfrlang.lang[lang]["pic_search"][3] % knwdbdir)
        return
    # setting path to _Wanted
    wntdbdir = os.path.join(os.getcwd(), "_Wanted")
    if not os.path.exists(wntdbdir):
        messagebox.showwarning(
            myfrlang.lang[lang]["pic_search"][4],
            myfrlang.lang[lang]["pic_search"][5] % wntdbdir)
        return
    fnw = os.path.join(wntdbdir, "wanted.pkl")  # trying to load wanted list
    if not os.path.exists(fnw):
        messagebox.showwarning(
            myfrlang.lang[lang]["pic_search"][6],
            myfrlang.lang[lang]["pic_search"][7] % fnw)
        return
    wfd = myfr1.Face_Dictionary(fnw, "load", lang)  # Reading wantedfacedic
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
            messagebox.showwarning(
                myfrlang.lang[lang]["pic_search"][8],
                myfrlang.lang[lang]["pic_search"][9].format(e.args[-1]))
    else:
        fl_rep_dir_default = True
   # init multythread session
    try:
        executor = concurrent.futures.ThreadPoolExecutor()
        fl_MultyTh = True
    except:
        fl_MultyTh = False
    # for all .pkl files in _DB
    dfcnt = 0
    allfound = [] # temp list for search results
    entries = os.scandir(knwdbdir)
    for entry in entries:
        parwnd.title(
            appcurver + myfrlang.lang[lang]["pic_search"][10] % (wfdlen, dfcnt))
        if (entry.name.lower().endswith(".pkl")) and entry.is_file():
            dfcnt += 1
            kfd = myfr1.Face_Dictionary(entry.path, "load", lang)
            wcnt = 0
           # finding wanted encodings at every loaded data file
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
                            to add some external DB functionality
                            (some SQL requests, whatever)
                            - to obtain data to be putted in the report
                            by variable <st>'''
                        extst = ""
                        if fl_dir_cmnt_file_loaded:
                            extst = str(dir_coms.get(t2.rpartition("\\")[2]))
                        st = " ".join([st, myfrlang.lang[lang]["pic_search"][35], extst.replace("\n", "")])
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
                messagebox.showwarning(
                    myfrlang.lang[lang]["pic_search"][11],
                    myfrlang.lang[lang]["pic_search"][12].format(e.args[-1]))
                return
            try:
                xlxfn = "Report_" + str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")
                                    ).replace(":", ".") + ".xlsx"  # xlsx
                wsx = xlsxwriter.Workbook(xlxfn)
            except (IOError, EOFError) as e:
                messagebox.showwarning(
                    myfrlang.lang[lang]["pic_search"][13],
                    myfrlang.lang[lang]["pic_search"][14].format(e.args[-1]))
                return
        else:
            try:
                txtfn = os.path.join(rep_dir, "Report_" + str(
                    datetime.now().strftime("%Y-%m-%d %H.%M.%S")).replace(":", ".") + ".txt")
                txtrep = open(txtfn, "wt")
            except (IOError, EOFError) as e:
                messagebox.showwarning(
                    myfrlang.lang[lang]["pic_search"][15],
                    myfrlang.lang[lang]["pic_search"][16].format(e.args[-1]))
                return
            try:
                xlxfn = os.path.join(rep_dir, "Report_" + str(datetime.now().strftime(
                    "%Y-%m-%d %H.%M.%S")).replace(":", ".") + ".xlsx")  # xlsx
                wsx = xlsxwriter.Workbook(xlxfn)
            except (IOError, EOFError) as e:
                messagebox.showwarning(
                    myfrlang.lang[lang]["pic_search"][17],
                    myfrlang.lang[lang]["pic_search"][18].format(e.args[-1]))
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
        wrksx.write(0, 0, myfrlang.lang[lang]["pic_search"][23] + str(datetime.now().strftime(
            "%Y-%m-%d %H.%M.%S")) + myfrlang.lang[lang]["pic_search"][24] % appcurver, cell_bold)
        wrksx.write(1, 0, myfrlang.lang[lang]["pic_search"][25] + str(tol), cell_bold)
        wrksx.write(3, 0, myfrlang.lang[lang]["pic_search"][26], cell_bold)
        wrksx.write(3, 1, myfrlang.lang[lang]["pic_search"][27], cell_bold)
        wrksx.write(3, 2, myfrlang.lang[lang]["pic_search"][28], cell_bold)
        wrksx.write(3, 3, myfrlang.lang[lang]["pic_search"][29], cell_bold)
        wrksx.write(3, 4, myfrlang.lang[lang]["pic_search"][30], cell_bold)
        wrksx.write(3, 5, myfrlang.lang[lang]["pic_search"][31], cell_bold)
        wrksx.write(3, 6, myfrlang.lang[lang]["pic_search"][32], cell_bold)
        wrksx.write(3, 7, myfrlang.lang[lang]["pic_search"][33], cell_bold)
        # txt header
        print(myfrlang.lang[lang]["pic_search"][23], str(datetime.now().strftime("%Y-%m-%d %H.%M.%S")),
              myfrlang.lang[lang]["pic_search"][24] % appcurver, file=txtrep, end="\n", flush=False)
        print(myfrlang.lang[lang]["pic_search"][25], str(tol), file=txtrep, end="\n", flush=False)
        print(myfrlang.lang[lang]["pic_search"][26], "\t", myfrlang.lang[lang]["pic_search"][31], "\t",
              myfrlang.lang[lang]["pic_search"][32], "\t", myfrlang.lang[lang]["pic_search"][33], file=txtrep, end="\n", flush=False)
        ###
        xlcnt = 4  # starting row at XLSX-sheet
        for r in allfound:
            wrksx.set_row(xlcnt, 175) # row height
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
                                   "_241.jpg"])  # Thumbnail is not available for gif-pictures
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
                wrksx.write(xlcnt, 1, myfrlang.lang[lang]["pic_search"][34])
                wrksx.write(xlcnt, 2, myfrlang.lang[lang]["pic_search"][34])
            try:
                im = Image.open(r[3])
                if fl_New_knowndir:
                    t2t = "".join([r[3], str(r[5]), str(datetime.now()).replace(":", ""),
                                   "_242.jpg"])  # no thumb for gif
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
                                   "_242.jpg"])  # Thumbnail is not available for gifpictures
                    im.thumbnail((240, 240))
                    im.save(t2t)
                    tmpetlist.append(t2t)
                    wrksx.insert_image(xlcnt, 4, t2t, {'object_position': 1})
            except Exception as e:
                print(e)
                wrksx.write(xlcnt, 3, myfrlang.lang[lang]["pic_search"][34])
                wrksx.write(xlcnt, 4, myfrlang.lang[lang]["pic_search"][34])
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
        messagebox.showinfo(
            myfrlang.lang[lang]["pic_search"][19],
            myfrlang.lang[lang]["pic_search"][20] % (
        wfdlen, dfcnt, txtfn, xlxfn))
    else:
        messagebox.showinfo(
            myfrlang.lang[lang]["pic_search"][21],
            myfrlang.lang[lang]["pic_search"][22]  % (wfdlen, dfcnt))
    del(allfound)
    parwnd.title(appcurver)
    return


# GUI
app = Mainapp(inter_language, appcurver)
app.mainloop()
