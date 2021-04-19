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
                       "Additional comment", "Add a comment for all files in folder (Enter if empty)"],
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
                        'Інформація', 'Current "wanted" folder is %s'],
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
                  'Help...'] #12
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
                       "Додайте коментар", "Коментар буде додано для усіх зображень (якщо немає - Enter)"],
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
        "GUI": ["ПОШУК ОБЛИЧЬ У ФАЙЛАХ ЗОБРАЖЕНЬ (НЕВІДОМІ СЕРЕД ВІДОМИХ))", #0
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
                  'Довідка...'] #12
    }
}