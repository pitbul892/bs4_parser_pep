from requests import RequestException

from exceptions import ParserFindTagException


def get_response(session, url, is_none=True, encoding='utf-8'):
    try:
        response = session.get(url)
        response.encoding = encoding
        if is_none and response is None:
            return None
        return response
    except RequestException:
        return f'Возникла ошибка при загрузке страницы {url}'


def find_tag(soup, tag, attrs=None):
    searched_tag = soup.find(tag, attrs=(attrs or {}))
    if searched_tag is None:
        error_msg = f'Не найден тег {tag} {attrs}'
        raise ParserFindTagException(error_msg)
    return searched_tag
