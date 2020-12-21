# first attemt to create a rec and comp app
import face_recognition
import tkinter as tk
from tkinter import filedialog


wnd = tk.Tk(screenName='Faces 0.001')
ftypes = [('JPG files', '*.jpg'), ('All files', '*')]
dlg = filedialog.Open(wnd, filetypes = ftypes)
fn_wanted = dlg.show()
image = face_recognition.load_image_file(fn_wanted)
face_landmarks_list = face_recognition.face_landmarks(image)
print(face_landmarks_list)
wnd.mainloop()