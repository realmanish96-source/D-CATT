import pyte


class ANSIParser:
    def __init__(self, columns=120, rows=30):
        self.screen = pyte.Screen(columns, rows)
        self.stream = pyte.Stream(self.screen)

    def feed(self, data):
        """
        Feed raw PTY output into pyte.
        """

        if isinstance(data, bytes):
            data = data.decode(
                "utf-8",
                errors="replace"
            )

        self.stream.feed(data)

    def get_display(self):
        """
        Return the current terminal screen.
        """

        return "\n".join(self.screen.display)

    def resize(self, columns, rows):
        """
        Resize the terminal screen.
        """

        self.screen.resize(
            lines=rows,
            columns=columns
        )

    def reset(self):
        """
        Reset terminal screen.
        """

        self.screen.reset()