import pty
import os
import select
import sys

pid, fd = pty.fork()

if pid == 0:
    os.execlp("bash", "bash")

else:
    print(f"Child PID: {pid}, PTY FD: {fd}", flush=True)

    try:
        while True:
            readable, _, _ = select.select([fd, 0], [], [], 1.0)

            # Keyboard input -> Bash
            if 0 in readable:
                data = os.read(0, 1024)

                if not data:
                    break

                os.write(fd, data)

            # Bash output -> terminal
            if fd in readable:
                try:
                    data = os.read(fd, 1024)
                except OSError:
                    break

                if not data:
                    break

                os.write(1, data)

    except KeyboardInterrupt:
        pass

    finally:
        os.close(fd)