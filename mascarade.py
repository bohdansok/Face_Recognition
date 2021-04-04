from tkinter import filedialog, simpledialog
import face_recognition
import cv2
import numpy as np


def put_virt_mask(image_basic, nous, mod5_68, model_hogcnn, executor, fl_MultyTh=False, fl_wanted_scan=False):
    """[Applying virtual medical masks of 4 types]

    Args:
        image_basic ([type]): [description]
        nous ([type]): [description]
        mod ([type]): [description]
        model_hogcnn ([type]): [description]
        executor ([type]): [description]
        fl_MultyTh (bool, optional): [description]. Defaults to False.

    Returns:
        images [list]: [list of 5 images (np.array)]
        boxes [list]: [list of face boxes found on basic image]
    """    
    #make local functions - just to be stylish
    frfl = face_recognition.face_locations
    frfland = face_recognition.face_landmarks
    images = []
    #
    if fl_MultyTh:
        boxes = executor.submit(frfl, image_basic, number_of_times_to_upsample=nous, model=model_hogcnn).result()
    else:
        boxes = frfl(image_basic, number_of_times_to_upsample=nous, model=model_hogcnn)
    if len(boxes) == 0:
        images.append([image_basic])
        return images, boxes
    if fl_wanted_scan:
        for box in boxes:
            images.append([image_basic])
        return images, boxes
    #convert BGR into RGB-colour
    rgb_image_basic_basic = cv2.cvtColor(image_basic, cv2.COLOR_BGR2RGB)
    #run on all boxes found at the image_basic
    #setting up colors
    blue_mask = (237, 234, 101)
    blue_mask_stripes = (242, 249, 170)
    black_mask = (17, 17, 17)
    black_mask_stripes = (42, 42, 42)
    white_resp_stripes = (220, 220, 220)
    white_resp = (250, 250, 250)
    resp_valve = (44, 191, 218)
    for box in boxes:
        image_6 = []
        rgb_image_basic = rgb_image_basic_basic.copy()
        image_6.append(rgb_image_basic.copy())
        basic_landmarks = frfland(rgb_image_basic,
                        [box],
                        mod5_68)
        #Making a simple mask model
        mask_list = []
        mask_list.extend([basic_landmarks[0].get("chin")[x] for x in range(1, 16)])
        mask_list.append(basic_landmarks[0]["nose_bridge"][1])
        mask = np.array(mask_list, np.int32)
        stripe_0_list = []
        stripe_0_list.append(basic_landmarks[0]["chin"][1])
        stripe_0_list.append(basic_landmarks[0]["nose_bridge"][1])
        stripe_0_list.append(basic_landmarks[0]["chin"][15])
        stripe_0 = np.array(stripe_0_list, np.int32)
        stripe_1_list = []
        stripe_1_list.append(basic_landmarks[0]["chin"][3])
        stripe_1_list.append(basic_landmarks[0]["nose_tip"][2])
        stripe_1_list.append(basic_landmarks[0]["chin"][13])
        stripe_1 = np.array(stripe_1_list, np.int32)
        stripe_2_list = []
        stripe_2_list.append(basic_landmarks[0]["chin"][4])
        stripe_2_list.append(basic_landmarks[0]["bottom_lip"][4])
        stripe_2_list.append(basic_landmarks[0]["chin"][12])
        stripe_2 = np.array(stripe_2_list, np.int32)
        valve_left_center = basic_landmarks[0]["top_lip"][6]
        valve_right_center = basic_landmarks[0]["top_lip"][0]
        valve_main_axes = int(
            (basic_landmarks[0]["bottom_lip"][4][1] - basic_landmarks[0]["nose_tip"][2][1]) * 0.8
            )
        valve_min_axes = int(valve_main_axes // 2)
        stripe_0_width = int((basic_landmarks[0]["nose_bridge"][2][1] - basic_landmarks[0]["nose_bridge"][1][1]) * 0.35)
        stripe_1_width = int((basic_landmarks[0]["nose_bridge"][3][1] - basic_landmarks[0]["nose_bridge"][1][1]) * 0.5)
        stripe_2_width = stripe_0_width
    #Applying digital blue mask
        image_blue_mask = cv2.drawContours(rgb_image_basic, [mask], -1, blue_mask, thickness=cv2.FILLED)
        image_blue_mask = cv2.polylines(image_blue_mask, [stripe_0], False, blue_mask_stripes, thickness=stripe_0_width)
        image_blue_mask = cv2.polylines(image_blue_mask, [stripe_1], False, blue_mask_stripes, thickness=stripe_1_width)
        image_blue_mask = cv2.polylines(image_blue_mask, [stripe_2], False, blue_mask_stripes, thickness=stripe_2_width)
        image_6.append(image_blue_mask.copy())
    #Applying digital black mask
        image_black_mask = cv2.drawContours(rgb_image_basic, [mask], -1, black_mask, thickness=cv2.FILLED)
        image_black_mask = cv2.polylines(image_black_mask, [stripe_0], False, black_mask_stripes, thickness=stripe_0_width)
        image_black_mask = cv2.polylines(image_black_mask, [stripe_1], False, black_mask_stripes, thickness=stripe_1_width)
        image_black_mask = cv2.polylines(image_black_mask, [stripe_2], False, black_mask_stripes, thickness=stripe_2_width)
        image_6.append(image_black_mask.copy())
     #Applying digital white mask
        image_white_mask = cv2.drawContours(rgb_image_basic, [mask], -1, white_resp, thickness=cv2.FILLED)
        image_white_mask = cv2.polylines(image_white_mask, [stripe_0], False, white_resp_stripes, thickness=stripe_0_width)
        image_white_mask = cv2.polylines(image_white_mask, [stripe_1], False, white_resp_stripes, thickness=stripe_1_width)
        image_white_mask = cv2.polylines(image_white_mask, [stripe_2], False, white_resp_stripes, thickness=stripe_2_width)
        image_6.append(image_white_mask.copy())
    #Applying digital respirator with left-side valve
        image_resp_left = cv2.drawContours(rgb_image_basic, [mask], -1, white_resp, thickness=cv2.FILLED)
        image_resp_left = cv2.polylines(image_resp_left, [stripe_0], False, white_resp_stripes, thickness=stripe_0_width)
        image_resp_left = cv2.polylines(image_resp_left, [stripe_1], False, white_resp_stripes, thickness=stripe_1_width)
        image_resp_left = cv2.polylines(image_resp_left, [stripe_2], False, white_resp_stripes, thickness=stripe_2_width)
        image_resp_left = cv2.ellipse(image_resp_left, valve_left_center, (valve_main_axes, valve_min_axes), 285, 0, 360, resp_valve, -1)
        image_6.append(image_resp_left.copy())
    #Applying digital respirator with right-side valve
        image_resp_right = cv2.drawContours(rgb_image_basic, [mask], -1, white_resp, thickness=cv2.FILLED)
        image_resp_right = cv2.polylines(image_resp_right, [stripe_0], False, white_resp_stripes, thickness=stripe_0_width)
        image_resp_right = cv2.polylines(image_resp_right, [stripe_1], False, white_resp_stripes, thickness=stripe_1_width)
        image_resp_right = cv2.polylines(image_resp_right, [stripe_2], False, white_resp_stripes, thickness=stripe_0_width)
        image_resp_right = cv2.ellipse(image_resp_right, valve_right_center,
                (valve_main_axes, valve_min_axes), 255, 0, 360, resp_valve, -1)
        image_6.append(image_resp_right.copy())
        #adding list of 6 images to the common images list
        images.append(image_6.copy())
        del(image_6)
        del(rgb_image_basic)
        del(image_blue_mask)
        del(image_black_mask)
        del(image_white_mask)
        del(image_resp_left)
        del(image_resp_right)
    del(frfl)
    del(frfland)
    return images, boxes

imfn = filedialog.askopenfilename("Choose a JPG-file with probe face")
image_basic = face_recognition.load_image_file(imfn)
aimages = []
aimages, boxes = put_virt_mask(image_basic,
                              1,
                              "large",
                              "hog",
                              None, False,
                              False)
for box_index, box in enumerate(boxes):
    cv2.imshow("Mascarade - 0", aimages[box_index][0])
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imshow("Mascarade - 1", aimages[box_index][1])
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imshow("Mascarade - 2", aimages[box_index][2])
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imshow("Mascarade - 3", aimages[box_index][3])
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imshow("Mascarade - 4", aimages[box_index][4])
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    cv2.imshow("Mascarade - 5", aimages[box_index][5])
    cv2.waitKey(0)
    cv2.destroyAllWindows()
cv2.destroyAllWindows()