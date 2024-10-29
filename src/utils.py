from bs4 import BeautifulSoup
from requests import RequestException

from exceptions import PageLoadException, ParserFindTagException


def get_response(session, url, is_none=True, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        return response
    except RequestException:
        raise PageLoadException(
            f'Возникла ошибка при загрузке страницы {url}'
        )


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        raise ParserFindTagException(error_msg)
    return searched_tag


def get_soup(session, url):
    response = get_response(session, url)
    soup = BeautifulSoup(response.text, features='lxml')
    return soup
