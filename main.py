import os
from pdf2image import convert_from_path
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from config import POPLER_PATH, PDF_FOLDER, JPG_FOLDER, MAX_WORKERS, FIRST_PAGE, LAST_PAGE


# Функция для конвертации страниц PDF в JPG
def convert_pdf_to_jpg(pdf_path, jpg_path, first_page, last_page):
    try:
        # Конвертируем указанные страницы PDF в изображения
        images = convert_from_path(pdf_path, dpi=300, poppler_path=POPLER_PATH, first_page=first_page,
                                   last_page=last_page)

        # Формируем имя файла в зависимости от количества страниц
        base_name = os.path.splitext(os.path.basename(pdf_path))[0]

        if first_page is not None and last_page is not None:  # Если указаны конкретные страницы
            jpg_file_name = f'{base_name}.jpg'
            jpg_file_path = os.path.join(os.path.dirname(jpg_path), jpg_file_name)
            # Сохраняем одну страницу
            images[0].save(jpg_file_path, 'JPEG')
        else:  # Если конвертируем все страницы
            for i, image in enumerate(images):
                jpg_file_name = f'{base_name}_page_{i + 1}.jpg'
                jpg_file_path = os.path.join(os.path.dirname(jpg_path), jpg_file_name)
                image.save(jpg_file_path, 'JPEG')

        return jpg_path
    except Exception as e:
        print(f"Ошибка при конвертации {pdf_path}: {e}")
        return None


# Функция для обработки всех PDF файлов в папке и ее подпапках
def process_pdfs_in_directory(pdf_directory, jpg_directory):
    # Список для хранения путей к задачам
    futures = []

    # Проходим по всем папкам и файлам в pdf_directory
    for root, _, files in os.walk(pdf_directory):
        # Определяем соответствующую папку в jpg_directory
        relative_path = os.path.relpath(root, pdf_directory)
        target_folder = os.path.join(jpg_directory, relative_path)

        # Создаем папку в jpg_directory, если она не существует
        os.makedirs(target_folder, exist_ok=True)

        for file in files:
            if file.lower().endswith('.pdf'):
                # Полный путь к PDF файлу
                pdf_path = os.path.join(root, file)

                # Полное имя JPG файла (имя папки для сохранения)
                jpg_path = os.path.join(target_folder, os.path.splitext(file)[0] + '.jpg')

                # Добавляем задачу в пул потоков
                futures.append((pdf_path, jpg_path))

    # Используем ThreadPoolExecutor для многопоточной обработки
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        # Инициализируем прогресс-бар
        with tqdm(total=len(futures), desc='Конвертация PDF в JPG', unit='файл', ncols=100) as pbar:
            # Создаем задачи для выполнения
            future_to_path = {
                executor.submit(convert_pdf_to_jpg, pdf_path, jpg_path, FIRST_PAGE, LAST_PAGE): (pdf_path, jpg_path) for
                pdf_path, jpg_path in futures}

            # Обрабатываем завершенные задачи
            for future in as_completed(future_to_path):
                pdf_path, jpg_path = future_to_path[future]
                try:
                    result = future.result()  # Получаем результат выполнения (или исключение)
                    if result:
                        pbar.set_postfix_str(f'Сохранено: {result}')
                except Exception as e:
                    print(f"Ошибка при выполнении задачи для {pdf_path}: {e}")
                pbar.update(1)  # Обновляем прогресс-бар


# Основная функция
def main():
    process_pdfs_in_directory(PDF_FOLDER, JPG_FOLDER)


# Запуск основного кода
if __name__ == "__main__":
    main()
