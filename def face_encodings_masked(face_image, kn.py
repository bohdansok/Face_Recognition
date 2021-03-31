import face_recognition
from face_recognition import api as frapi
import numpy as np
import dlib


class Full_object_detection_masked(dlib.full_object_detection):
    def part(self, idx:int):
        if idx in range(2, 15) or idx in range(48, 68):
            return (0, 0)
        return super().part(idx)
    
    def parts(self):
        lst = dlib.points()
        for idx in range(0, 2):
            old_x = super().part(idx).x
            old_y = super().part(idx).y
            lst.insert(idx, dlib.point(old_x, old_y))
        for idx in range(2, 15):
            lst.insert(idx, dlib.point(0, 0))
        for idx in range(15, 29):
            old_x = super().part(idx).x
            old_y = super().part(idx).y
            lst.insert(idx, dlib.point(old_x, old_y))
        for idx in range(29, 36):
            lst.insert(idx, dlib.point(0, 0))
        for idx in range(36, 48):
            old_x = super().part(idx).x
            old_y = super().part(idx).y
            lst.insert(idx, dlib.point(old_x, old_y))    
        for idx in range(48, 68):
            lst.insert(idx, dlib.point(0, 0))
        return lst
    
    
def face_encodings_masked(face_image, known_face_locations=None, num_jitters=1, model="large"):
    # list_of_maske_points = [0, 1, 15:47]
    """
    Given an image, return the 128-dimension face encoding for each face in the image.

    :param face_image: The image that contains one or more faces
    :param known_face_locations: Optional - the bounding boxes of each face if you already know them.
    :param num_jitters: How many times to re-sample the face when calculating encoding. Higher is more accurate, but slower (i.e. 100 is 100x slower)
    :param model: Optional - which model to use. "large" (default) or "small" which only returns 5 points but is faster.
    :return: A list of 128-dimensional face encodings (one for each face in the image)
    """
    raw_landmarks = frapi._raw_face_landmarks(face_image,
                                        known_face_locations,
                                        model)
    masked_raw_landmarks = []
    for lm in raw_landmarks:
        masked_raw_landmarks.append(Full_object_detection_masked(lm.rect, lm.parts()))
    return [np.array(
        frapi.face_encoder.compute_face_descriptor(
            face_image,
            raw_landmark_set,
            num_jitters)) for raw_landmark_set in masked_raw_landmarks]


image = face_recognition.load_image_file("1.jpg")
# calling modified face_encodings with truncated face landmarks..
enc_masked = face_encodings_masked(image, known_face_locations=None, num_jitters=1, model="large")
# calling standard face_encodings with normal face landmarks..
enc_full = frapi.face_encodings(image, known_face_locations=None, num_jitters=1, model="large")
print("Difference between face encodings with partial (masked) and full landmarks:")
print(enc_full[0] - enc_masked[0])