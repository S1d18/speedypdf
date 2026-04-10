"""
Benchmark PDF -> JPG conversion.
PyMuPDF vs pdf2image (Poppler) vs pypdfium2
Modes: single-thread, multi-thread (ThreadPool), multi-process (ProcessPool)
"""

import os
import sys
import io

# Force UTF-8 output on Windows
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import time
import json
import shutil
import platform
import statistics
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from datetime import datetime

import fitz  # PyMuPDF
from pdf2image import convert_from_path
import pypdfium2 as pdfium
from PIL import Image
from tqdm import tqdm

# ── Настройки ──────────────────────────────────────────────
PDF_FOLDER = Path("pdf")
OUTPUT_DIR = Path("benchmark_output")
POPPLER_PATH = r"C:/Program Files/poppler-24.07.0/Library/bin"
DPI = 300
MAX_WORKERS = 4  # потоки/процессы для параллельных тестов
# ───────────────────────────────────────────────────────────


# ── Конвертеры (однофайловые) ─────────────────────────────

def convert_pymupdf(pdf_path: Path, output_folder: Path, dpi: int = DPI):
    """PyMuPDF: PDF → JPG"""
    zoom = dpi / 72
    mat = fitz.Matrix(zoom, zoom)
    doc = fitz.open(pdf_path)
    pages = 0
    for i in range(len(doc)):
        pix = doc[i].get_pixmap(matrix=mat)
        pix.save(str(output_folder / f"{pdf_path.stem}_p{i+1}.jpg"))
        pages += 1
    doc.close()
    return pages


def convert_pdf2image(pdf_path: Path, output_folder: Path, dpi: int = DPI):
    """pdf2image (Poppler): PDF → JPG"""
    images = convert_from_path(str(pdf_path), dpi=dpi, poppler_path=POPPLER_PATH)
    for i, img in enumerate(images):
        img.save(str(output_folder / f"{pdf_path.stem}_p{i+1}.jpg"), "JPEG")
    return len(images)


def convert_pdfium(pdf_path: Path, output_folder: Path, dpi: int = DPI):
    """pypdfium2: PDF → JPG"""
    doc = pdfium.PdfDocument(pdf_path)
    pages = 0
    for i in range(len(doc)):
        page = doc[i]
        bitmap = page.render(scale=dpi / 72)
        img = bitmap.to_pil()
        img.save(str(output_folder / f"{pdf_path.stem}_p{i+1}.jpg"), "JPEG", quality=95)
        pages += 1
    return pages


# Обёртки для ProcessPoolExecutor (top-level для pickle)
def _worker_pymupdf(args):
    pdf_path, output_folder, dpi = args
    return convert_pymupdf(Path(pdf_path), Path(output_folder), dpi)

def _worker_pdf2image(args):
    pdf_path, output_folder, dpi = args
    return convert_pdf2image(Path(pdf_path), Path(output_folder), dpi)

def _worker_pdfium(args):
    pdf_path, output_folder, dpi = args
    return convert_pdfium(Path(pdf_path), Path(output_folder), dpi)


CONVERTERS = {
    "PyMuPDF":    (convert_pymupdf,   _worker_pymupdf),
    "pdf2image":  (convert_pdf2image, _worker_pdf2image),
    "pypdfium2":  (convert_pdfium,    _worker_pdfium),
}


# ── Запуск бенчмарков ─────────────────────────────────────

def run_single(name, converter, pdf_files, output_folder, dpi):
    """Однопоточный режим."""
    times = []
    total_pages = 0
    for pdf in tqdm(pdf_files, desc=f"  {name} [single]", unit="pdf"):
        try:
            t0 = time.perf_counter()
            pages = converter(pdf, output_folder, dpi)
            times.append(time.perf_counter() - t0)
            total_pages += pages
        except Exception as e:
            print(f"    ОШИБКА {pdf.name}: {e}")
            times.append(None)
    return times, total_pages


def run_threaded(name, converter, pdf_files, output_folder, dpi, workers):
    """Многопоточный режим (ThreadPoolExecutor)."""
    total_pages = 0
    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(converter, pdf, output_folder, dpi): pdf for pdf in pdf_files}
        for f in tqdm(as_completed(futures), total=len(futures), desc=f"  {name} [thread×{workers}]", unit="pdf"):
            try:
                total_pages += f.result()
            except Exception as e:
                print(f"    ОШИБКА: {e}")
    wall_time = time.perf_counter() - t0
    return wall_time, total_pages


def run_multiprocess(name, worker_fn, pdf_files, output_folder, dpi, workers):
    """Многопроцессорный режим (ProcessPoolExecutor)."""
    total_pages = 0
    args_list = [(str(pdf), str(output_folder), dpi) for pdf in pdf_files]
    t0 = time.perf_counter()
    with ProcessPoolExecutor(max_workers=workers) as ex:
        futures = {ex.submit(worker_fn, a): a for a in args_list}
        for f in tqdm(as_completed(futures), total=len(futures), desc=f"  {name} [proc×{workers}]", unit="pdf"):
            try:
                total_pages += f.result()
            except Exception as e:
                print(f"    ОШИБКА: {e}")
    wall_time = time.perf_counter() - t0
    return wall_time, total_pages


# ── Главная ───────────────────────────────────────────────

def get_total_pdf_pages(pdf_files):
    """Подсчитать общее кол-во страниц через PyMuPDF (быстро)."""
    total = 0
    for pdf in pdf_files:
        try:
            doc = fitz.open(pdf)
            total += len(doc)
            doc.close()
        except:
            pass
    return total


def clean_output(folder: Path):
    if folder.exists():
        shutil.rmtree(folder)
    folder.mkdir(parents=True)


def main():
    pdf_files = sorted(PDF_FOLDER.glob("*.pdf"))
    n_files = len(pdf_files)

    if not pdf_files:
        print("Нет PDF файлов в папке", PDF_FOLDER)
        sys.exit(1)

    total_pages = get_total_pdf_pages(pdf_files)
    print(f"\n{'='*65}")
    print(f"  BENCHMARK PDF->JPG  |  {n_files} files  |  {total_pages} pages  |  {DPI} DPI")
    print(f"  Workers: {MAX_WORKERS}  |  {datetime.now():%Y-%m-%d %H:%M}")
    print(f"  OS: {platform.system()} {platform.release()}  |  CPU: {os.cpu_count()} cores")
    print(f"{'='*65}\n")

    results = {}

    for lib_name, (converter, worker_fn) in CONVERTERS.items():
        print(f"> {lib_name}")
        lib_results = {}

        # 1) Однопоточный
        out = OUTPUT_DIR / f"{lib_name}_single"
        clean_output(out)
        times, pages = run_single(lib_name, converter, pdf_files, out, DPI)
        valid = [t for t in times if t is not None]
        errors = sum(1 for t in times if t is None)
        lib_results["single"] = {
            "total_sec": round(sum(valid), 3),
            "mean_sec": round(statistics.mean(valid), 4) if valid else 0,
            "median_sec": round(statistics.median(valid), 4) if valid else 0,
            "min_sec": round(min(valid), 4) if valid else 0,
            "max_sec": round(max(valid), 4) if valid else 0,
            "pages": pages,
            "errors": errors,
            "pages_per_sec": round(pages / sum(valid), 2) if valid and sum(valid) > 0 else 0,
        }
        print(f"    Итого: {sum(valid):.2f}s  |  {pages} стр  |  {lib_results['single']['pages_per_sec']} стр/с  |  ошибок: {errors}")

        # 2) Многопоточный
        out = OUTPUT_DIR / f"{lib_name}_threaded"
        clean_output(out)
        wall, pages = run_threaded(lib_name, converter, pdf_files, out, DPI, MAX_WORKERS)
        lib_results["threaded"] = {
            "total_sec": round(wall, 3),
            "workers": MAX_WORKERS,
            "pages": pages,
            "pages_per_sec": round(pages / wall, 2) if wall > 0 else 0,
        }
        print(f"    Итого: {wall:.2f}s  |  {pages} стр  |  {lib_results['threaded']['pages_per_sec']} стр/с")

        # 3) Многопроцессорный
        out = OUTPUT_DIR / f"{lib_name}_multiproc"
        clean_output(out)
        wall, pages = run_multiprocess(lib_name, worker_fn, pdf_files, out, DPI, MAX_WORKERS)
        lib_results["multiprocess"] = {
            "total_sec": round(wall, 3),
            "workers": MAX_WORKERS,
            "pages": pages,
            "pages_per_sec": round(pages / wall, 2) if wall > 0 else 0,
        }
        print(f"    Итого: {wall:.2f}s  |  {pages} стр  |  {lib_results['multiprocess']['pages_per_sec']} стр/с")
        print()

        results[lib_name] = lib_results

    # ── Сводная таблица ──
    print(f"\n{'='*65}")
    print(f"  СВОДНАЯ ТАБЛИЦА (время в секундах)")
    print(f"{'='*65}")
    header = f"{'Библиотека':<14} {'Single':>9} {'Thread×'+str(MAX_WORKERS):>10} {'Proc×'+str(MAX_WORKERS):>10} {'Best стр/с':>11}"
    print(header)
    print("-" * len(header))

    for lib_name, data in results.items():
        s = data["single"]["total_sec"]
        t = data["threaded"]["total_sec"]
        m = data["multiprocess"]["total_sec"]
        best_pps = max(
            data["single"]["pages_per_sec"],
            data["threaded"]["pages_per_sec"],
            data["multiprocess"]["pages_per_sec"],
        )
        print(f"{lib_name:<14} {s:>9.2f} {t:>10.2f} {m:>10.2f} {best_pps:>11.1f}")

    print()

    # ── Сохраняем JSON ──
    report = {
        "date": datetime.now().isoformat(),
        "system": {
            "os": f"{platform.system()} {platform.release()}",
            "cpu_cores": os.cpu_count(),
            "python": platform.python_version(),
        },
        "params": {
            "dpi": DPI,
            "workers": MAX_WORKERS,
            "pdf_files": n_files,
            "total_pages": total_pages,
        },
        "libraries": {
            "PyMuPDF": fitz.VersionBind,
            "pdf2image": "1.17.0",
            "pypdfium2": str(pdfium.version),
        },
        "results": results,
    }

    report_path = Path("benchmark_results.json")
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print(f"Результаты сохранены в {report_path}")

    # ── Удаляем временные изображения ──
    if OUTPUT_DIR.exists():
        shutil.rmtree(OUTPUT_DIR)
        print("Временные файлы удалены.")


if __name__ == "__main__":
    main()
