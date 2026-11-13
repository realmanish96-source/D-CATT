import os
import time
import unittest
from unittest.mock import patch

from app.systems.linux import PTYManager


class PTYManagerTests(unittest.TestCase):
    def test_shell_receives_xterm_and_truecolor_environment(self):
        manager = PTYManager()
        with patch.dict(os.environ, {"TERM": "dumb"}):
            manager.start()
            try:
                manager.write(b'printf "\\n__TERM__%s__COLOR__%s\\n" "$TERM" "$COLORTERM"\n')
                output = bytearray()
                deadline = time.monotonic() + 2
                while time.monotonic() < deadline:
                    chunk = manager.read_available(timeout=0.1)
                    if chunk:
                        output.extend(chunk)
                    if b"__TERM__xterm-256color__COLOR__truecolor" in output:
                        break
                self.assertIn(
                    b"__TERM__xterm-256color__COLOR__truecolor",
                    output
                )
            finally:
                manager.close()


if __name__ == "__main__":
    unittest.main()
