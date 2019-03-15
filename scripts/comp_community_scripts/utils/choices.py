from __future__ import absolute_import

import inspect
from collections import Iterable

from .exceptions import (MissingParameterError, InvalidParameterError,
    InvalidInputError)


__all__ = ('get_choice_options', )


class ChoiceOption(object):

    def __init__(self, obj, attr=None, index=None, key=None):
        self.obj = obj
        self.attr = attr
        self.index = index
        self.key = key

    @classmethod
    def _get_obj_attr(cls, obj, attr=None):
        """
        Retrieves the attribute off of a generic object or dictionary.

        TODO: These methods might be eventually useful to maintain inside of
        ollie.utils once that reorganization is done.
        """
        if inspect.isclass(obj) or type(obj) is dict or hasattr(obj, '__dict__'):
            if not attr:
                raise MissingParameterError('attr')

            if inspect.isclass(obj) or hasattr(obj, '__dict__'):
                if not hasattr(obj, attr):
                    raise InvalidParameterError('attr', attr)
                return getattr(obj, attr)
            else:
                try:
                    return obj[attr]
                except KeyError:
                    raise InvalidParameterError('attr', attr)

        elif isinstance(obj, Iterable) and type(obj) is not dict:
            return obj

        return obj

    @classmethod
    def _get_obj_attr_recursively(cls, obj, attr=None):
        """
        Finds attributes on a dict or object by '.' separated values.

        TODO: These methods might be eventually useful to maintain inside of
        ollie.utils once that reorganization is done.
        """
        if attr:
            if len(attr.split('.')) == 1:
                return cls._get_obj_attr(obj, attr=attr)
            else:
                parts = attr.split('.')
                nested_obj = cls._get_obj_attr(obj, attr=parts[0])
                return cls._get_obj_attr_recursively(nested_obj, '.'.join(parts[1:]))
        return cls._get_obj_attr(obj, attr=attr)

    @property
    def body_text(self):
        return self._get_obj_attr_recursively(self.obj, attr=self.attr)

    def __str__(self):
        if self.index is not None and self.key:
            return '(%s) %s: %s' % (self.index + 1, self.key, self.body_text)
        elif self.index is not None:
            return '(%s) %s' % (self.index + 1, self.body_text)
        elif self.key:
            return '%s: %s' % (self.key, self.body_text)
        else:
            return '%s' % self.body_text


def get_choice_options(choices, numbered=False, attr=None, key=None):
    """
    Given an Iterable of objects (dict, object, string, etc.) or a dict,
    will create an instance of ChoiceOption for each item.

    These instances will be displayed in their __str__ format, but they
    also contain other properties that are important when the selected option
    is returned from a management command input request.

    # Common usage
    >>> get_choice_options([
            {'id': 1, 'issue': {'slug': 2018, 'dek': '2018 Issue'}},
            {'id': 2, 'issue': {'slug': 2019, 'dek': '2019 Issue'}},
        ], attr='issue.dek', key='Description')
    >>> ['Description: 2018 Issue', 'Description: 2019 Issue']

    # Usage with single dict.
    >>> get_choice_options({'ID': 1, 'Name': 'John'}, numbered=True)
    >>> ['(1) ID: 1', '(2) Name: John']
    """
    items = []
    if isinstance(choices, dict):
        for i, (dict_key, val) in enumerate(choices.items()):
            index = i if numbered else None
            items.append(ChoiceOption(val, key=dict_key, index=index))

    elif isinstance(choices, Iterable):
        for i, choice in enumerate(choices):
            index = i if numbered else None
            items.append(ChoiceOption(choice, index=index, attr=attr, key=key))

    else:
        raise InvalidInputError('Invalid iterable supplied.')

    return items
