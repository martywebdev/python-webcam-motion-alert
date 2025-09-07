import glob
import os
import shutil
import cv2
import time
from threading import Thread

# Import your email sending function
from emailing import send_email_solution

# Initialize video capture
video = cv2.VideoCapture(0)
time.sleep(1)

first_frame = None
status_list = []
count = 1
all_images = []
image_with_object = None

# Folder for sent images
sent_folder = "sent"
os.makedirs(sent_folder, exist_ok=True)

# Function to clean the images folder
def clean_folder():
    global all_images, image_with_object, count
    for file in all_images:
        if os.path.exists(file):
            os.remove(file)
    all_images = []
    image_with_object = None
    count = 1
    print("Folder cleaned")

# Main loop
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

    # Compute difference between current frame and first frame
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

        # Save motion frame
        img_path = f'images/{count}.png'
        os.makedirs('images', exist_ok=True)
        cv2.imwrite(img_path, frame)
        count += 1
        all_images = glob.glob('images/*.png')
        image_with_object = all_images[len(all_images)//2]
        break

    status_list.append(status)
    status_list = status_list[-2:]

    # Trigger email and cleanup if motion stopped
    if status_list == [1, 0] and image_with_object and os.path.exists(image_with_object):
        # Copy file first to sent folder
        saved_path = os.path.join(sent_folder, os.path.basename(image_with_object))
        shutil.copy(image_with_object, saved_path)

        # Start daemon threads
        email_thread = Thread(target=send_email_solution, args=(saved_path,))
        email_thread.daemon = True
        email_thread.start()

        clean_thread = Thread(target=clean_folder)
        clean_thread.daemon = True
        clean_thread.start()

        # Reset first frame to adapt to new background
        first_frame = None

    # Display video
    cv2.imshow("Video", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release resources
video.release()
cv2.destroyAllWindows()
