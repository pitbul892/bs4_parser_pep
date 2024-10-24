import argparse
import logging
from logging.handlers import RotatingFileHandler

from constants import BASE_DIR, FILE_VIEW, LOGS_FILE, ONE_MB, TABLE_VIEW

LOG_FORMAT = '"%(asctime)s - [%(levelname)s] - %(message)s"'
DT_FORMAT = '%d.%m.%Y %H:%M:%S'


def configure_argument_parser(available_modes):
    parser = argparse.ArgumentParser(description='Парсер документации Python')
    parser.add_argument(
        'mode',
        choices=available_modes,
        help='Режимы работы парсера'
    )
    parser.add_argument(
        '-c',
        '--clear-cache',
        action='store_true',
        help='Очистка кеша'
    )
    parser.add_argument(
        '-o',
        '--output',
        choices=(TABLE_VIEW, FILE_VIEW),
        help='Дополнительные способы вывода данных'
    )

    return parser


def configure_logging():
    log_dir = BASE_DIR / LOGS_FILE
    log_dir.mkdir(exist_ok=True)
    log_file = log_dir / 'parser.log'
    rotating_handler = RotatingFileHandler(
        log_file, maxBytes=ONE_MB, backupCount=5, encoding='utf-8',
    )
    logging.basicConfig(
        encoding='utf-8',
        datefmt=DT_FORMAT,
        format=LOG_FORMAT,
        level=logging.INFO,
        handlers=(rotating_handler, logging.StreamHandler())
    )
