
# first attemt to create a rec and comp app
# $ face_recognition --cpus -1
# from sys import version_info
# if version_info.major == 2:
#     import Tkinter as tk
# elif version_info.major == 3:
#     import tkinter as tk
    
import face_recognition, os, pickle, os.path
import tkinter as tk
from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from datetime import datetime

## Global vars - Start
PicFileTypes = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG']
knownEncodings = []
knownNames = []
KnownFaceDic = {"encodings": knownEncodings, "names": knownNames}
BaseDirectory = ''
WantedDirectory = ''
Dir_List = []
fl_Dir_list_Saved = False
## Global vars - End
##
def LoadDirList():
    # dlnm = os.path.join(os.path.join(os.getcwd(), "_dirlist.ini"))
    dlnm = "_dirlist.ini"
    try:
            f = open(dlnm, "rb")
            Dir_list = pickle.load(f)
            print(str(Dir_List)) # temp
            f.close()
    except (IOError, EOFError) as e:
            print("Не можу знайти/прочитати файл даних сканованих папок: {}".format(e.args[-1]))
            return
    return

def SaveDirList():
    # dlnm = os.path.join(os.path.join(os.getcwd(), "_dirlist.ini"))
    dlnm = "_dirlist.ini"
    try:
        f = open(dlnm, "wb")
        pickle.dump(Dir_List, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()
    except OSError:
        print ("Не можу записати список сканованих папок %s" % dlnm)
            # parwnd.destroy()
            # sys.exit('Роботу програми припинено через помилку зстворення/запису на диск')
        return
    return

def sel_dir(rootwnd, Title): # selecting a directory with pictures
    sel_dir_path = tk.filedialog.askdirectory(parent=rootwnd, title=Title, mustexist=True)
    # sel_dir_path = os.path.normpath(sel_dir_path)
    if sel_dir_path == '.' or sel_dir_path == '': return
    if sel_dir_path in Dir_List:
        if tk.messagebox.askyesno("Увага!", "Папка вже сканувлась Повторити?"):
            return sel_dir_path
        else:
            sel_dir_path = sel_dir(rootwnd, Title)
            # sel_dir_path = os.path.normpath(sel_dir_path)
            Dir_List.append(sel_dir_path)
            print(str(Dir_List)) # temp 
    else:
        Dir_List.append(sel_dir_path)
        print(str(Dir_List)) # temp 
    return sel_dir_path

def dir_load_allimg(parwnd, title):
    directory = sel_dir(parwnd, title)
    print(directory)
    if directory == "." or directory == "" or directory == None: return
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        try:
            os.mkdir(knwdbdir)
        except OSError:
            print ("Не можу створити робочий каталог %s" % knwdbdir)
            # parwnd.destroy()
            # sys.exit('Роботу програми припинено через помилку зстворення/запису на диск')
            return
    fn = os.path.join(knwdbdir, (str(datetime.now()).replace(":", ".") + ".pkl"))
    try:
        f = open(fn, "wb")
    except OSError:
            print ("Не можу створити файл бази даних %s" % fn)
            # parwnd.destroy()
            # sys.exit('Роботу програми припинено через помилку зстворення/запису на диск')
            return
    cnt = 1
    data = {}
    for entry in os.scandir(directory):
        if (entry.path.lower().endswith(".jpg") 
            or entry.path.lower().endswith(".png")) and entry.is_file():
            image = face_recognition.load_image_file(entry.path)
            boxes = face_recognition.face_locations(image, model='hog') # maybe cnn - more accu and use GPU/CUDA,
            # hog - MUCH faster but less accurate
            if len(boxes) == 1:
                enc = face_recognition.face_encodings(image, boxes)[0]
                knownEncodings.append(enc)
                knownNames.append(entry.path)
                print(cnt, entry.path)
                print(enc)
                cnt += 1
            else: print(entry.path, 'No or more then one face')
    print("[INFO] Saving encodings to file...")
    data = {"encodings": knownEncodings, "names": knownNames}
    # data[knownEncodings] = knownNames
    # for en, nm in knownNames, knownNames: data = dict.fromkeys(en, nm)
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    SaveDirList()
    fl_Dir_List_Saved = True
    return

def dir_load_wantedimg(parwnd, title): # Loading and encoding wanted people
    directory = sel_dir(parwnd, title)
    WantedDirectory = directory
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    if not os.path.exists(wntdbdir):
        try:
            os.mkdir(wntdbdir)
        except OSError:
            print("Не можу створити робочий каталог %s" % wntdbdir)
            # parwnd.destroy()
            # sys.exit('Роботу програми припинено через помилку зстворення/запису на диск')
            return
    fn = os.path.join(wntdbdir, "wanted.pkl")
    if os.path.exists(fn):
        if tk.messagebox.askyesno("Увага!", "Файл даних розшукуваних осіб вже існує. Замінити?"):
            try:
                f = open(fn, "wb")
            except OSError:
                print("Не можу створити файл бази даних %s" % fn)
                #parwnd.destroy()
                #sys.exit('Роботу програми припинено через помилку зстворення/запису на диск')
                return
            cnt = 1
            data = {}
            for entry in os.scandir(directory):
                if (entry.path.lower().endswith(".jpg")
                    or entry.path.lower().endswith(".png")) and entry.is_file():
                    image = face_recognition.load_image_file(entry.path)
                    boxes = face_recognition.face_locations(image, model='hog') # maybe cnn - more accu and use GPU/CUDA,
                    # hog - MUCH faster but less accurate
                    if len(boxes) == 1:
                        enc = face_recognition.face_encodings(image, boxes)[0]
                        knownEncodings.append(enc)
                        knownNames.append(entry.path)
                        print(cnt, entry.path)
                        print(enc)
                        cnt += 1
                    else:
                        print(entry.path, 'Облич немає або багато!')
            print("[INFO] Saving encodings to file...")
            data = {"encodings": knownEncodings, "names": knownNames}
            # data[knownEncodings] = knownNames
            # for en, nm in knownNames, knownNames: data = dict.fromkeys(en, nm)
            pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
            f.close()
            return
        else:
            return
    else:
        cnt = 1
        data = {}
        for entry in os.scandir(directory):
            if (entry.path.lower().endswith(".jpg")
                or entry.path.lower().endswith(".png")) and entry.is_file():
                image = face_recognition.load_image_file(entry.path)
                boxes = face_recognition.face_locations(image, model='hog') # maybe cnn - more accu and use GPU/CUDA,
                # hog - MUCH faster but less accurate
                if len(boxes) == 1:
                    enc = face_recognition.face_encodings(image, boxes)[0]
                    knownEncodings.append(enc)
                    knownNames.append(entry.path)
                    print(cnt, entry.path)
                    print(enc)
                    cnt += 1
                else: print(entry.path, 'No or more then one face')
        print("[INFO] Saving encodings to file...")
        data = {"encodings": knownEncodings, "names": knownNames}
        # data[knownEncodings] = knownNames
        # for en, nm in knownNames, knownNames: data = dict.fromkeys(en, nm)
        pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
        f.close()
    return    
    
def facedic_load(dicfilename):
    try:
        f = open(dicfilename, "rb")
    except (IOError, EOFError) as e:
        print("Не можу знайти/прочитати файл даних розшукуваних осіб: {}".format(e.args[-1]))
        return
    else:
        picdic = {}
        picdic = pickle.load(f)
    f.close()
    print("Face encodings loaded from", dicfilename)
    return picdic

def pic_search(): ## test edition with a single pre-designated encoding
    knwdbdir = os.path.join(os.path.join(os.getcwd(), "_DB"))
    if not os.path.exists(knwdbdir):
        print ("Не можу знайти робочий каталог %s" % knwdbdir)
        return
    wntdbdir = os.path.join(os.path.join(os.getcwd(), "_Wanted"))
    if not os.path.exists(wntdbdir):
        print ("Не можу знайтии робочий каталог %s" % wntdbdir)
        return
    for entry in os.scandir(knwdbdir):
        if (entry.path.lower().endswith(".pkl")) and entry.is_file():
            KnownFaceDic = facedic_load(entry.path)
            obama = face_recognition.load_image_file("obama.jpg")
            obenc = face_recognition.face_encodings(obama)[0]
            match = face_recognition.compare_faces(KnownFaceDic["encodings"], obenc, tolerance=0.6)
            print(str(match))
            if True in match:
                matchedIdxs = [i for (i, b) in enumerate(match) if b]
                for i in matchedIdxs:
                    print("Got Obama at", KnownFaceDic["names"][i])
            else:
                print("Нема Обами")
        # i = 0
        # ei = len(KnownFaceDic["encodings"])
        # while i < ei:
        #     print(KnownFaceDic["encodings"][i], i, KnownFaceDic["names"][i])
        #     i += 1
    return
        
## GUI
LoadDirList()   
wnd = tk.Tk(screenName='Faces 0.004')
wnd.title('Faces 0.004')
# wnd.geometry("1024x600")
frame1 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=10)
label1 = tk.Label(master=frame1,
                  text='Пошук облич у файлах зображень (невідомі серед відомих, 1 фото = 1 обличчя!)',
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
                  text='''1. Оберіть папки (по одній) з еталонними фото для наповнення бази даних.
                  Скануйте тільки один раз, а нові еталонні фото кладіть у нові папки (із наступним їх скануванням)''',
                  font=("Times New Roman", 13),
                  background='green',
                  foreground="white",
                  height=3
                  )
label2.pack()
but_lb = tk.Button(master=frame2,
                   text='Оберіть папку з еталонними фото ',
                   relief=RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: dir_load_allimg(wnd, "Оберіть каталог з еталонними фото"))
but_lb.pack()
frame2.pack()
##
frame3 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=8)
label3 = tk.Label(master=frame3,
                  text='2. Оберіть папку з фото невідомих осіб.',
                  font=("Times New Roman", 13),
                  background='green',
                  foreground="white",
                  height=3
                  )
label3.pack()
but_lw = tk.Button(master=frame3,
                   text='Оберіть папку з фото невідомих осіб.',
                   relief=RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: dir_load_wantedimg(wnd, "Оберіть папку з фото невідомих осіб."))
but_lw.pack()
frame3.pack()
##
frame4 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=8)
label4 = tk.Label(master=frame4,
                  text='3. Натисніть кнопку для початку пошуку. Результати буде збережено к папці з фото для пошуку у форматі TXT та XLS.',
                  font=("Times New Roman", 13),
                  background='green',
                  foreground="white",
                  height=3
                  )
label4.pack()
but_ab = tk.Button(master=frame4,
                   text='Пошук',
                   relief=RAISED,
                   height=1,
                   font=("Times New Roman", 16),
                   bg='lightgreen',
                   command=lambda: pic_search())
but_ab.pack()
frame4.pack()
##
wnd.mainloop()
if not fl_Dir_list_Saved: SaveDirList()