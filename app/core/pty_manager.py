#all the imports
import pty
import os
import select
import sys
import termios
import tty


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

    def read(self):
        if self.fd is None:
            return None

        readable, _, _ = select.select(
            [self.fd], [], [], 0.1
        )

        if self.fd in readable:
            return os.read(self.fd, 1024)

        return None

    def close(self):
        #close the file descripter
        fd = self.fd
        self.fd = None

        try:
            if fd is not None:
                os.close(fd)

        finally:
            #child process reaper
            pid = self.pid

            if pid is not None:
                try:
                    while True:
                        try:
                            waitedpid, status = os.waitpid(pid,0)
                            break

                        except InterruptedError:
                            continue

                    self.exit_status = status

                except ChildProcessError:
                    #if child process is reaped
                    self.exit_status = None

                finally:
                    self.pid = None


if __name__ == "__main__":
    manager = PTYManager()
    manager.start()

    print(
        f"PID: {manager.pid}, FD: {manager.fd}",
        flush=True
    )

    stdin_fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(stdin_fd)

    try:
        tty.setraw(stdin_fd)

        while(True):
            readable, _, _ = select.select([stdin_fd,manager.fd],[],[],0.1)

            #keyboard input -> bash
            if stdin_fd in readable:
                data  = os.read(stdin_fd,1024)

                if not data:
                    break

                manager.write(data)

            #bash output -> terminal
            if manager.fd in readable:
                try:
                    data = os.read(manager.fd,1024)

                except OSError:
                    break

                if not data:
                    break

                os.write(sys.stdout.fileno(), data)



    finally:
        termios.tcsetattr(stdin_fd,termios.TCSADRAIN, old_settings )
        manager.close()
