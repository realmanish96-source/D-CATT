# Linux-specific imports
import errno
import fcntl
import os
import pty
import select
import signal
import struct
import termios
import time


class PTYManager:
    def __init__(self):
        self.pid = None
        self.fd = None
        self.exit_status = None

    def start(self):
        self.pid, self.fd = pty.fork()

        if self.pid == 0:
            os.execlp("bash", "bash")

    def write(self, data):
        if self.fd is None:
            return

        os.write(self.fd, data)

    def resize(self, rows, columns):
        if self.fd is None:
            return

        winsize = struct.pack("HHHH", rows, columns, 0, 0)
        fcntl.ioctl(self.fd, termios.TIOCSWINSZ, winsize)

    def read(self):
        if self.fd is None:
            return None

        try:
            return os.read(self.fd, 1024)

        except OSError as exc:
            # EIO usually indicates that the PTY slave has closed
            if exc.errno == errno.EIO:
                return b""

            raise

    def read_available(self, timeout=0.1):
        if self.fd is None:
            return None

        readable, _, _ = select.select(
            [self.fd],
            [],
            [],
            timeout
        )

        if not readable:
            return None

        return self.read()

    def _wait_for_exit(self, pid, timeout):
        deadline = time.monotonic() + timeout

        while time.monotonic() < deadline:
            try:
                waited_pid, status = os.waitpid(
                    pid,
                    os.WNOHANG
                )

            except InterruptedError:
                continue

            except ChildProcessError:
                return True, None

            if waited_pid == pid:
                return True, os.waitstatus_to_exitcode(status)

            time.sleep(0.05)

        return False, None

    def close(self):
        # Keep close() safe if called more than once
        fd = self.fd
        self.fd = None

        try:
            if fd is not None:
                os.close(fd)

        finally:
            pid = self.pid

            if pid is not None:
                try:
                    # Give the child process a moment to exit naturally
                    finished, status = self._wait_for_exit(
                        pid,
                        0.5
                    )

                    if not finished:
                        try:
                            os.kill(pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass

                        finished, status = self._wait_for_exit(
                            pid,
                            0.5
                        )

                    if not finished:
                        try:
                            os.kill(pid, signal.SIGKILL)
                        except ProcessLookupError:
                            pass

                        # Reap the forcibly terminated child
                        while True:
                            try:
                                _, raw_status = os.waitpid(pid, 0)

                                self.exit_status = (
                                    os.waitstatus_to_exitcode(raw_status)
                                )
                                break

                            except InterruptedError:
                                continue

                            except ChildProcessError:
                                self.exit_status = None
                                break

                    else:
                        self.exit_status = status

                finally:
                    self.pid = None