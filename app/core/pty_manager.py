
import pty
import os
import select


class PTYManager:
    def __init__(self):
        self.pid = None
        self.fd = None

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
        if self.fd is None:
            return

        os.close(self.fd)
        self.fd = None


if __name__ == "__main__":
    manager = PTYManager()
    manager.start()

    print(
        f"PID: {manager.pid}, FD: {manager.fd}",
        flush=True
    )

    try:
        while True:
            readable, _, _ = select.select(
                [0, manager.fd], [], [], 0.1
            )
            readable.append(0)

            # Keyboard input -> Bash
            if 0 in readable:
                data = os.read(0,1024)
                print(f"keyboard input :{data!r}",flush=True)

                if not data:
                    break

                manager.write(data)

            # Bash output -> Terminal
            if manager.fd in readable:
                data = manager.read()

                if data:
                    os.write(1, data)

    except KeyboardInterrupt:
        pass

    finally:
        manager.close()
