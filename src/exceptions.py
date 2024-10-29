class ParserFindTagException(Exception):
    """Вызывается, когда парсер не может найти тег."""

    pass


class PageLoadException(Exception):
    """Вызывается, когда парсер не может получить response."""

    pass
