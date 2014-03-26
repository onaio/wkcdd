from pyramid.i18n import TranslationStringFactory, get_localizer

translation_string_factory = TranslationStringFactory('wkcdd')


def tuple_to_dict_list(key_tuple, value_tuples):
    return [dict(zip(key_tuple, c)) for c in value_tuples]
