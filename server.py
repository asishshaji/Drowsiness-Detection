from flask import Flask, request, jsonify
import cv2
from keras.models import load_model
import numpy as np
import os
import base64
from datetime import datetime
import glob

os.environ['KERAS_BACKEND'] = 'theano'

leye = cv2.CascadeClassifier(
    'haarcascadefiles/haarcascade_lefteye_2splits.xml')
reye = cv2.CascadeClassifier(
    'haarcascadefiles/haarcascade_righteye_2splits.xml')
model = load_model('models/cnnCat2.h5')

app = Flask(__name__)


# curl -i -X POST -H "Content-Type: multipart/form-data" -F "file=@/home/asish/Desktop/me.jpg" https://drowsinessapiproject.herokuapp.com/detect
@app.route('/detect', methods=["GET", "POST"])
def detect():
    if request.method == "POST":
        image = request.json['file']
        if image:
            imagename = f"{datetime.now().microsecond}.jpg"
            with open("uploads" + imagename, "w+") as fh:
                fh.write(base64.decodebytes(image.encode()))
            image = cv2.imread(os.path.join("uploads", imagename))

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            left_eye = leye.detectMultiScale(gray)
            right_eye = reye.detectMultiScale(gray)

            for (x, y, w, h) in right_eye:
                r_eye = image[y:y + h, x:x + w]
            r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
            r_eye = cv2.resize(r_eye, (24, 24))
            r_eye = r_eye / 255
            r_eye = r_eye.reshape(24, 24, -1)
            r_eye = np.expand_dims(r_eye, axis=0)
            rpred = model.predict_classes(r_eye)
            break

            for (x, y, w, h) in left_eye:
                l_eye = image[y:y + h, x:x + w]
                l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
                l_eye = cv2.resize(l_eye, (24, 24))
                l_eye = l_eye / 255
                l_eye = l_eye.reshape(24, 24, -1)
                l_eye = np.expand_dims(l_eye, axis=0)
                lpred = model.predict_classes(l_eye)
                break
            files = glob.glob("uploads/*")
            for f in files:
                os.remove(f)

            if rpred[0] == 0 and lpred[0] == 0:
                return jsonify(result="Definitely sleeping", level=2)
            elif (lpred[0] == 1 and rpred[0] == 0) or (lpred[0] == 0 and rpred[0] == 1):
                return jsonify(result="Probably sleeping", level=1)
            else:
                return jsonify(result="Not sleeping", level=0)

    return "hey"


if __name__ == '__main__':
    app.run()
