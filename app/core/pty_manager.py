import pty
import os

pid, fd = pty.fork()

if (pid == 0):
    os.execlp("bash","bash")

else:
    while True:
        data = os.read(fd, 1024)

        if not data:
            break

        print(data)