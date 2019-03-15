from __future__ import print_function

from os.path import join, dirname, realpath

from plumbum import cli, local
from plumbum.cmd import docker_compose

from comp_community_scripts import __version__

from .app_ports import app_ports

from .utils.exceptions import CompCommandError
from .utils.logging import get_logger
from .utils.plumbum import FG

from .base import CompositionApplication


local.env["COMPOSE_HTTP_TIMEOUT"] = "6000"

scripts_dir = local.path(realpath(join(dirname(__file__), "..")))
root_dir = scripts_dir / '..'

logger = get_logger()


class Composition(cli.Application):
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
