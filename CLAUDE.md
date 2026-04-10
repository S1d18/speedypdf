# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## О проекте

Конвертер PDF в JPG с поддержкой многопоточной обработки. Проект содержит несколько реализаций конвертации с использованием разных библиотек.

## Команды

```bash
# Установка зависимостей
pip install -r requirements.txt

# Запуск основного конвертера (pdf2image + Poppler)
python main.py

# Запуск альтернативного конвертера (pypdfium2, многопроцессорность)
python pdfium_multiprocess.py

# Запуск бенчмарка PyMuPDF vs pdf2image
python PyMuPDF_vs_pdf2image.py

# Сборка в exe
pyinstaller main.py
```

## Архитектура

### Реализации конвертации

- **main.py** — основной конвертер на базе `pdf2image` (требует Poppler). Многопоточность через `ThreadPoolExecutor`. Поддерживает рекурсивный обход папок и выбор конкретных страниц.

- **pdfium_multiprocess.py** — альтернативный конвертер на базе `pypdfium2`. Многопроцессорность через `ProcessPoolExecutor`. Не требует внешних зависимостей (Poppler).

- **PyMuPDF_vs_pdf2image.py** — бенчмарк для сравнения производительности PyMuPDF и pdf2image.

### Конфигурация (config.py)

| Параметр | Описание |
|----------|----------|
| `POPLER_PATH` | Путь к Poppler (требуется для pdf2image) |
| `PDF_FOLDER` | Папка с исходными PDF |
| `JPG_FOLDER` | Папка для сохранения JPG |
| `MAX_WORKERS` | Количество потоков |
| `FIRST_PAGE` / `LAST_PAGE` | Диапазон страниц (None = все страницы) |

## Зависимости

- **pdf2image** — требует установленного Poppler в системе
- **pypdfium2** — встроенный рендерер, не требует Poppler
- **PyMuPDF (fitz)** — используется в бенчмарке