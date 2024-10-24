import csv
import datetime as dt
import logging

from prettytable import PrettyTable

from constants import (BASE_DIR, DATETIME_FORMAT, FILE_VIEW, RESULTS_FILE,
                       TABLE_VIEW)


def control_output(results, cli_args):
    output = cli_args.output
    if output == TABLE_VIEW:
        pretty_output(results)
    elif output == FILE_VIEW:
        file_output(results, cli_args)
    else:
        default_output(results)


def default_output(results):
    for row in results:
        print(*row)


def pretty_output(results):
    table = PrettyTable()
    table.field_names = results[0]
    table.align = 'l'
    table.add_rows(results[1:])
    print(table)


def file_output(results, cli_args):
    results_dir = BASE_DIR / RESULTS_FILE
    results_dir.mkdir(exist_ok=True)
    if cli_args == 'pep':
        parser_mode = cli_args
    else:
        parser_mode = cli_args.mode
    now = dt.datetime.now()
    now_formatted = now.strftime(DATETIME_FORMAT)
    file_name = f'{parser_mode}_{now_formatted}.csv'
    file_path = results_dir / file_name
    with open(file_path, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, dialect='unix', quoting=csv.QUOTE_MINIMAL)
        writer.writerows(results)
    logging.info(f'Файл с результатами был сохранён: {file_path}')
