import json

import requests
import base64

url = "http://127.0.0.1:5000/detect"
image = "/home/asish/Desktop/me.jpg"

with open(image, "rb") as img:
    data = base64.b64encode(img.read()).decode('utf-8')

# req = requests.post(url, data=json.dumps({"file": data}))
#
# print(req)
with open("test.jpg", "wb") as fh:
    fh.write(base64.decodebytes(data.encode()))
