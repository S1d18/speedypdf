from setuptools import setup, find_packages

setup(
    name='pdf-to-jpg-converter',  # Имя вашего пакета
    version='0.1',  # Версия вашего пакета
    description='Конвертер PDF в JPG с использованием многопоточности',  # Краткое описание
    author='S1d18',  # Ваше имя
    url='https://github.com/ваш_пользователь_или_организация/ваш_репозиторий',  # URL репозитория
    packages=find_packages(),  # Поиск всех пакетов в проекте
    install_requires=[
        'pdf2image',  # Библиотека для конвертации PDF в изображения
        'tqdm',       # Библиотека для отображения прогресс-бара
        'Pillow',     # Библиотека для обработки изображений
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',  # Минимальная версия Python
)
