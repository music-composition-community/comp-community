# -*- coding: utf-8 -*-

__all__ = (
    'CompCommandError',
    'MissingParameterError',
    'InvalidParameterError',
    'InvalidInputError',
    'BooleanInputError',
)


class CompCommandError(Exception):
    pass


class MissingParameterError(CompCommandError):
    """
    Raised when a parameter provided to the user input methods is
    missing.
    """
    def __init__(self, attr, extension=None):
        message = "The parameter '%s' is required." % attr
        super(MissingParameterError, self).__init__(message)


class InvalidParameterError(CompCommandError):
    """
    Raised when a parameter provided to the user input methods is
    invalid.
    """
    def __init__(self, attr, val, extension=None):
        message = "%s is not a valid value for parameter %s." % (val, attr)
        super(InvalidParameterError, self).__init__(message)


class InvalidInputError(CompCommandError):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return "The input %s is invalid." % self.value


class BooleanInputError(InvalidInputError):
    def __str__(self):
        return "Invalid choice %s." % self.value
