from __future__ import absolute_import

from os.path import join, dirname, realpath

from plumbum import cli, local
from plumbum.cmd import docker_compose, egrep

from .utils.choices import get_choice_options
from .utils.exceptions import CompCommandError
from .utils.logging import get_logger
from .utils.plumbum import FG
from .utils.prompts import UserPrompt, ChoicePrompt, BooleanPrompt
from .utils.terminal import StdoutMixin


__all__ = ('CompositionApplication', )


scripts_dir = local.path(realpath(join(dirname(__file__), "..")))
root_dir = scripts_dir / '..'

logger = get_logger()


class CompositionApplication(StdoutMixin, cli.Application):
    """
    These are not flags that we currently use, but we will leave them here
    for reference because we might use them in the future or need to define
    flags similarly.

    >>> with_sentry = cli.Flag("--with-sentry", default=False)
    >>> with_celery = cli.Flag("--with-celery", default=False)
    """
    @property
    def compose_files(self):
        return ['docker-compose.yml']

    @property
    def compose_flags(self):
        flags = []
        for f in self.compose_files:
            flags += ['-f', f]
        return flags

    @classmethod
    def create_compose_flags(cls, files=None):
        compose_files = files or ['docker-compose.yml']
        compose_flags = []
        for f in compose_files:
            compose_flags += ['-f', f]
        return compose_flags

    def display_line_items(self, choices, numbered=False, attr=None, key=None):
        """
        Given an Iterable of objects (dict, object, string, etc.) or a dict,
        will create a line item display for each item and display output them
        to the user.

        >>> self.display_line_items({'ID': 1, 'Name': 'John'}, numbered=True)
        >>> (1) ID: 1
        >>> (2) Name: John

        >>> self.display_line_items([
                {'id': 1, 'issue': {'slug': 2018, 'dek': '2018 Issue'}},
                {'id': 2, 'issue': {'slug': 2019, 'dek': '2019 Issue'}},
            ], attr='issue.dek', key='Description')
        >>> Description: 2018 Issue
        >>> Description: 2019 Issue
        """
        obj_choices = get_choice_options(choices, attr=attr, numbered=numbered, key=key)
        for choice in obj_choices:
            self.write(str(choice))

    def create_generator(self, prompt, prompter):
        """
        If an ask method is called with continual=True, the method must
        return a generator that can be iterated over to provide a series
        of user input.
        """
        def gen():
            while not prompter.quit:
                response = prompter(prompt)
                if response:
                    yield response
        return gen()

    def _ask(self, prompt, prompter, continual=False):
        if not continual:
            return prompter(prompt)
        return self.create_generator(prompt, prompter)

    def ask(self, prompt, continual=False, **kwargs):
        prompter = UserPrompt(**kwargs)
        return self._ask(prompt, prompter, continual=continual)

    def bool_ask(self, question, continual=False, **kwargs):
        """
        Provide the functionality for management commands to request (y/n) user input
        and wait until the input is valid to proceed.
        """
        prompter = BooleanPrompt(**kwargs)
        return self._ask(question, prompter, continual=continual)

    def choice_ask(self, choices, prompt=None, continual=False, **kwargs):
        """
        Provide functionality for management commands to display a list of choices
        and then select a choice based in an integer input.

        Choices can be objects, dicts or elements.  If objects or dicts are provided,
        an attr must be specified so the attribute in the dictionary or object
        can be accessed to display.
        """
        prompt = prompt or "Choose from the available options"
        prompter = ChoicePrompt(self, choices, **kwargs)
        return self._ask(prompt, prompter, continual=continual)

    @classmethod
    def pull_from_docker_hub(cls, files=None, flags=None):
        with local.cwd(root_dir):
            if not flags:
                flags = cls.create_compose_flags(files=files)
            logger.info("Attempting to pull from docker hub")
            try:
                docker_compose[flags + ['pull']] & FG
            except Exception as e:
                print(e)
                raise CompCommandError(
                    "There was an error using 'docker-compose pull'.\n"
                    "Are you logged into docker hub?")

    @classmethod
    def stop_docker(cls, flags=None, files=None):
        if not flags:
            flags = cls.create_compose_flags(files=files)

        compose_containers = (
            docker_compose[flags + ['ps']] | egrep['Up'])(retcode=None)
        if compose_containers:
            docker_compose[flags + ['stop']] & FG

    @classmethod
    def start_database_server(cls):
        # TODO: When we figure out what we are doing with the database.
        docker_compose['run', '--rm', 'mysqld', 'initialize'] & FG

    @classmethod
    def start_api_server(cls, flags=None, files=None):
        if not flags:
            flags = cls.create_compose_flags(files=files)
        docker_compose[flags + ['up']] & FG

    @classmethod
    def setup(cls, files=None, flags=None):

        if not flags:
            flags = cls.create_compose_flags(files=files)

        with local.cwd(root_dir):
            cls.stop_docker(flags=flags)
            cls.pull_from_docker_hub(flags=flags)

            # We will eventually want to secure things with SSH
            # init_ssh_agent_forward()
            # cls.start_database_server()

            cls.start_api_server()

        docker_compose[flags + ['down']] & FG
        print("\nSuccessfully setup comp-community!")

    @classmethod
    def start(cls, files=None, flags=None):

        if not flags:
            flags = cls.create_compose_flags(files=files)

        with local.cwd(root_dir):
            cls.stop_docker(flag=flags)

            # We will eventually want to secure things with SSH
            # init_ssh_agent_forward()

    @classmethod
    def comp_community_check_for_updates(cls, files=None, flags=None):
        return

    @classmethod
    def containers_needing_update(cls, files=None, flags=None):
        return None
