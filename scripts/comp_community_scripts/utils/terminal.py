from __future__ import absolute_import

import sys


__all__ = ('colors', 'StdoutMixin', )


class colors:
    """
    Colors class to allow standard sys.stdout() to write text with specific
    colors in Django management commands.

    Using the BaseCommand self.style attribute has limitations, since it does
    not provide a useful/wide range of colors, and can only be accessed inside
    instances of BaseCommand:
    >>> self.stdout.write('Test', style_func=self.style.SUCCESS)

    This is okay sometimes, but there are utilities, validation and other
    functionality that we want to use with our management commands, and do not
    want to have to always provide the BaseCommand instance to these objects
    just so they can access the colors.
    """
    RESET = "\033[00m"
    BLACK = '\033[30m'

    RED = '\033[31m'
    LIGHTRED = '\033[91m'

    GREEN = '\033[32m'
    LIGHTGREEN = '\033[92m'

    BLUE = '\033[34m'
    LIGHTBLUE = '\033[94m'

    CYAN = '\033[36m'
    LIGHTCYAN = '\033[96m'

    DARKGRAY = '\033[90m'
    LIGHTGRAY = '\033[37m'

    PURPLE = '\033[35m'
    ORANGE = '\033[33m'
    YELLOW = '\033[93m'

    BOLD = '\033[01m'
    UNDERLINE = '\033[04m'
    STRIKETHROUGH = '\033[09m'

    WARNING = YELLOW
    ERROR = RED
    SUCCESS = GREEN
    NOTICE = LIGHTBLUE

    @classmethod
    def format_text(cls, text, color=None, style=None):
        """
        *args can be a tuple (like ERROR = (RED, None)), a single style,
        or a single color.

        >>> self.write("Message", self.ERROR)
        >>> self.write("Message", self.styles.BOLD)
        >>> self.write("Message", self.LIGHTBLUE)
        """
        color = color or ""
        style = style or ""
        return "%s%s%s%s" % (color, style, text, cls.RESET)

    @classmethod
    def write(cls, text, color=None, style=None):
        text = cls.format_text(text, color=color, style=style)
        sys.stdout.write("%s" % text)
        sys.stdout.write("\n")


class StdoutMixin(colors):
    """
    Provides useful methods for outputing styled and easy to read information
    in management commands.
    """
    divider = "----------------------------------------------------------------------"

    def divide(self):
        self.write(self.divider)

    def heading(self, message, divider=False):
        if divider:
            self.divide()
        self.write(message, color=self.DARKGRAY)

    def error(self, message, fatal=False):
        if isinstance(message, Exception):
            message = str(message)
        self.write(message, color=self.ERROR)

    def success(self, message):
        self.write(message, color=self.SUCCESS, style=self.BOLD)

    def notice(self, message):
        if isinstance(message, Exception):
            message = str(message)
        self.write(message, color=self.NOTICE)

    def warn(self, message):
        if isinstance(message, Exception):
            message = str(message)
        self.write(message, color=self.WARNING)

    def newline(self):
        sys.stdout.write('\n')
