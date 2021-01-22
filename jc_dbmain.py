import json
"""
"ID"
"OVD"
"CATEGORY"
"FIRST_NAME_U"
"LAST_NAME_U"
"MIDDLE_NAME_U"
"FIRST_NAME_R"
"LAST_NAME_R"
"MIDDLE_NAME_R"
"FIRST_NAME_E"
"LAST_NAME_E"
"MIDDLE_NAME_E"
"BIRTH_DATE"
"SEX"
"LOST_DATE"
"LOST_PLACE"
"ARTICLE_CRIM"
"RESTRAINT"
"CONTACT"
"PHOTOID"
"""
data = []
with open("mvswantedperson_1.json", encoding="utf-8-sig") as json_file:
    data = json.load(json_file)
fn = "mainwanted.txt"
f = open(fn, "wt")
st = "\t".join(["ID", "OVD", "CATEGORY", "FIRST_NAME_U",
                  "LAST_NAME_U", "MIDDLE_NAME_U", "FIRST_NAME_R",
                  "LAST_NAME_R", "MIDDLE_NAME_R", "MIDDLE_NAME_R",
                  "FIRST_NAME_E", "LAST_NAME_E", "MIDDLE_NAME_E",
                  "BIRTH_DATE", "BIRTH_DATE", "SEX", "LOST_DATE",
                  "LOST_PLACE", "ARTICLE_CRIM", "RESTRAINT", "CONTACT",
                  "PHOTOID"]
                  )
print(st, file=f, end="\n", flush=False)
for r in data:
    s = "\t".join([r["ID"], r["OVD"], r["CATEGORY"], r["FIRST_NAME_U"],
                  r["LAST_NAME_U"], r["MIDDLE_NAME_U"], r["FIRST_NAME_R"],
                  r["LAST_NAME_R"], r["MIDDLE_NAME_R"], r["MIDDLE_NAME_R"],
                  r["FIRST_NAME_E"], r["LAST_NAME_E"], r["MIDDLE_NAME_E"],
                  r["BIRTH_DATE"], r["BIRTH_DATE"], r["SEX"], r["LOST_DATE"],
                  r["LOST_PLACE"], r["ARTICLE_CRIM"], r["RESTRAINT"], r["CONTACT"],
                  r["PHOTOID"]]
                  )
    print(s, file=f, end="\n", flush=False)
del(data)
f.flush()
f.close()