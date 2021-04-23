# Face Recognition v1.97
The most recent release of the app:
-	Now this face recognition app is a hybrid of Face_recognition  /dlib and Mediapipe frameworks. It looks like CNN face detection model from Mediapipe works in 50 times faster even on CPU then dlib HOG model.

Найсвіжіший випуск, вер. 1.97:
-	Зараз цей додаток з розпізнавання обличь став гібридом бібліотек Face_recognition  /dlib та Mediapipe. Схоже, що CNN модель виявлення обличь з Mediapipe працює у 50 разів швидше навіть на ЦПУ, ніж модель HOG, реалізована у dlib.


# Face Recognition v1.96
Starting from this release the latest only  version of code to be placed here. 
The most recent release of the app:
-	code is more structured now (some functions are moved to MYFR1.PY module as well as all of language-depended dialogs, screen labels etc.- to MYFRLANG.PY), a new Face_Dictionary  class was  implemented ;
-	code became slightly more DRY;
-	some bugs fixed;
-	also you can try MASCARADE.PY to sеe  (and then save the results as a file) how virtual mask application works: run and choose a face picture (multiface ones are good too);
-	a new feature added: use CHANGEPATH.PY for batch modification of the images’  pathes directly in  pkl – face encodings data files. BEWARE! You need to edit source code first by modifying < change_dic> dictionary according to your needs. 

Найсвіжіший випуск, вер. 1.96:
Починаючи з цього релізу тільки остання версія буде розміщена тут.
-	код став більш структурований (деякі функції перенесено в окремий модулт MYFR1.PY, так само як усі залежні від мови діалоги, екранні мітки тощо - до мдулю MYFRLANG.P), введено новий клас Face_Dictionary;
-	код став трохи більше DRY
-	виправлено помилки;
-	також додано програмку mascarade.py. Запустить, щоб побачити (та зберегти результат у файл) як працює віртуальне накладання маски: просто оберіть картинку з обличчям (фото з декількома обличчями теж годяться);
- додано нову можливість: використайте  CHANGEPATH.PY для пакетної зміни шляху до файлів зображень безпосередньо у pkl - файлах даних кодувань обличь. УВАГА! Вам доведеться трохи корегувати код скріпта, змінивши значення < change_dic>  відповідно до ваших потреб.


# Face Recognition v1.94
The most recent release of the app:
-	next attempt to solve "medical mask issue" and IT WORKS! The virtual mask (5 types) application method has been used, so now there 6 encodings instead of 1 made for each reference face (on single- or multiface pictures);
-	code became slightly more DRY;
-	some bugs fixed;in Ukrainian only for the moment;
-	also you can try mascarade.py to sеe how virtual mask application works: run and choose a face picture (multyface ones are good too).

Найсвіжіший випуск, вер. 1.94:
-	наступнаспроба вирішити проблему "медичних маск" і ТЕПЕР ВСЕ ПРАЦЮЄ! Використано метод віртуального накладання на зображення обличчя маск (5 різних типів), тож замість 1 кодування для кожного еталонного обличчя розраховується 6;
-	код став трохи більше DRY
-	виправлено помилки;
-	також додано програмку mascarade.py. Запустить, щоб побачити як працює віртуальне накладання маски: просто оберіть картинку з обличчям (фото з декількома обличчями теж годяться).

# Face Recognition v1.92
The most recent release of the app:
-	first attempt to solve "medicalmask issue" (it doesn't work good enough so far);
-	code became slightly more DRY;
-	help file updated.
-	some bugs fixed.

Найсвіжіший випуск, вер. 1.92:
-	перша спроба вирішити проблему "медичних маск" (поки ще не дуже працює);
-	код став трохи більше DRY
-	оновлено файл довідки;
-	виправлено помилки.

# Face Recognition v1.90
The most recent release of the app:
-	now both wanted and found faces are highlighted by frames, including group pictures, at xlsx-report sheet;
-	new, down-compatible face encodings data files format implemented;
-	help file added.

Найсвіжіший випуск, вер. 1.90:
-	тепер у звіті обличчя на фото виділяються рамками, у тому числі й на групових зображеннях;
-	при використанні групових фото в якості пошукових виокремлення обличь та послідовний пошук га ними відбувається автоматично;
-	впроваджено новий, зворотно-сумісний із старим, формат файлів даних кодувань обличь;
-	додано файл довідки.

# Face Recognition v1.84
The most recent release of the app:
- aspect ratio issue of the thumbnails in the xlsx-reports is solved now;
- optimization (in fact – consolidation) of the face encodings data files is now available;
- reporting code became faster and more compactж
- code is shorted a little bit.

Найсвіжіший випуск, вер. 1.84:
- виправлено проблему з порушення пропорцій ескізів в xlsx-звітах;
- додано можливість оптимізації (шляхом консолідації) файлів даних кодувань обличь;
- код підготовки звіту став швидшим та компактнішим;
- ше трохи скорочення коду.

# Face Recognition v1.7
- now it's in Ukrainian and English;
- memory leaks removed (at least ones I've recognized);
- multithread approach implemented for the most "heavy" mathematics;
- slow disk IO operations are minimized;
- some other basic optimization being done (now it works up to 3 times faster than v.1.5)

- тепер українською та англійською мовою;
- "витоки" пам’яті усунене (як мінімум ті, що я виявив);
- застосовано багатопотоковий підхід для найбільш важких математичних обчислень;
- мінімізовано повільні дискові операції;
- проведено іншу базову оптимізацію (тепер працює  у 3 рази швидше, ніж вер.1.5)

# Face Recognition v1.6
Skipped / Пропущено.

# Face Recognition v1.5
I've done a good way to make an app that scans millions of pictures and then finding out wanted individuals among them. And it really works fast and accurate due to face_recognition and dlib libraries. Sure, the app could be simpler but I've needed to fill it with good usability and all reasonable safeguards. Current version of the app has Ukrainian interface only (English version is coming soon).

Я пройшов непоганий шлях задля створення додатку, що сканує мільйони фотографій та потім відшуковує серед них фото осіб, які перебувають у розшуку. І він дійсно швидко працює завдяки бібліотекам face_recognition та dlib. Безумовно, код може бути простішим, але мені було потрібно забезпечити зручність і простоту користування та передбачити усі необхідні запобіжники. Поточна версія має українську мову інтерфейсу (англійська буле незабаром).
