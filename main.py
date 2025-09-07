import glob
import os
import shutil
import cv2
import time
from emailing import send_email_solution
from threading import Thread, Lock

video = cv2.VideoCapture(0)
time.sleep(1)

first_frame = None
status_list = []
count = 1
all_images = []
image_with_object = None

lock = Lock()

def clean_folder():
    global all_images, image_with_object, count
    with lock:
        for file in all_images:
            if os.path.exists(file):
                os.remove(file)
        all_images = []
        image_with_object = None
        count = 1
        print("Folder cleaned")
def send_email_safe(image_path):
    with lock:
        send_email_solution(image_path)
while True:
    status = 0
    ret, frame = video.read()
    if not ret:
        break

    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray_frame = cv2.GaussianBlur(gray_frame, (21, 21), 0)

    if first_frame is None:
        first_frame = gray_frame
        continue

    delta_frame = cv2.absdiff(first_frame, gray_frame)
    thresh_frame = cv2.threshold(delta_frame, 60, 255, cv2.THRESH_BINARY)[1]
    thresh_frame = cv2.dilate(thresh_frame, None, iterations=2)

    contours, _ = cv2.findContours(thresh_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 5000:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)
        status = 1

        # Save image
        img_path = f'images/{count}.png'
        cv2.imwrite(img_path, frame)
        count += 1
        all_images = glob.glob('images/*.png')
        image_with_object = all_images[len(all_images)//2]
        break

    status_list.append(status)
    status_list = status_list[-2:]

    if status_list == [1, 0] and image_with_object and os.path.exists(image_with_object):
        # Save copy first
        sent_folder = "sent"
        os.makedirs(sent_folder, exist_ok=True)
        saved_path = os.path.join(sent_folder, os.path.basename(image_with_object))
        shutil.copy(image_with_object, saved_path)

        # Start threads on the copied file
        email_thread = Thread(target=send_email_solution, args=(saved_path,))
        clean_thread = Thread(target=clean_folder)

        email_thread.start()
        clean_thread.start()

        # Reset first frame after motion
        first_frame = None

    cv2.imshow("Video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

video.release()
cv2.destroyAllWindows()
