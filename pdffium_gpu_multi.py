import pypdfium2 as pdfium
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
from tqdm import tqdm
import time

# Параметры
pdf_folder = Path("pdf")  # Папка с PDF-файлами
convert_folder = pdf_folder / "convert"  # Папка для сохранения JPG внутри pdf/convert
dpi = 300  # Устанавливаем DPI для рендеринга
convert_folder.mkdir(exist_ok=True, parents=True)

# Конвертация с помощью PyPDFium2 в JPG
def convert_with_pdfium_to_jpg(pdf_path, output_folder, dpi):
    pdf = pdfium.PdfDocument(pdf_path)
    for page_number in range(len(pdf)):
        page = pdf[page_number]
        image = page.render(scale=dpi / 72)  # Масштабируем DPI
        # Сохраняем изображение в папку внутри convert
        output_image = output_folder / f"{pdf_path.stem}_page_{page_number + 1}.jpg"
        image.to_pil().save(output_image, "JPEG", quality=95)  # Сохраняем в JPG

# Обработка файла
def process_pdf(pdf_path, output_folder, dpi):
    convert_with_pdfium_to_jpg(pdf_path, output_folder, dpi)

# Многопроцессорная обработка PDF с tqdm
def process_pdfs_multiprocess(pdf_files, output_folder, dpi, max_processes=4):
    with ProcessPoolExecutor(max_processes) as executor:
        futures = {executor.submit(process_pdf, pdf, output_folder, dpi): pdf for pdf in pdf_files}
        with tqdm(total=len(pdf_files), desc="Обработка PDF", unit="файл") as pbar:
            for future in as_completed(futures):
                pbar.update(1)

# Основной запуск
if __name__ == "__main__":
    # Получение списка PDF-файлов
    pdf_files = sorted(pdf_folder.glob("*.pdf"))

    # Тестирование многопроцессорной обработки с tqdm
    start_time = time.time()
    process_pdfs_multiprocess(pdf_files, convert_folder, dpi, max_processes=8)
    total_time = time.time() - start_time

    # Результаты
    print(f"\nОбщее время обработки всех PDF (многопроцесс): {total_time:.2f} секунд")
