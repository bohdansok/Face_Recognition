import requests, time, os
#import urllib.request, urllib.error, urllib.parse

"""
6   <meta name="Description" content="Дзюба Віталій Миколайович, Інженер з експлуатації та технічного обслуговування шукає роботу у Києві. Про себе: 52&nbsp;роки, вища освіта, досвід роботи 23 роки. Цікавить повна зайнятість, ЗП від 35000 грн."> 
229     <span class="text-muted">Резюме від&nbsp;24 липня 2021</span> <span class="label label
231     <img width="300" height="400" src="//i.work.ua/sent_photo/7/8/0/7808903ace02312411cd73f5fa25bec5.jpg" alt="">
240     <dd>33&nbsp;роки</dd>
244     <dd>Бориспіль</dd>

34     <title>Сторiнку не знайдено. Помилка 404 — Work.ua</title>
102    <h1>На жаль, резюме не знайдено</h1>


5074715

urllib.error.HTTPErro
"""

PROF_START = 1
PROF_END = 99999999
WORKUA = "workua"
DATEOFPROC = "25.07.2021"
image_url = ""
if_picture = ""

report = open("alljobs.txt", "wt")

file_c = 0
folder_c = 0 # starting folder changed!
file_total = 0
bad_f = 0
c = 0
print_once = True
jpg_picsfolder = os.path.join(os.getcwd(), WORKUA, str(folder_c))
if not os.path.exists(jpg_picsfolder):
    os.mkdir(jpg_picsfolder)

for prof in range(PROF_START, PROF_END):
    text = []
    r = requests.get(f"https://www.work.ua/resumes/{prof}/")
    text = r.text.split("\n")
    # for i, line in enumerate (text):
    #     print(i, "**", line)
    # print("+++++++++++++++++++++++++++++++++++++++++++++++++++++")
    if text[33].find("<title>Сторiнку не знайдено. Помилка 404 — Work.ua</title>") == -1:
        try:
            if_pcture = text[224]
        except:
            print(f"Some error with picture line with {prof}: {if_picture}")
            continue
        if if_pcture.find('<img width="300" height="400" src="') != -1:
            image_url = text[224].replace("\n", "").removeprefix('                            <img width="300" height="400" src="').removesuffix('" alt="">')
            image_url = "".join(["https:", image_url])
            img_filename = os.path.split(image_url)[1]
            img_filename_tag = img_filename.split(".")[0]
            try:
                img_r = requests.get(image_url)
            except Exception as err:
                print(err)
                continue
            full_img_filename = os.path.join(jpg_picsfolder, img_filename)
            with open(full_img_filename,'wb') as f:
                f.write(img_r.content)
            file_c += 1
            if file_c > 35000:
                folder_c += 1
                jpg_picsfolder = os.path.join(os.getcwd(), WORKUA, str(folder_c))
                os.mkdir(jpg_picsfolder)
                file_c = 0
            rep_str = text[5].removeprefix('    <meta name="Description" content="').removesuffix('">').replace("&nbsp", " ")
            date_resume = text[222].removeprefix('                            <span class="text-muted">').split('</span>')[0].replace("&nbsp;", " ")
            rep_str = " ".join([rep_str, date_resume, f"(вік станом на {DATEOFPROC})"])
            print(img_filename_tag, rep_str, file=report, sep="\t", flush=True)
            print(prof, ":", img_filename_tag, rep_str, sep="\t")
            time.sleep(1)
            file_total += 1
        else:
            continue
    else:
        bad_f += 1
        continue

report.close()
print(f"Found {file_total} resumes with a picture; {bad_f} without picture were skipped,")


    
