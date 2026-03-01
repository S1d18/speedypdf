import os
import time
from pathlib import Path
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import matplotlib.pyplot as plt

# Параметры
pdf_folder = Path("pdf")  # Папка с PDF-файлами
output_folder_pymupdf = Path("output_pymupdf")
output_folder_pdf2image = Path("output_pdf2image")
dpi = 300  # Устанавливаем одинаковое разрешение (300 DPI)

# Создание выходных папок
output_folder_pymupdf.mkdir(exist_ok=True)
output_folder_pdf2image.mkdir(exist_ok=True)

# Функция для конвертации с помощью PyMuPDF (с фиксированным DPI)
def convert_with_pymupdf(pdf_path, output_folder, dpi):
    images = []
    zoom = dpi / 72  # PyMuPDF работает в базовом разрешении 72 DPI
    mat = fitz.Matrix(zoom, zoom)
    doc = fitz.open(pdf_path)
    for page_num in range(len(doc)):
        pix = doc[page_num].get_pixmap(matrix=mat)
        output_image = output_folder / f"{pdf_path.stem}_page_{page_num + 1}.jpg"
        pix.save(output_image)
        images.append(output_image)
    return images

# Функция для конвертации с помощью pdf2image (с фиксированным DPI)
def convert_with_pdf2image(pdf_path, output_folder, dpi):
    images = convert_from_path(pdf_path, dpi=dpi)
    output_images = []
    for i, img in enumerate(images):
        output_image = output_folder / f"{pdf_path.stem}_page_{i + 1}.jpg"
        img.save(output_image, "JPEG")
        output_images.append(output_image)
    return output_images

# Функция для замера времени
def benchmark_conversion(pdf_files, converter_function, output_folder, dpi):
    times = []
    for pdf in pdf_files:
        try:
            start_time = time.time()
            converter_function(pdf, output_folder, dpi)
            end_time = time.time()
            times.append(end_time - start_time)
        except Exception as e:
            print(f"Ошибка при обработке {pdf.name}: {e}")
            times.append(0)
    return times

# Получение списка PDF-файлов
pdf_files = sorted(pdf_folder.glob("*.pdf"))
if not pdf_files:
    print("PDF-файлы не найдены в папке.")
    exit()

# Тестирование PyMuPDF
print("Тестирование PyMuPDF...")
pymupdf_times = benchmark_conversion(pdf_files, convert_with_pymupdf, output_folder_pymupdf, dpi)

# Тестирование pdf2image
print("Тестирование pdf2image...")
pdf2image_times = benchmark_conversion(pdf_files, convert_with_pdf2image, output_folder_pdf2image, dpi)

# Построение графиков
plt.figure(figsize=(10, 6))
plt.plot(range(len(pymupdf_times)), pymupdf_times, label="PyMuPDF", marker='o')
plt.plot(range(len(pdf2image_times)), pdf2image_times, label="pdf2image", marker='x')
plt.title(f"Сравнение производительности PyMuPDF и pdf2image при {dpi} DPI")
plt.xlabel("Номер PDF")
plt.ylabel("Время обработки (секунды)")
plt.legend()
plt.grid(True)
plt.savefig("benchmark_result.png", dpi=150)
print("График сохранён в benchmark_result.png")

# Сравнение общего времени
total_pymupdf_time = sum(pymupdf_times)
total_pdf2image_time = sum(pdf2image_times)
print(f"Общее время PyMuPDF: {total_pymupdf_time:.2f} секунд")
print(f"Общее время pdf2image: {total_pdf2image_time:.2f} секунд")
print(f"Общее время обработки: {total_pymupdf_time + total_pdf2image_time:.2f} секунд")
