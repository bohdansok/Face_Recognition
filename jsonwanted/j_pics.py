import json, os
import base64
"""
https://data.gov.ua/dataset/7c51c4a0-104b-4540-a166-e9fc58485c1b

"ID"
"VD"
"OPPHOTO1"
"PHOTO1BASE64ENCODE"
"""
data = []
entries = os.scandir()
for ent in entries:
    if ent.name.endswith(".json"):
        with open(ent.path, encoding="utf-8-sig") as json_file:
            os.mkdir(ent.name.split(".")[0])
            data = json.load(json_file)
            for r in data:
                nm = os.path.join(os.getcwd(), ent.name.split(".")[0], r["ID"] + ".jpg")
                with open(nm, 'wb') as imf:
                    d = base64.decodebytes(r["PHOTO1BASE64ENCODE"].encode())
                    imf.write(d)
del(data)
