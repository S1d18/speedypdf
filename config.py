# config.py
import os
# Путь к папке bin в Poppler
POPLER_PATH = r'C:/Program Files/poppler-24.07.0/Library/bin'

# Путь к папке PDF в проекте
PDF_FOLDER = os.path.join('pdf')  # или путь папки r'D:/python/convertpdf-jpg/pdf'

# Путь к папке JPG в проекте
JPG_FOLDER = os.path.join('jpg') # или путь папки r'D:/python/convertpdf-jpg/jpg'

# Количество потоков для многопоточной обработки
MAX_WORKERS = 4  # Вы можете изменить это значение в зависимости от доступных ресурсов

# Конвертировать только первую страницу или все страницы
# Если 'first_page' == 1 и 'last_page' == 1, то конвертируется только первая страница
# Если 'first_page' и 'last_page' равны None, то конвертируются все страницы
FIRST_PAGE = None  # Или None, если нужно конвертировать все страницы
LAST_PAGE = None # Или None, если нужно конвертировать все страницы