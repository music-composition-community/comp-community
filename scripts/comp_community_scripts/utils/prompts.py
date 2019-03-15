from __future__ import absolute_import

from .exceptions import InvalidInputError
from .choices import get_choice_options
from .terminal import StdoutMixin


__all__ = ('UserPrompt', 'BooleanPrompt', 'ChoicePrompt', )


class UserPrompt(StdoutMixin, object):
    """
    A UserPrompt object controls settings and handling of responses when asking
    for user input in management commands.

    Prompts will request information from the user and continue to ask for
    the input if it is invalidated.  If the user quits, the prompt will stop
    asking.

    UserPrompt can be subclassed to provide different validation rules requiring
    specific types of input.

    They can also be used inside generators to request input and perform a task
    based on that input, and then repeat the cycle.
    """
    QUIT_EXTENSION = "q to quit"

    def __init__(self, color=None, style=None):

        self.color = color
        self.style = style

        self.quit = False
        self.num_prompts = 0
        self.response = None

    def format_prompt(self, prompt):
        prompt = self.format_text(prompt, color=self.color, style=self.style)

        extensions = [self.QUIT_EXTENSION]
        if hasattr(self, 'EXTENSION'):
            extensions = [self.EXTENSION, self.QUIT_EXTENSION]

        extensions = map(lambda ext: "(%s)" % ext, extensions)
        extension_text = ' '.join(extensions)
        return prompt + ' ' + extension_text + ' '

    @classmethod
    def validate_input(cls, value):
        """
        Want to externalize this utility as well.
        """
        return cls()._validate_input(value)

    def _validate_input(self, value):
        """
        A validate_input must be a method that:
        (1) Takes as its first argument the user input.
        (2) Raises an InvalidInputError if the input is invalid.
        (3) Returns a formatted or original valid input if input is valid.
        """
        return value

    def check_if_quitting(self, input):
        self.quit = False
        try:
            input = str(input)
        except ValueError:
            self.quit = False
        else:
            if str(input).lower() == 'q':
                self.quit = True

    def raw_input(self, prompt):
        raw_response = input(self.format_prompt(prompt))
        self.check_if_quitting(raw_response)
        return raw_response

    def __call__(self, prompt):
        """
        Prompts user for user input.

        Notes if the user has quit.  If the user did not quit, the provided
        input will be validated and not returned until this validation is
        successful.
        """
        self.response = None
        self.quit = False

        while self.response is None and not self.quit:
            raw_response = self.raw_input(prompt)
            if not self.quit:
                try:
                    self.response = self._validate_input(raw_response)
                except InvalidInputError as e:
                    self.error(e)
                else:
                    self.num_prompts += 1
                    return self.response


class BooleanPrompt(UserPrompt):

    BOOL_CONVERSION = {'y': True, 'n': False, 'yes': True, 'no': False}
    ERROR_MESSAGE = "Invalid choice, please type 'y' or 'n'"
    EXTENSION = "y/n"

    def _validate_input(self, value):
        """
        Validates prompted user input for (y/n).
        If default_true is True, then an empty string (i.e. the user not entering a
        response but clicking "Enter") will return as True.  Otherwise, it will be
        False (i.e. not a valid response).
        """
        if not isinstance(value, str):
            raise InvalidInputError(self.ERROR_MESSAGE)
        try:
            value = value.strip()
            return self.BOOL_CONVERSION[value.lower()]
        except KeyError:
            raise InvalidInputError(self.ERROR_MESSAGE)


class ChoicePrompt(UserPrompt):

    EXTENSION = "select by number"

    def __init__(self, choices, attr=None, divider=False, **kwargs):
        super(ChoicePrompt, self).__init__(**kwargs)
        self.divider = divider

        self.choices = get_choice_options(choices, attr=attr, numbered=True)
        self.ERROR_MESSAGE = ("Input must be an integer in range %s to %s." %
            (1, len(choices)))

    def display_choices(self):
        for choice in self.choices:
            self.write(str(choice), color=self.color, style=self.style)

    @classmethod
    def validate_input(cls, value, choices):
        return cls(choices)._validate_input(value)

    def _validate_input(self, value):
        try:
            value = int(value)
        except ValueError:
            raise InvalidInputError(self.ERROR_MESSAGE)
        else:
            if value <= 0:
                raise InvalidInputError(self.ERROR_MESSAGE)
            else:
                try:
                    return self.choices[value - 1]
                except IndexError:
                    raise InvalidInputError(self.ERROR_MESSAGE)

    def __call__(self, prompt):
        if self.num_prompts == 0:
            if self.divider:
                self.divide()
            self.display_choices()

        return super(ChoicePrompt, self).__call__(prompt)
