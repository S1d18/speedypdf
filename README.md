# SpeedyPDF
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Быстрый конвертер PDF в JPG с поддержкой многопоточности и многопроцессорности.

## Возможности

- Пакетная конвертация всех PDF-файлов в папке
- Рекурсивный обход вложенных директорий с сохранением структуры
- Многопоточность через `ThreadPoolExecutor`
- Альтернативная реализация через `ProcessPoolExecutor` (pypdfium2)
- Выбор диапазона страниц
- Настраиваемое качество (DPI, по умолчанию 300)
- Несколько бэкендов: pdf2image + Poppler, pypdfium2, PyMuPDF
- Встроенный бенчмарк для сравнения производительности
- Прогресс-бар (tqdm)
- Сборка в exe через PyInstaller

## Технологии

- Python 3.9+
- pdf2image + Poppler
- pypdfium2
- PyMuPDF (fitz)
- Pillow
- tqdm
- matplotlib (бенчмарки)

## Установка

```bash
git clone https://github.com/<username>/speedypdf.git
cd speedypdf
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
```

### Дополнительные зависимости

**Poppler** (нужен только для `pdf2image`):
- Windows: скачать с [poppler-windows](https://github.com/oschwartz10612/poppler-windows/releases), распаковать, прописать путь в `config.py`
- Linux: `sudo apt install poppler-utils`
- macOS: `brew install poppler`

**PyMuPDF** (нужен для бенчмарка):
```bash
pip install PyMuPDF
```

> `pypdfium2` и `PyMuPDF` не требуют Poppler -- у них свой встроенный рендерер.

## Использование

### 1. Основной конвертер -- pdf2image + Poppler

```bash
python main.py
```

Читает PDF из папки `pdf/`, сохраняет JPG в `jpg/`. Рекурсивно обходит вложенные папки, сохраняя структуру директорий. Использует многопоточность (`ThreadPoolExecutor`).

**Требует:** установленный Poppler.

Настройки в `config.py`:

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `POPLER_PATH` | Путь к папке `bin` Poppler | `C:/Program Files/poppler-24.07.0/Library/bin` |
| `PDF_FOLDER` | Папка с исходными PDF | `pdf` |
| `JPG_FOLDER` | Папка для сохранения JPG | `jpg` |
| `MAX_WORKERS` | Количество потоков | `4` |
| `FIRST_PAGE` | Первая страница для конвертации | `None` (все страницы) |
| `LAST_PAGE` | Последняя страница для конвертации | `None` (все страницы) |

Примеры настройки страниц:
```python
# Конвертировать только первую страницу каждого PDF
FIRST_PAGE = 1
LAST_PAGE = 1

# Конвертировать все страницы
FIRST_PAGE = None
LAST_PAGE = None
```

### 2. Альтернативный конвертер -- pypdfium2

```bash
python pdfium_multiprocess.py
```

Читает PDF из папки `pdf/`, сохраняет JPG в `pdf/convert/`. Использует многопроцессорность (`ProcessPoolExecutor`).

**Не требует Poppler** -- pypdfium2 содержит встроенный рендерер PDFium (тот же движок, что в Chrome).

Параметры задаются прямо в файле:

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `pdf_folder` | Папка с PDF | `pdf` |
| `convert_folder` | Папка для JPG | `pdf/convert` |
| `dpi` | Разрешение рендеринга | `300` |
| `max_processes` | Количество процессов | `8` |

### 3. Бенчмарк -- сравнение всех библиотек

```bash
python benchmark.py
```

Тестирует **3 библиотеки** в **3 режимах** (9 тестов):

| Библиотека | Single-thread | Multi-thread | Multi-process |
|------------|:---:|:---:|:---:|
| PyMuPDF | + | + | + |
| pdf2image | + | + | + |
| pypdfium2 | + | + | + |

Параметры задаются в начале файла `benchmark.py`:

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `PDF_FOLDER` | Папка с тестовыми PDF | `pdf` |
| `DPI` | Разрешение рендеринга | `300` |
| `MAX_WORKERS` | Количество потоков/процессов | `4` |
| `POPPLER_PATH` | Путь к Poppler (для pdf2image) | `C:/Program Files/poppler-24.07.0/Library/bin` |

По завершении:
- Выводит сводную таблицу в консоль
- Сохраняет детальные результаты в `benchmark_results.json`
- Автоматически удаляет временные изображения

### 4. Старый бенчмарк -- PyMuPDF vs pdf2image

```bash
python PyMuPDF_vs_pdf2image.py
```

Сравнивает только PyMuPDF и pdf2image в однопоточном режиме, строит график `benchmark_result.png`.

## Результаты бенчмарка

**Система:** Windows 11 Pro | 12 ядер CPU | Python 3.11
**Тест:** 100 PDF | 397 страниц | 300 DPI | 4 воркера

### Время обработки (секунды, меньше = лучше)

| Библиотека | Single | Thread x4 | Process x4 |
|------------|-------:|----------:|-----------:|
| PyMuPDF 1.27 | 222.55 | 229.88 | 103.46 |
| pdf2image 1.17 | 218.12 | 111.93 | 104.33 |
| **pypdfium2 5.7** | **53.09** | **21.75** | **22.49** |

### Скорость (страниц/сек, больше = лучше)

| Библиотека | Single | Thread x4 | Process x4 |
|------------|-------:|----------:|-----------:|
| PyMuPDF | 1.78 | 1.73 | 3.84 |
| pdf2image | 1.82 | 3.55 | 3.81 |
| **pypdfium2** | **7.48** | **18.25** | **17.65** |

### Выводы

1. **pypdfium2 -- самый быстрый.** В однопотоке быстрее в 4 раза, с потоками -- в 5-10 раз.

2. **Лучшая комбинация: `pypdfium2 + ThreadPoolExecutor(4)` -- 18.25 стр/с.**
   Многопроцессорность не дает выигрыша из-за накладных расходов на IPC.

3. **PyMuPDF** плохо параллелится через потоки (GIL не отпускается), но multiprocess дает ускорение в 2 раза.

4. **pdf2image** хорошо параллелится обоими способами (Poppler написан на C и отпускает GIL). Потоки и процессы дают примерно одинаковое ускорение ~2x.

5. **pypdfium2 не требует Poppler** -- проще устанавливать и деплоить. Работает на встроенном движке PDFium (тот же, что в Google Chrome).

### Какую библиотеку выбрать?

| Сценарий | Рекомендация |
|----------|-------------|
| Максимальная скорость | pypdfium2 + ThreadPoolExecutor |
| Poppler уже установлен | pdf2image + ProcessPoolExecutor |
| Нужна работа с содержимым PDF (текст, аннотации) | PyMuPDF |
| Простой деплой без внешних зависимостей | pypdfium2 |

## Структура проекта

```
speedypdf/
  config.py                  # Настройки основного конвертера
  main.py                    # Конвертер на pdf2image + Poppler
  pdfium_multiprocess.py     # Конвертер на pypdfium2
  benchmark.py               # Бенчмарк всех 3 библиотек
  PyMuPDF_vs_pdf2image.py    # Старый бенчмарк (PyMuPDF vs pdf2image)
  benchmark_results.json     # Результаты последнего бенчмарка
  requirements.txt           # Зависимости
  setup.py                   # Сборка
  pdf/                       # Папка с исходными PDF
```

## Лицензия

MIT
