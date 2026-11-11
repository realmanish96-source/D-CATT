from app.core.pty_manager import PTYManager


class TerminalSession:
    def __init__(self):
        self.pty = PTYManager()
        self.is_running = False

    def start(self):
        if self.is_running:
            return

        self.pty.start()
        self.is_running = True

    def write(self, data):
        if not self.is_running:
            return

        self.pty.write(data)

    def resize(self, rows, columns):
        if not self.is_running:
            return

        self.pty.resize(rows, columns)

    def read(self, timeout=0.1):
        if not self.is_running:
            return None

        data = self.pty.read_available(timeout)

        if data == b"":
            self.is_running = False

        return data

    def close(self):
        try:
            self.pty.close()
        finally:
            self.is_running = False