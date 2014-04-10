import re

from pyramid.i18n import TranslationStringFactory


translation_string_factory = TranslationStringFactory('wkcdd')
humanize_re = re.compile(r"[\W_]+")


def tuple_to_dict_list(key_tuple, value_tuples):
    return [dict(zip(key_tuple, c)) for c in value_tuples]


def humanize(value):
    """
    Make value pretty for humans.

    Replace all special characters with spaces.
    """
    return humanize_re.sub(" ", value)