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
    value = float(value)
    localizer = get_localizer(request)
    return format_number(round(value, 1), locale=localizer.locale_name) + '%'


def format_value(value, request):
    """
    Format large values by adding a comma
    e.g. 1000 => 1,000
    """
    try:
        value = float(value)
    except Exception:
        value = 0

    localizer = get_localizer(request)
    return format_number(value, locale=localizer.locale_name)


def humanize(value):
    """
    Make value pretty for humans.

    Replace all special characters with spaces.
    """
    return humanize_re.sub(" ", value)


def sum_reduce_func(current, value):
    """
    Reduce the supplied values by summing them and ignoring invalid values
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        value = 0

    try:
        current = int(current)
    except (ValueError, TypeError):
        current = 0

    return abs(value) + abs(current)


def get_impact_indicator_list(indicators_tuple):
    return tuple_to_dict_list(('name', 'key', 'label'), indicators_tuple)


def get_performance_indicator_list(indicators_tuple):
    return tuple_to_dict_list(('property', 'key', 'type'), indicators_tuple)


def number_to_month_name(number):
    months = {
        1: 'January', 2: 'February', 3: 'March', 4: 'April',
        5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September',
        10: 'October', 11: 'November', 12: 'December'}
    return months[number]
