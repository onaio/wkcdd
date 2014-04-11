import re
from pyramid.i18n import TranslationStringFactory, get_localizer

from babel.numbers import format_number


translation_string_factory = TranslationStringFactory('wkcdd')
humanize_re = re.compile(r"[\W_]+")


def tuple_to_dict_list(key_tuple, value_tuples):
    return [dict(zip(key_tuple, c)) for c in value_tuples]


def format_percent(value, request):
    """
    Format 123.54 to a pretty percentage value i.e. 123.5%
    """
    if value is None:
        return 0
    value = float(value)
    localizer = get_localizer(request)
    return format_number(round(value, 1), locale=localizer.locale_name) + '%'


def format_value(value, request):
    """
    Format large values by adding a comma
    e.g. 1000 => 1,000
    """
    if value is None:
        return 0
    value = float(value)
    localizer = get_localizer(request)
    return format_number(value, locale=localizer.locale_name)


def humanize(value):
    """
    Make value pretty for humans.

    Replace all special characters with spaces.
    """
    return humanize_re.sub(" ", value)
