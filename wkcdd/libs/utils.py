import re
from pyramid.i18n import TranslationStringFactory, get_localizer

from babel.numbers import format_number

translation_string_factory = TranslationStringFactory('wkcdd')


def tuple_to_dict_list(key_tuple, value_tuples):
    return [dict(zip(key_tuple, c)) for c in value_tuples]


def format_percent(value, request):
    value = value if type(value) == float else float(value)
    localizer = get_localizer(request)
    return format_number(round(value, 1), locale=localizer.locale_name) + '%'


def format_value(value, request):
    value = value if type(value) == float else float(value)
    localizer = get_localizer(request)
    return format_number(value, locale=localizer.locale_name)


def number_to_symbol(value):
    return re.sub('Total|Number', '#', value)
