import glob
import os.path
import shutil

import cv2
import time
from emailing import send_email, send_email_solution

video = cv2.VideoCapture(0)
time.sleep(1)

first_frame = None
status_list = []
count = 1
all_images = []
image_with_object = None
while True:
    status = 0
    check, frame = video.read()


    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame_gau = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    if first_frame is None:
        first_frame = gray_frame_gau

    delta_frame = cv2.absdiff(first_frame, gray_frame_gau)

    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
    # cv2.imshow('My Video', dil_frame)

    contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)


    for contour in contours:
        if cv2.contourArea(contour) < 10000: # this assume no moving object
            continue
        x, y, w, h = cv2.boundingRect(contour)
        rectangle = cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 3)

        if rectangle.any():
            status = 1

            cv2.imwrite(f'images/{count}.png', frame)
            count = count + 1
            all_images = glob.glob('images/*.png')

            index = int(len(all_images) / 2)

            image_with_object = all_images[index]
            break

    status_list.append(status)
    status_list = status_list[-2:]

    if status_list[0] == 1 and status_list[1] == 0 and image_with_object is not None and os.path.exists(image_with_object):

        send_email_solution(image_with_object)

        # save the sent image to another folder
        sent_folder = "sent"
        os.makedirs(sent_folder, exist_ok=True)

        saved_path = os.path.join(sent_folder, os.path.basename(image_with_object))
        shutil.copy(image_with_object, saved_path)

        # cleanup
        for file in all_images:
            if os.path.exists(file):
                os.remove(file)

        # reset state
        all_images = []
        image_with_object = None
        count = 1

    cv2.imshow("Video", frame)


    key = cv2.waitKey(1)

    if key == ord('q'):
        break

video.release()