import contextlib

import plumbum
from plumbum.commands.processes import run_proc


__all__ = ('FG', )


@contextlib.contextmanager
def bgrun(cmd, retcode=0, timeout=None):
    p = cmd.popen(stdin=None, stdout=None, stderr=None)
    was_run = [False]

    def runner():
        if was_run[0]:
            return  # already done
        was_run[0] = True
        try:
            return run_proc(p, retcode=0, timeout=None)
        except KeyboardInterrupt:
            p.wait()
            raise
        finally:
            del p.run  # to break cyclic reference p -> cell -> p
            for f in [p.stdin, p.stdout, p.stderr]:
                try:
                    f.close()
                except Exception:
                    pass
    p.run = runner
    yield p
    runner()


class FG(type(plumbum.FG)):

    def __rand__(self, cmd):
        with bgrun(cmd, retcode=self.retcode, timeout=self.timeout) as p:
            p.run()


FG = FG()
