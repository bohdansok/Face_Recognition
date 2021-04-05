# -*- coding: utf-8 -*-
__author__ = """Bohdan SOKRUT"""
__www__ = 'https://github.com/bohdansok/Face_Recognition'
__version__ = '1.00'
""" Initial building of reference face encodings takes a time even on GPUs...
The script allows to save your time in case if you've decided to move that millions of
your pictures to another location. Just edit dictionary <change_dic>  below. 
"""

import os.path
import pickle
from tkinter import filedialog, messagebox

# Here is dictionary with path replacing data: what for what
change_dic = {"What_to_change_in_old_path": "New_part_of_path_to_the_pictures_",
              "C:/Pics_Folders/": "D:/FRPics/Pics_Folders/", }
######


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
        messagebox.showwarning(
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


###
directory = filedialog.askdirectory(
    title="Choose DB pkl directory", mustexist=True)
if directory in [".", "", None]:
    sys.exit
# os.chdir(directory)
v3fcnt = 0
fcnt = 0
new_n = ""
entries = os.scandir(directory)
for entry in entries:
    if entry.name.lower().startswith("v3-") and entry.name.lower().endswith(".pkl") and entry.is_file():
        bigdic = {}
        Encodings = []
        Names = []
        New_names = []
        facelocs = []
        td = {}
        td = facedic_load(entry.path)  # Reading facedic
        Encodings.extend(td["encodings"])
        Names.extend(td["names"])
        facelocs.extend(td["locations"])
        del(td)
        v3fcnt += 1
        fl_Madenew = False
        for old_n in Names:
            for k in change_dic.keys():
                if old_n.find(k) != -1:
                    new_n = old_n.replace(k, change_dic.get(k))
                    fl_Madenew = True
            New_names.append(new_n)
        if fl_Madenew:
            fnew = os.path.join(directory, "v3-changed_" + entry.name)
            try:
                f = open(fnew, "wb")
            except OSError:
                del(Encodings)
                del(Names)
                del(New_names)
                del(facelocs)
                sys.exit("Не можу створити файл бази даних %s." % fnew)
            bigdic = {"encodings": Encodings,
                      "names": New_names, "locations": facelocs}
            pickle.dump(bigdic, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
            del(bigdic)
            del(Encodings)
            del(facelocs)
            del(Names)
            del(New_names)
       # optimization of old-school data files
    if (not entry.name.lower().startswith("v3-")) and entry.name.lower().endswith(".pkl") and entry.is_file():
        bigdic = {}
        Encodings = []
        Names = []
        New_names = []
        td = {}
        td = facedic_load(entry.path)  # Reading facedic
        Encodings.extend(td["encodings"])
        Names.extend(td["names"])
        del(td)
        fcnt += 1
        fl_Madenew = False
        for old_n in Names:
            for k in change_dic.keys():
                new_n = old_n.replace(k, change_dic.get(k))
                fl_Madenew = True
            New_names.append(new_n)
        if fl_Madenew:
            fnew = os.path.join(directory, "changed_" + entry.name)
            try:
                f = open(fnew, "wb")
            except OSError:
                del(Encodings)
                del(Names)
                del(New_names)
                del(facelocs)
                sys.exit("Не можу створити файл бази даних %s." % fnew)
            bigdic = {"encodings": Encodings, "names": New_names}
            pickle.dump(bigdic, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
            del(bigdic)
            del(Encodings)
            del(Names)
            del(New_names)
print("Totally %d face encodings data files changed" % (v3fcnt + fcnt))
