import typing
from itertools import chain
from .logic import global_langs, translation_models_list


def setup_inlines(*args):
    """
    Method to compose Admin inliners with each other
    :param args:
    :return:
    """
    inlines_admins = list(chain(*args))
    return inlines_admins


class TranslateAdminInlines:
    """
    Class iterator. Compose admin inliners, model into new type
    """
    def __init__(self, base_translating_model, inliner_type,
                 include_langs=(),
                 exclude_langs=(),
                 **kwargs):
        assert base_translating_model in translation_models_list, 'This model is not registered as translatable'
        self.base_model = base_translating_model
        self.inliner = inliner_type
        self.kwargs = kwargs
        if not self.kwargs.get('extra'):
            self.kwargs['extra'] = 0
        self.include_langs = [include_lang.lower() for include_lang in include_langs]
        self.exclude_langs = [exclude_lang.lower() for exclude_lang in exclude_langs]
        self.langs = global_langs

        self._prepare_langs()

    def _prepare_langs(self) -> typing.NoReturn:
        """ Method deal with global_langs stuff """
        if self.include_langs and self.exclude_langs:
            raise ValueError("Not possible include and exclude languages")
        elif self.include_langs:
            self.langs = filter(lambda x: x in self.langs, self.include_langs)
        elif self.exclude_langs:
            self.langs = iter([lang for lang in self.langs if lang not in self.exclude_langs])
        else:
            self.langs = iter(self.langs)

    def _prepare_item(self):
        lang = next(self.langs)  # make langs iterator
        name = self.base_model.get_translate_model_name(lang)  # getting our model created name
        base = (self.inliner,)  # set up inliner class
        dct = {'model': self.base_model.get_connected_translated_model_class(lang), **self.kwargs}  # creating dict
        return type(name, base, dct)  # returning class

    def __iter__(self):
        return self

    def __next__(self):
        return self._prepare_item()
