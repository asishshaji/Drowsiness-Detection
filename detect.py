from time import sleep

import cv2
import numpy as np
from tensorflow.python.keras.models import load_model

np.set_printoptions(suppress=True)

leye = cv2.CascadeClassifier('haarcascadefiles/haarcascade_lefteye_2splits.xml')
reye = cv2.CascadeClassifier('haarcascadefiles/haarcascade_righteye_2splits.xml')

model = load_model('models/cnnCat2.h5')

cap = cv2.VideoCapture('video1.MP4')
vals = []

while (True):
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Video stopped")
        break
    cv2.imshow('Detector', frame)

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    left_eye = leye.detectMultiScale(gray)
    right_eye = reye.detectMultiScale(gray)
    rpred = 12
    lpred = 12

    for (x, y, w, h) in right_eye:
        r_eye = frame[y:y + h, x:x + w]
        r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
        r_eye = cv2.resize(r_eye, (24, 24))
        r_eye = r_eye / 255
        r_eye = r_eye.reshape(24, 24, -1)
        r_eye = np.expand_dims(r_eye, axis=0)

        rpred = model.predict_classes(r_eye)[0]
        break

    for (x, y, w, h) in left_eye:
        l_eye = frame[y:y + h, x:x + w]
        l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
        l_eye = cv2.resize(l_eye, (24, 24))
        l_eye = l_eye / 255
        l_eye = l_eye.reshape(24, 24, -1)
        l_eye = np.expand_dims(l_eye, axis=0)

        lpred = model.predict_classes(l_eye)[0]
        break
    vals.append((rpred, lpred))

    if (vals[len(vals) - 8:] == [(0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0), (0, 0)]):
        print("Definitely sleeping")
    elif (vals[len(vals) - 8:] == [(1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1), (1, 1)]):
        print("Not sleeping")

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
