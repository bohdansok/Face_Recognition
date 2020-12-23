# import face_recognition


# baiden_image = face_recognition.load_image_file("biden.jpg")
# ob_image = face_recognition.load_image_file("obama.jpg")
# unknown_image = face_recognition.load_image_file("obama2.jpg")

# biden_encoding = face_recognition.face_encodings(baiden_image)[0]
# ob_encoding = face_recognition.face_encodings(ob_image)[0]
# unknown_encoding = face_recognition.face_encodings(unknown_image)[0]

# results = face_recognition.compare_faces([biden_encoding], unknown_encoding)
# print(results)
# results = face_recognition.compare_faces([ob_encoding], unknown_encoding)
# print(results)
# print(biden_encoding)
# print(ob_encoding)
# print(unknown_encoding)

  
# first attemt to create a rec and comp app
# $ face_recognition --cpus -1
import face_recognition, os, pickle
import tkinter as tk
from tkinter import filedialog

## Global vars - Start
PicFileTypes = ['.jpg', '.JPG', '.jpeg', '.JPEG', '.png', '.PNG']
knownEncodings = []
knownNames = []
KnownFaceDic = {"encodings": knownEncodings, "names": knownNames}
## Global vars - End
##
def sel_dir(rootwnd, Title): # selecting a directory with pictures
    sel_dir_path = tk.filedialog.askdirectory(parent=rootwnd, title=Title, mustexist=True)
    return os.path.normpath(sel_dir_path)

def dir_load_allimg(directory):
    # os.chdir(directory)
    cnt = 1
    # en = []
    # nm = ""
    # data = {"encd": en, "nms": nm}
    data = {}
    for entry in os.scandir(directory):
        if (entry.path.lower().endswith(".jpg") 
            or entry.path.lower().endswith(".png")) and entry.is_file():
            image = face_recognition.load_image_file(entry.path)
            boxes = face_recognition.face_locations(image, model='hog') # maybe cnn - more accu and use GPU/CUDA,
            # hog - MUCH faster but less accurate
            if len(boxes) == 1:
                enc = face_recognition.face_encodings(image, boxes)[0]
                # data[enc] = entry.path
                # data = dict.fromkeys(enc, entry.path)
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
    f = open('Knownfaces.pkl', "ab")
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
   
wnd = tk.Tk(screenName='Faces 0.001')
# ftypes = [('JPG files', '*.jpg'), ('All files', '*')]
# dlg = filedialog.Open(wnd, filetypes = ftypes)
# fn_wanted = dlg.show()
# image = face_recognition.load_image_file(fn_wanted)
# unknown_encoding = face_recognition.face_encodings(image)[0]
dirpath = sel_dir(wnd, 'Select a directory with wanted pics')
# print(unknown_encoding)
# print(len(image))
print(dirpath)
# dirpath = dirpath.replace("/", r"\"")
dir_load_allimg(dirpath)
KnownFaceDic = facedic_load("Knownfaces.pkl")
# print(KnownFaceDic.items())
obama = face_recognition.load_image_file("obama.jpg")
obenc = face_recognition.face_encodings(obama)[0]
for key in KnownFaceDic.keys():
    if face_recognition.api.compare_faces(key, obenc, tolerance=0.6):
        print("Got Obama at", KnownFaceDic[key])
wnd.destroy()
wnd.mainloop()