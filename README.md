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

> Для основного конвертера необходим [Poppler](https://poppler.freedesktop.org/). Путь настраивается в `config.py`.

## Использование

### Основной конвертер (pdf2image)
```bash
python main.py
```

Настройки в `config.py`:

| Параметр | Описание | По умолчанию |
|----------|----------|--------------|
| `POPLER_PATH` | Путь к Poppler | `C:/Program Files/poppler-.../bin` |
| `PDF_FOLDER` | Папка с PDF | `pdf` |
| `JPG_FOLDER` | Папка для JPG | `jpg` |
| `MAX_WORKERS` | Количество потоков | `4` |
| `FIRST_PAGE` | Первая страница | `None` (все) |
| `LAST_PAGE` | Последняя страница | `None` (все) |

### Альтернативный конвертер (pypdfium2)
```bash
python pdffium_gpu_multi.py
```
Не требует Poppler. Использует многопроцессорность.

### Бенчмарк
```bash
python PyMuPDF_vs_pdf2image.py
```
Сравнивает PyMuPDF и pdf2image, строит график.

## Лицензия

MIT
