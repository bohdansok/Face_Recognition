
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
from datetime import datetime

## Global vars - Start
PicFileTypes = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG']
knownEncodings = []
knownNames = []
KnownFaceDic = {"encodings": knownEncodings, "names": knownNames}
BaseDirectory = ''
WantedDirectory = ''
## Global vars - End
##
def sel_dir(rootwnd, Title): # selecting a directory with pictures
    sel_dir_path = tk.filedialog.askdirectory(parent=rootwnd, title=Title, mustexist=True)
    return os.path.normpath(sel_dir_path)

def dir_load_allimg(parwnd, title):
    directory = sel_dir(parwnd, title)
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
    fn = os.path.join(os.path.join(os.getcwd(), "_DB"), (str(datetime.now()).replace(":", ".") + ".pkl"))
    f = open(fn, "wb")
    pickle.dump(data, f, protocol=pickle.HIGHEST_PROTOCOL)
    f.close()
    return

def facedic_load(dicfilename):
    try:
        f = open(dicfilename, "rb")
    except (IOError, EOFError) as e:
        print("Dictionary file missing or corrupt. {}".format(e.args[-1]))
    else:
        picdic = {}
        picdic = pickle.load(f)
    f.close()
    print("Face encodings loaded from", dicfilename)
    return picdic

def pic_search():
    for entry in os.scandir(os.path.join(os.getcwd(), "_DB")):
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
        i = 0
        ei = len(KnownFaceDic["encodings"])
        while i < ei:
            print(KnownFaceDic["encodings"][i], i, KnownFaceDic["names"][i])
            i += 1
    return
        
## GUI   
wnd = tk.Tk(screenName='Faces 0.004')
wnd.title('Faces 0.004')
wnd.geometry("1024x600")
frame1 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=10)
label1 = tk.Label(master=frame1,
                  text='''Пошук облич у файлах зображень
                  (невідомі серед відомих, 1 фото = 1 обличчя!)''',
                  font=("Times New Roman", 15),
                  background='green',
                  foreground="white",
                  height=3
                  )
label1.pack()
frame1.pack()
frame2 = tk.Frame(master=wnd, relief=tk.RAISED, borderwidth=8)
label2 = tk.Label(master=frame2,
                  text='''1. Оберіть кпапки (по одній) з еталонними фото для наповнення бази даних.
                  Сканувати тільки олин раз. Нові фото класти у нові папки''',
                  font=("Times New Roman", 12),
                  background='green',
                  foreground="white",
                  height=3
                  )
label2.pack()
but_lb = tk.Button(master=frame2, text='Оберіть каталог з еталоними фото ', relief=RAISED, command=dir_load_allimg(wnd, "Оберіть каталог з еталоними фото"))
but_lb.pack()
frame2.pack()
but_ab = tk.Button(master=wnd, text='Пошук',  relief=RAISED, command=pic_search())
but_ab.pack()
wnd.mainloop()