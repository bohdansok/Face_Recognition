# first attemt to create a rec and comp app
import cv2
import tkinter as tk
from tkinter import filedialog
import os
import numpy as np

def viewImage(image, name_of_window):
    cv2.namedWindow(name_of_window, cv2.WINDOW_NORMAL)
    cv2.imshow(name_of_window, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def get_images(path):
    # Ищем все фотографии и записываем их в image_paths
    image_paths = [os.path.join(path, f) for f in os.listdir(path) if not f.endswith('.happy')]
    
    images = []
    labels = []

    for image_path in image_paths:
        # Переводим изображение в черно-белый формат и приводим его к формату массива
        gray = Image.open(image_path).convert('L')
        image = np.array(gray, 'uint8')
        # Из каждого имени файла извлекаем номер человека, изображенного на фото
        subject_number = int(os.path.split(image_path)[1].split(".")[0].replace("subject", ""))
        
        # Определяем области где есть лица
        faces = faceCascade.detectMultiScale(image, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
        # Если лицо нашлось добавляем его в список images, а соответствующий ему номер в список labels
        for (x, y, w, h) in faces:
            images.append(image[y: y + h, x: x + w])
            labels.append(subject_number)
            # В окне показываем изображение
            cv2.imshow("", image[y: y + h, x: x + w])
            cv2.waitKey(50)
    return images, labels

    
wnd = tk.Tk()
wnd.title('Faces 0.001 / OpenCV')
ftypes = [('JPG files', '*.jpg'), ('All files', '*')]
dlg = filedialog.Open(wnd, filetypes = ftypes)
fn_wanted = dlg.show()
wnd.destroy()
# image = face_recognition.load_image_file(fn_wanted)
# face_landmarks_list = face_recognition.face_landmarks(image)
# print(face_landmarks_list)
image = cv2.imread(fn_wanted)
# rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
# cv2.imshow("Image", rgb_image)
# viewImage(image, fn_wanted)
# cropped = image[10:50, 100:150]
# viewImage(cropped, "Cropped "+fn_wanted)
# (h, w, d) = image.shape
# center = (w // 2, h // 2)
# M = cv2.getRotationMatrix2D(center, 120, 1.0)
# rotated = cv2.warpAffine(image, M, (w, h))
# viewImage(rotated, "на 120 градусiв")
# gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
# viewImage(gray_image, "в градациях серого")
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
faces = face_cascade.detectMultiScale(
    gray,
    scaleFactor= 1.1,
    minNeighbors= 6,
    minSize=(15, 15)
    )
faces_detected = "Face(s) detected: " + format(len(faces))
print(faces_detected)
# Рисуем квадраты вокруг лиц
for (x, y, w, h) in faces:
    cv2.rectangle(image, (x, y), (x+w, y+h), (255, 255, 0), 2)
viewImage(image,faces_detected)
###
wnd.mainloop()