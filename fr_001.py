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
import face_recognition, os
import tkinter as tk
from tkinter import filedialog


def sel_dir(rootwnd, Title): # selecting a directory with pictures
    sel_dir_path = tk.filedialog.askdirectory(parent=rootwnd, title=Title, mustexist=True)
    return os.path.normpath(sel_dir_path)

def dir_load_allimg(directory):
    # os.chdir(directory)
    cnt = 1
    for entry in os.scandir(directory):
        if (entry.path.endswith(".jpg") or entry.path.endswith(".png")) and entry.is_file():
            image = face_recognition.load_image_file(entry.path)
            enc = face_recognition.face_encodings(image)[0]
            print(cnt, entry.path)
            print(enc)
            cnt += 1
    return
   
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
wnd.destroy()
wnd.mainloop()