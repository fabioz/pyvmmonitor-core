# License: LGPL
#
# Copyright: Brainwy Software

import StringIO
import subprocess
import sys
import threading

import psutil


PY2 = sys.version_info[0] < 3


def kill_process(pid, kill_children=True):
    process = psutil.Process(pid)

    if kill_children:
        if hasattr(process, 'children'):
            for child in process.children(recursive=True):
                child.kill()
        else:
            for child in process.get_children(recursive=True):
                child.kill()
    process.kill()


class ExecExternal(object):
    '''
    execute_external = ExecExternal([my, cmd])

    # I.e.: call will be in a busy loop getting output, so, we have to
    # do it in a thread.
    threading.Thread(target=execute_external.call).start()

    while not execute_external.finished:
        output = execute_external.get_output()
        if output:
            ... show to user?

        if cancel_it():
            execute_external.cancel()

        sleep(0.1)

    output = execute_external.get_output()
    if output:
        # Do one additional loop as it may have finished but the last output
        # was not gotten.
    '''

    def __init__(self, args, cwd=None, env=None):
        self.args = args
        self.cwd = cwd
        self.env = env
        self.pid = None
        self._read_contents = []
        self._process = None
        self._finished_event = threading.Event()
        self._lock = threading.Lock()

    finished = property(lambda self: self._finished_event.is_set())

    def call(self):
        try:
            startupinfo = None
            if sys.platform == 'win32':
                # We don't want to show the shell on windows!
                startupinfo = subprocess.STARTUPINFO()
                startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
                startupinfo.wShowWindow = subprocess.SW_HIDE
                startupinfo = startupinfo

            if PY2:
                args = []
                for arg in self.args:
                    if isinstance(arg, unicode):
                        arg = arg.encode(sys.getfilesystemencoding())
                    args.append(arg)

            else:
                args = self.args

            process = self._process = subprocess.Popen(
                args=args,
                bufsize=50,
                cwd=self.cwd,
                env=self.env,
                universal_newlines=True,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                startupinfo=startupinfo,
            )
            self.pid = process.pid

            process.stdin.close()
            try:
                for line in iter(process.stdout.readline, ''):
                    with self._lock:
                        self._read_contents.append(line)

                process.wait()
            finally:
                self._finished_event.set()
                self._process = None
        except:
            f = StringIO.StringIO()
            import traceback
            traceback.print_exc(file=f)
            with self._lock:
                self._read_contents.append(f.getvalue())
            raise

    def get_output(self):
        with self._lock:
            current_read = self._read_contents
            self._read_contents = []
            return ''.join(current_read)

    def cancel(self):
        if self._finished_event.isSet():
            return
        process = self._process

        kill_process(process.pid)

        self._finished_event.set()
        self._process = None
