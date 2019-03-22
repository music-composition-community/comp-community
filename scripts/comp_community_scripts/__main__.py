from __future__ import print_function

import os

from plumbum import cli, local
from plumbum.cmd import docker_compose

from comp_community_scripts import __version__

from .app_ports import app_ports

from .utils.exceptions import CompCommandError
from .utils.logging import get_logger
from .utils.plumbum import FG

from .base import CompositionApplication


local.env["COMPOSE_HTTP_TIMEOUT"] = "6000"

# TODO: See if we can tie these in with export SCRIPTS_ROOT="${COMP_ROOT}/scripts"
# in env.sh.
scripts_dir = local.path(os.path.realpath(os.path.join(os.path.dirname(__file__), "..")))
root_dir = scripts_dir / '..'

logger = get_logger()


class Composition(cli.Application):
    """
    TODO:
    ------
    Might be useful to start using Docker SDK.
    """
    VERSION = __version__

    def main(self, *args):
        if args:
            print("Unknown command %r" % (args[0]))
            return 1
        if not self.nested_command:
            print("No command given")
            return 1


@Composition.subcommand("setup")
class CompositionSetup(CompositionApplication):

    port = app_ports['api']
    host = "0.0.0.0"
    env_vars = {}

    def main(self, *args):
        try:
            self.setup()
        except KeyboardInterrupt:
            pass
        except CompCommandError as e:
            logger.error("Error during setup: %s" % e)


@Composition.subcommand("migrate")
class CompositionMigrate(cli.Application):

    port = app_ports['api']

    def main(sel, *args):
        with local.cwd(root_dir):
            """
            TODO:
            -----
            We have to add a --user flag here, that we should register
            somewhere before this point (probably in DockerFile).

            Then, we would want to run the binary in /api/bin/manage
            >>> docker_compose['exec', 'api', '--user', 'xxx',
            >>>     '/api/bin/manage', 'migrate']
            """
            docker_compose[
                'exec', 'api', '/api/apps/manage.py', 'migrate',
            ] & FG


@Composition.subcommand("shell")
class CompositionShell(cli.Application):
    """
    Opens a bash shell.
    """
    root = cli.Flag("--root", default=False)

    def _get_user(self, service='api'):
        user = 'root'
        if self.root:
            return user
        if service == 'api':
            return 'apiuser'
        return user

    def _get_bash_cmd(self, service='api'):
        # Here is where we could add a custom config file for BASH.
        # bash_cmd = 'bash --init-file ~/.ollierc -i'
        service_cmds = {
            'default': 'bash -i',
            # 'api': 'bash --init-file ~/.apirc -i'
            'api': 'bash --init-file /api/.apirc -i'
        }
        return service_cmds[service]

    def main(self, service='api'):
        user = self._get_user(service=service)
        bash_cmd = self._get_bash_cmd(service=service)

        with local.cwd(root_dir):
            docker_compose['-f', 'docker-compose.yml', 'exec', '--user', user,
                'api', 'script', '-q', '/dev/null', '-c', bash_cmd] & FG(retcode=None)


@Composition.subcommand("start")
class CompositionStart(CompositionApplication):

    port = app_ports['api']
    host = "0.0.0.0"
    env_vars = {}

    def main(self, *args):
        # Not currently checking for updates, but will want to do eventually:
        try:
            self.comp_community_check_for_updates()
            to_update = self.containers_needing_update(files=self.compose_files)
            if to_update:
                response = self.bool_ask("Containers out of date; download updates?")
                if response:
                    self.pull_from_docker_hub(files=self.compose_files)

            with local.cwd(root_dir):
                with local.env(**self.env_vars):
                    docker_compose['up', '--abort-on-container-exit'] & FG
        except KeyboardInterrupt:
            pass
        except CompCommandError as e:
            logger.error("Error starting Composition Community: %s" % e)


def main():
    Composition.run()


if __name__ == '__main__':
    main()
