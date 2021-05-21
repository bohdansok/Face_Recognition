# -*- coding: utf-8 -*-
"""Special thanks to:
-	face_recognition by Adam Geitgey (https://github.com/ageitgey/face_recognition) under MIT License;
-	dlib by Davis E. King (https://github.com/davisking/dlib ) under BSL-1.0 License;
-	Mediapipe by Google (https://github.com/google/mediapipe) under Apache-2.0 License.
"""
__author__ = "Bohdan SOKRUT"
__www__ = 'https://github.com/bohdansok/Face_Recognition'
__version__ = '1.03'

"""  language data module"""

lang = {
    "eng": {
        "dir_load_allimg": ["Select a folder with reference pictures",
                           "Attention!", "Can't create working folder %s",
                           "Information", "Added %d face(s) from %d  pictures at %s. Saving encodings to file..."],
        "dir_load_allimg_sub": ["Select a folder with reference pictures",
                                "Attention!", "Can't create working folder %s",
                                "Information", "Added %d face(s) from %d  pictures at %s. Saving encodings to file..."],
        "dir_load_wantedimg": ["Choose folder with wanted persons' pictures",
                               "Attention!", "Can't create working folder %s",
                               "Attention!", "Can't write search parameters to file %s. Reports to be saved at the app's working folder",
                               'Information', "Added %d faces from %d images at folder %s. Saving encodings to file..."],
        "pic_search": ["Face compare accuracy", "Less is more accurate (0<x<1, default is 0.45):",
                       "Attention!", "Can't find/read working folder %s",
                       "Attention!", "Can't find/read working folder %s",
                       "Attention!", "Can't find/read wanted individuals(s) data file %s. Please, scan the appropriate folder with pictures",
                       "Attention!", "Can't find/read search options file: {}",
                       " - found %d face(s) among %d reference data files",
                       "Attention!", "Can't write report {}",
                       "Attention!", "Can't write report {}",
                       "Attention!", "Can't write report {}",
                       "Attention!", "Can't write report {}",
                       'Information', "Searched %d faces among %d data files. Reports saved to %s and %s",
                       'Information',  "Searched %d faces among %d data files. Found nothing",
                       "Report created ", #23
                       "by %s", #24
                       "Accuracy: ", #25
                       "Wanted person picture file", #26
                       "Picture of wanted person", #27
                       "Face of wanted person", #28
                       '"Reference" face', #29
                       '"Reference" picture', #30
                       "Reference picture file", #31
                       "Additional data", #32
                       "Similarity, %", #33
                       "Thumbnail is not available", #34
                       "Additional comment:"], #35
        "load": ["Attention!!", "Can't read/find face encodings file: {}"],
        "save": ["Attention!", "Can't create data file %s"],
        "LoadDirList": ["Attention!!", "Can't read/find face encodings file: {}"],
        "SaveDirList": ["Attention!", "Can't create data file %s"],
        "sel_dir": ["Attention!", "The folder %s has been already scanned. Proceed?",
                    " (with subfolders)"],
        "make_encodings": ["Attention!", "Wanted persons datafile already exists. Replace?",
                           " - added %d face)s) from %d picture(s)..."],
        "get_params": ["Chose face search Math model", "1 - HOG (faster), 2- CNN (more accurate):",
                       "Number of upsamples for face locations", "1 - 100 (less - faster, bigger - smaller faces to be found)",
                       "Number of upsamples for face encodings", "1 - 100 (bigger - slower but more accurate)",
                       "Face encoding model", "1 - small (5 points, faster), 2- large (default, 68 points):",
                       "Additional comment", "Add a comment for all files in folder (Enter if empty)",
                       "Face detection confidence", "Greater is less acccurate  (0<x<1, default and good 0.5):"],
        "facedic_load": ["Attention!!", "Can't read/find face encodings file: {}"],
        "optim": ["Attention", "Small face encodings data files to be consolidated for faster face search. Proceed?", #0, 1
                  "Attention!", "Can't find/read working folder %s", #2, 3
                  "Attention!", "Can't create back-up folder %s", #4, 5
                  "Attention!", "Can't create data base file %s. Move manually file %s back to  %s", #6, 7
                  "Attention!",  "Can't create data base file %s. Move manually file %s back to %s", #8, 9
                  'Information', "Merged %d face encodings data files. Basked up to %s."], #10, 11
        "showdirlist": ["Scanned reference picture fo;ders"],
        "splitvid": ["Choose video for proccessing",'Video files',
                     'Attention!', "Place your file under path with Latin letters only}",
                     'Information', "Saved %d frames with faces from totally %d frames of %s."],
        "showhelp": ["Attention!", "Can't find help file"],
        "showcurwdir": ["Attention!", 'No data for current "wanted" folder.',
                        'Information', 'Current "wanted" folder is %s'],
        "GUI": ["FIND UNKNOWN FACES AMONG KNOWN ONES", #0
                '''1. Choose folder(s) with the pictures (.jpg, .png, .bmp, .gif) of reference (known, identified) individuals to create a database.
                  Scan only once; any new pictures store at new folder(s) and scan them too''',
                  'Scan reference pictures folder', #2
                  'Scan reference pictures folder (with subfolders) ', #3
                  'Video proccessing...', #4
                  '2. Choose a folder with wanted individual(s) pictures', #5
                  'Scan wanted  individual(s) pictures folder', #6
                  'Current "wanted" folder...', #7
                  '3. Push ANALYZE & REPORT to search the faces. Reports will be saved at current app folder as TXT та XLSX (with thumbnails).', #8
                  'ANALYZE & REPORT', #9
                  'List of scanned folders...', #10
                  'Face database optimization', #11
                  'Help...', #12
                  "English"] #13
        },
    "ukr": {
        "dir_load_allimg": ["Оберіть теку з еталонними фото",
                             "Увага!", "Не можу створити робочу теку %s",
                             'Інформація', "Додано %d обличь з %d зображень з теки %s. Зберігаю кодування обличь до файлу..."],
        "dir_load_allimg_sub": ["Оберіть папку з еталонними фото (із вклад. теками)",
                                "Увага!", "Не можу створити робочу теку %s",
                                'Інформація', "Додано %d обличь з %d зображень з теки %s та вкладених тек. Зберігаю кодування обличь до файлу..."],
        "dir_load_wantedimg": ["Оберіть теку з фото невідомих осіб.",
                               "Увага!", "Не можу створити робочу теку %s",
                               "Увага!", "Не можу записати параметри пошуку у файл %s. Звіти зберігатимуться у робочу теку програми",
                               'Інформація', "Додано %d обличь з %d зображень з теки %s. Зберігаю кодування обличь до файлу..."],
        "pic_search": ["Точність розпізнавання обличь", "Менше значення - точніше (0<x<1, непогано 0.45):",
                       "Увага!", "Не можу знайти робочу теку %s",
                       "Увага!", "Не можу знайти робочу теку %s",
                       "Увага!", "Файл даних рошукуваних осіб %s відсутній або недоступний. Проскануйте папку!",
                       "Увага!", "Не можу знайти/прочитати файл даних сканованих папок: {}",
                       " - проведено пошук %d обличь у %d файлах еталонних даних",
                       "Увага!", "Не можу записати файл звіту {}",
                       "Увага!", "Не можу записати файл звіту {}",
                       "Увага!", "Не можу записати файл звіту {}",
                       "Увага!", "Не можу записати файл звіту {}",
                       'Інформація', "Проведено пошук %d обличь у %d файлах еталонних даних. Звіти збережено до файлів %s та %s",
                       "Інформація", "Проведено пошук %d обличь у %d файлах еталонних даних. Збігів не знайдено",
                       "Звіт створено ",
                       " з використанням %s",
                       "Задана точність: ",
                       "Файл зображення розшук. особи",
                       "Фото розшук. особи",
                       "Обличчя розшук. особи",
                       '"Еталонне" обличчя',
                       '"Еталонне" зображення',
                       "Файл еталонного зображення",
                       "Додаткові дані",
                       "Схожість, %",
                       "Ескізу не буде", #34
                       "Дод. коментар:"], #35
        "load": ["Увага!", "Не можу знайти/прочитати файл кодувань обличь: {}"],
        "save": ["Увага!", "Не можу створити файл бази даних %s"],
        "LoadDirList": ["Увага!", "Не можу знайти/прочитати файл кодувань обличь: {}"],
        "SaveDirList": ["Увага!", "Не можу створити файл бази даних %s"],
        "sel_dir": ["Увага!", "Ця тека вже сканувлась %s. Повторити?",
                    " (з вклад. теками)"],
        "make_encodings": ["Увага!", "Файл даних розшукуваних осіб вже існує. Замінити?",
                           " - вже додано %d обличь(чя) з %d зображень...",
                           ],
        "get_params": ["Оберіть матем. модель пошуку обличь", "1 - HOG (швидше), 2- CNN (точніше):",
                       "Проходів пошуку обличь", "1 - 100 (більше - точніше, але довше)",
                       "Проходів при кодуванні обличь", "1 - 100 (більше - точніше, але довше)",
                       "Оберіть модель кодування обличь", "1 - мала (швидше), 2- велика (точніше):",
                       "Додайте коментар", "Коментар буде додано для усіх зображень (якщо немає - Enter)",
                       "Точність виявлення обличь", "Менше значення - точніше (0<x<1, непогано 0.5):"],
        "facedic_load": ["Увага!", "Не можу знайти/прочитати файл кодувань обличь: {}"],
        "optim": ["Увага!", "Дрібні файли даних кодувань обличь буде консолідовано для прискорення пошуку. Продовжити?",
                  "Увага!", "Не можу знайти робочу теку %s",
                  "Увага!", "Не можу створити теку резервних копій %s",
                  "Увага!", "Не можу створити файл бази даних %s. Перенесіть файли з даних з теки %s назад до теки %s",
                  "Увага!", "Не можу створити файл бази даних %s. Перенесіть файли з даних з теки %s назад до теки %s",
                  'Інформація', "Консолідовано %d файлів кодувань обличь. Резервні копії переміщено до %s."],
        "showdirlist": ["Список сканованих папок з еталонними фото"],
        "splitvid": ["Обеpіть файл відео для обробки",'Файли відео',
                     'Увага!', "Розмістить відео у теці, шлях до якої та назва не містять кіриличних символів, та повторіть спробу.",
                     'Інформація', "Збережено %d кадрів з обличчами з %d кадрів відео %s."],
        "showhelp": ["Увага!", "Не можу знайти/прочитати файл довідки"],
        "showcurwdir": ["Увага!", "Дані про поточну пошукову теку відсутны.",
                        'Інформація', "Поточна пошукова тека %s"],
        "GUI": ["ПОШУК ОБЛИЧЬ У ФАЙЛАХ ЗОБРАЖЕНЬ (НЕВІДОМІ СЕРЕД ВІДОМИХ)", #0
                '''1. Оберіть теки (по одній) з еталонними фото (.jpg, .png, .bmp, .gif) для наповнення бази даних.
                  Скануйте тільки один раз, а нові еталонні фото кладіть 
                  у нові теки (із наступним їх скануванням). Для виділення кадрів з обличчями з відeофрагменту натисніть кнопку "Обробка відео..."''',
                  'Сканувати еталонні фото ', #2
                  'Сканувати еталонні фото (із вклад. теками) ', #3
                  'Обробка відео...', #4
                  '2. Оберіть теку з фото невідомих осіб.', #5
                  'Сканувати фото невідомих осіб', #6
                  'Поточна тека пошуку...', #7
                  '3. Натисніть кнопку для початку пошуку. Результати буде збережено в теці з файлами фото невідомих осіб у форматах TXT та XLSX (з ескізами).',
                  'АНАЛІЗ & ЗВІТ', #9
                  'Скановані теки...', #10
                  'Оптимізація бази даних', #11
                  'Довідка...', #12
                  "Українська"] #13
        },
    "rus": {
        "dir_load_allimg": ["Выберите папку с эталонными фото",
                             "Внимание!", "Не могу создать рабочую папку %s",
                             'Информация', "Добавлено %d лиц из %d изображений из папки %s. Сохраняю кодировки лиц в файл..."],
        "dir_load_allimg_sub": ["Выберите папку з эталонными фото (с вложен. папками)",
                                "Внимание!", "Не могу создать рабочую папку %s",
                                'Информация', "Добавлено %d лиц мз %d изображений из папки %s и вложеных папок. Сохраняю кодировки лиц в файл..."],
        "dir_load_wantedimg": ["Выберите папку с фото неизвестных лиц.",
                               "Внимание!", "Не могу создать рабочую папку %s",
                               "Внимание!", "Не могу записать параметры поиска в файл %s. Отчёты будут сохраняться в рабочую папку програмы",
                               'Информация', "Добавлено %d лиц из %d изображений из папки %s. Сохраняю кодировки лиц в файл..."],
        "pic_search": ["Точность распознавания лиц", "Меншее значение - точнее (0<x<1, неплохо 0.45):",
                       "Внимание!", "Не могу найти рабочую папку %s",
                       "Внимание!", "Не могу найти рабочую папку %s",
                       "Внимание!", "Файл даных розыскиваемых лиц %s отсутствует или недоступный. Просканируйте папку!",
                       "Внимание!", "Не могу знайти/прочитати файл даних сканованих папок: {}",
                       " - проведено поиск %d лиц в %d файлах эталонных данниых",
                       "Внимание!", "Не могу записать файл отчёта {}",
                       "Внимание!", "Не могу записать файл отчёта {}",
                       "Внимание!", "Не могу записать файл отчёта {}",
                       "Внимание!", "Не могу записать файл отчёта {}",
                       'Информация', "Проведен поиск %d лиц в %d файлах эталонних данных. Отчёты сохранены в файлы %s и %s",
                       "Информация", "Проведен поиск %d лиц в %d файлах эталонних данных. Совпадений не найдено",
                       "Отчёт создано ",
                       " с использованием %s",
                       "Заданая точность: ",
                       "Файл изображения розыск. лица",
                       "Фото розыск. лица",
                       "Лицо розыск. особы",
                       '"Эталонное" лицо',
                       '"Эталонное" изображение',
                       "Файл эталонного изображения",
                       "Дополнительные данные",
                       "Схожесть, %",
                       "Эскиза не будет", #34
                       "Доп. комментарий:"], #35
        "load": ["Внимание!", "Не могу найти/прочитать файл кодировок лиц: {}"],
        "save": ["Внимание!", "Не могу создать файл базы данных %s"],
        "LoadDirList": ["Внимание!", "Не могу найти/прочитать файл кодировок лиц: {}"],
        "SaveDirList": ["Внимание!", "Не могу создать файл базы данных %s"],
        "sel_dir": ["Внимание!", "Эта папка уже сканировалась %s. Повторить?",
                    " (с вложен. папками)"],
        "make_encodings": ["Внимание!", "Файл даных розыскиваемых лиц уже существует. Заменить?",
                           " - уже добавлено %d лиц из %d изображений...",
                           ],
        "get_params": ["Выберите матем. модель поиска лиц", "1 - HOG (быстрее), 2- CNN (точнее):",
                       "Проходов поиска лиц", "1 - 100 (больше - точнее, но дольше)",
                       "Проходов при кодировании лиц", "1 - 100 (больше - точнее, но дольше)",
                       "Выберите модель кодировки лиц", "1 - мала (швидше), 2- велика (точніше):",
                       "Добавьте комемнтарий", "Комментарий будет добавлен для всех изображений (если нет - Enter)",
                       "Точность выявления лиц", "Меншее значение - точнее (0<x<1, неплохо 0.5):"],
        "facedic_load": ["Внимание!", "Не могу найти/прочитать файл кодировок лиц: {}"],
        "optim": ["Внимание!", "Мелкие файлы даних кодировок лиц будут консолидированы для ускорения поиска. Продолжить?",
                  "Внимание!", "Не могу знайти робочу папку %s",
                  "Внимание!", "Не могу создать папку резервных копий %s",
                  "Внимание!", "Не могу создать файл базы данных %s. Перенесите файлы даних из папки %s назад в папку %s",
                  "Внимание!", "Не могу создать файл базы данных %s. Перенесите файлы даних из папки %s назад в папку %s",
                  'Информация', "Консолидировано %d файлов кодировок лиц. Резервные копии перемнесено в %s."],
        "showdirlist": ["Список сканированных папок с эталонными фото",
                     'Внимание!', "Розместите видео в папке, путь к которой и название не содержат киррилических символов, и повторите попытку.",
                     'Информация', "Сохранено %d кадров с лмцами из %d кадров видео %s."],
        "splitvid": ["Выберите файл для обработки",'Файлы видео',
                     'Внимание!', "Разместите файл видео в папке, путь и название корого записаны латинскими буквами, и повторите попытку.",
                     'Информация', "Сохранено %d кадров с лицами из %d кадров видео %s."],
        "showhelp": ["Внимание!", "Не могу знайти/прочитати файл довідки"],
        "showcurwdir": ["Внимание!", "Даные о текущей поисковой папке отсутствуют",
                        'Информация', "Текущая поисковая папка %s"],
        "GUI": ["ПОИСК ЛИЦ В ФАЙЛАХ ИЗОБРАЖЕНИЙ (НЕИЗВЕСТНЫЕ СРЕДИ ИЗВЕСТНЫХ)", #0
                '''1. Выберите папки (по одной) с эталонными фото (.jpg, .png, .bmp, .gif) для наповнення базы данных.
                  Сканируйту тіоько один раз, а новые эталонные фото размещайте 
                  в новые папки (с последующим их сканированием). Для виделения кадров с лицами в видeофрагменте нажмите кнопку "Обработка видео..."''',
                  'Сканировать эталонные фото', #2
                  'Сканировать эталонные фото (с вложен. папками) ', #3
                  'Обработка видео...', #4
                  '2. Выберите папку с фото неизвестных лиц.', #5
                  'Сканировать фото неизвестных лиц', #6
                  'Текущая поисковая папка...', #7
                  '3. Надмите кнопку для начала поиска. Результаты будут сохранены в текущей поисковой папке в форматах TXT и XLSX (с эскизами).',
                  'АНАЛИЗ & ОТЧЁТ', #9
                  'Сканированные папки...', #10
                  'Оптимизация базы данных', #11
                  'Справка...', #12
                  "Русский"] #13
        },
}
