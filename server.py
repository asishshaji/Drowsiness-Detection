from flask import Flask, request, jsonify
import cv2
from keras.models import load_model
import numpy as np
import os
import base64
import glob
from flask_cors import CORS

os.environ['KERAS_BACKEND'] = 'theano'

leye = cv2.CascadeClassifier('haarcascadefiles/haarcascade_lefteye_2splits.xml')
reye = cv2.CascadeClassifier('haarcascadefiles/haarcascade_righteye_2splits.xml')

model = load_model('models/cnnCat2.h5')

app = Flask(__name__)
CORS(app)


@app.route('/detect', methods=["GET", "POST"])
def detect():
    if request.method == "POST":
        image = request.json['file']
        if image:
            img = base64.decodebytes(image.encode())
            npimg = np.fromstring(img, dtype=np.uint8)
            image = cv2.imdecode(npimg, 1)

            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            left_eye = leye.detectMultiScale(gray)
            right_eye = reye.detectMultiScale(gray)
            rpred = 12
            lpred = 12
            for (x, y, w, h) in right_eye:
                r_eye = image[y:y + h, x:x + w]
                r_eye = cv2.cvtColor(r_eye, cv2.COLOR_BGR2GRAY)
                r_eye = cv2.resize(r_eye, (24, 24))
                r_eye = r_eye / 255
                r_eye = r_eye.reshape(24, 24, -1)
                r_eye = np.expand_dims(r_eye, axis=0)

                rpred = model.predict_classes(r_eye)[0]
                break

            for (x, y, w, h) in left_eye:
                l_eye = image[y:y + h, x:x + w]
                l_eye = cv2.cvtColor(l_eye, cv2.COLOR_BGR2GRAY)
                l_eye = cv2.resize(l_eye, (24, 24))
                l_eye = l_eye / 255
                l_eye = l_eye.reshape(24, 24, -1)
                l_eye = np.expand_dims(l_eye, axis=0)
                lpred = model.predict_classes(l_eye)[0]
                break
            files = glob.glob("uploads/*")
            for f in files:
                os.remove(f)

            if rpred == 0 and lpred == 0:
                return jsonify(result="Definitely sleeping", level=2)
            elif (lpred == 1 and rpred == 0) or (lpred == 0 and rpred == 1):
                return jsonify(result="Probably sleeping", level=1)
            else:
                return jsonify(result="Not sleeping", level=0)

    return "hey"


if __name__ == '__main__':
    app.run(host="0.0.0.0")
