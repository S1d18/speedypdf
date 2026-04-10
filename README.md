# SpeedyPDF

![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Конвертер PDF в JPG на Python. Три движка на выбор, параллельная обработка, встроенный бенчмарк.

---

## Быстрый старт

```bash
git clone https://github.com/S1d18/speedypdf.git
cd speedypdf
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux / macOS
pip install -r requirements.txt
```

Положите PDF-файлы в папку `pdf/` и запустите:

```bash
python main.py                  # pdf2image (требует Poppler)
python pdfium_multiprocess.py   # pypdfium2 (ничего не требует)
```

---

## Движки конвертации

В проекте реализовано три движка. Каждый можно использовать отдельно:

| Движок | Файл | Внешние зависимости | Параллелизм |
|--------|------|---------------------|-------------|
| **pdf2image** | `main.py` | Poppler | ThreadPoolExecutor |
| **pypdfium2** | `pdfium_multiprocess.py` | -- | ProcessPoolExecutor |
| **PyMuPDF** | только в бенчмарке | -- | -- |

> **pypdfium2** и **PyMuPDF** содержат встроенный рендерер и не требуют установки Poppler.

---

## Конвертеры

### main.py -- pdf2image + Poppler

Основной конвертер. Рекурсивно обходит вложенные папки, сохраняет структуру директорий.

```bash
python main.py
```

**Требует** установленный [Poppler](https://github.com/oschwartz10612/poppler-windows/releases):

| ОС | Установка |
|----|-----------|
| Windows | Скачать, распаковать, прописать путь в `config.py` |
| Linux | `sudo apt install poppler-utils` |
| macOS | `brew install poppler` |

**Настройки** -- файл `config.py`:

```python
POPLER_PATH  = r'C:/Program Files/poppler-24.07.0/Library/bin'
PDF_FOLDER   = 'pdf'       # откуда читать
JPG_FOLDER   = 'jpg'       # куда сохранять
MAX_WORKERS  = 4            # количество потоков
FIRST_PAGE   = None         # None = все страницы, 1 = только первая
LAST_PAGE    = None         # None = все страницы, 1 = только первая
```

---

### pdfium_multiprocess.py -- pypdfium2

Альтернативный конвертер. Не требует Poppler -- использует встроенный движок PDFium (тот же, что в Google Chrome).

```bash
python pdfium_multiprocess.py
```

**Настройки** -- в начале файла:

```python
pdf_folder     = Path("pdf")             # откуда читать
convert_folder = pdf_folder / "convert"   # куда сохранять
dpi            = 300                      # разрешение
max_processes  = 8                        # количество процессов
```

---

## Бенчмарк

### benchmark.py -- сравнение всех трёх движков

Тестирует каждый движок в трёх режимах: однопоток, многопоток, многопроцесс (всего 9 тестов).

```bash
pip install PyMuPDF    # если ещё не установлен
python benchmark.py
```

**Настройки** -- в начале файла:

```python
PDF_FOLDER   = Path("pdf")
DPI          = 300
MAX_WORKERS  = 4
POPPLER_PATH = r"C:/Program Files/poppler-24.07.0/Library/bin"
```

**Что делает:**
1. Прогоняет каждый движок в 3 режимах по всем PDF в папке
2. Выводит сводную таблицу в консоль
3. Сохраняет результаты в `benchmark_results.json`
4. Удаляет временные изображения

---

### PyMuPDF_vs_pdf2image.py -- старый бенчмарк

Сравнивает только PyMuPDF и pdf2image в однопоточном режиме, строит график `benchmark_result.png`.

```bash
python PyMuPDF_vs_pdf2image.py
```

---

## Результаты бенчмарка

> **Система:** Windows 11 Pro, 12 ядер CPU, Python 3.11
> **Данные:** 100 PDF-файлов, 397 страниц, 300 DPI, 4 воркера

### Время (секунды)

```
                 1 поток     4 потока     4 процесса
PyMuPDF          222.55      229.88       103.46
pdf2image        218.12      111.93       104.33
pypdfium2         53.09       21.75        22.49
                                 ▲
                            лучший результат
```

### Скорость (страниц в секунду)

```
                 1 поток     4 потока     4 процесса
PyMuPDF            1.78        1.73         3.84
pdf2image          1.82        3.55         3.81
pypdfium2          7.48       18.25        17.65
                                 ▲
                          18.25 стр/с
```

### Главное

- **pypdfium2 быстрее в 5-10 раз** по сравнению с PyMuPDF и pdf2image
- **Лучшая комбинация:** `pypdfium2 + ThreadPoolExecutor(4)` -- 21.75 сек на 397 страниц
- **PyMuPDF** не ускоряется потоками (Python GIL), но ускоряется процессами в 2 раза
- **pdf2image** ускоряется и потоками, и процессами примерно в 2 раза (Poppler на C, отпускает GIL)
- Многопроцессорность для pypdfium2 не даёт выигрыша -- накладные расходы на IPC съедают разницу

### Что выбрать?

| Задача | Движок |
|--------|--------|
| Максимальная скорость конвертации | `pypdfium2` + потоки |
| Poppler уже установлен в системе | `pdf2image` + процессы |
| Нужен текст, аннотации, метаданные из PDF | `PyMuPDF` |
| Деплой без внешних зависимостей | `pypdfium2` |

---

## Структура проекта

```
speedypdf/
├── config.py                 # настройки для main.py
├── main.py                   # конвертер: pdf2image + Poppler
├── pdfium_multiprocess.py    # конвертер: pypdfium2
├── benchmark.py              # бенчмарк всех движков
├── PyMuPDF_vs_pdf2image.py   # старый бенчмарк
├── benchmark_results.json    # результаты бенчмарка
├── requirements.txt
├── setup.py
└── pdf/                      # сюда кладёте PDF-файлы
```

## Лицензия

MIT
