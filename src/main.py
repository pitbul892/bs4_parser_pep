import logging
import re
from urllib.parse import urljoin

import requests_cache
from bs4 import BeautifulSoup
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import (BASE_DIR, DOWNLOADS_FILE, EXPECTED_STATUS, MAIN_DOC_URL,
                       PEP_URL)
from exceptions import PageLoadException, ParserFindTagException
from outputs import control_output, file_output
from utils import find_tag, get_soup


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    soup = get_soup(session, whats_new_url)
    div_with_ul = find_tag(soup, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li', attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = section.find('a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        soup = get_soup(session, version_link)
        h1 = find_tag(soup, 'h1')
        dl = find_tag(soup, 'dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append((version_link, h1.text, dl_text))
    return results


def latest_versions(session):
    soup = get_soup(session, MAIN_DOC_URL)
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise ParserFindTagException('Ничего не нашлось')
    results = [('Ссылка на документацию', 'Версия', 'Статус')]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        text_match = re.search(pattern, a_tag.text)
        if text_match is not None:
            version, status = text_match.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (a_tag['href'], version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    soup = get_soup(session, downloads_url)
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag, 'a', {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / DOWNLOADS_FILE
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


def pep(session):
    soup = get_soup(session, PEP_URL)
    section_tag = find_tag(soup, 'section', attrs={'id': 'index-by-category'})
    table_tags = section_tag.find_all('tbody')
    results = [('Status', 'Count')]
    first_results = {}
    for table_tag in table_tags:
        row_tags = table_tag.find_all('tr')
        for row_tag in row_tags:
            status_tag = find_tag(row_tag, 'td')
            status_table = status_tag.text[1:]
            link_tag = find_tag(
                row_tag, 'a', attrs={'href': re.compile(r'pep.+')}
            )
            link = link_tag['href']
            detail_pep_url = urljoin(PEP_URL, link)
            pep_response = session.get(detail_pep_url)
            pep_response.encoding = 'utf-8'
            pep_soup = BeautifulSoup(pep_response.text, features='lxml')
            dl_tag = find_tag(pep_soup, 'dl')
            dt_tags = dl_tag.find_all('dt')
            for dt_tag in dt_tags:
                if 'Status' in dt_tag.text:
                    status_pep = dt_tag.find_next_sibling('dd').text
                    if status_pep in first_results:
                        first_results[status_pep] += 1
                    else:
                        first_results[status_pep] = 1
                    if status_pep not in EXPECTED_STATUS[status_table]:
                        logging.info('Несовпадающие статусы:\n'
                                     f'{detail_pep_url}\n'
                                     f'Статус в карточке: {status_pep}\n'
                                     'Ожидаемые статусы:'
                                     f'{EXPECTED_STATUS[status_table]}'
                                     )
    for status, count in first_results.items():
        results.append((status, count))
    results.append(('Total', sum(first_results.values())))
    file_output(results, 'pep')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep,
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    try:
        session = requests_cache.CachedSession()
        if args.clear_cache:
            session.cache.clear()

        parser_mode = args.mode
        results = MODE_TO_FUNCTION[parser_mode](session)
        if results is not None:
            control_output(results, args)
    except (PageLoadException, ParserFindTagException)as e:
        if isinstance(e, PageLoadException):
            text = f'Возникла ошибка при загрузке страницы: {str(e)}'
        elif isinstance(e, ParserFindTagException):
            text = f'Не найден тег: {str(e)}'
        logging.error(text, stack_info=True)
    finally:
        logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
