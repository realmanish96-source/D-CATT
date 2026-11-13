from itertools import islice

import pyte


class ANSIParser:
    def __init__(self, columns=120, rows=30):
        self.screen = pyte.HistoryScreen(
            columns,
            rows,
            history=10000
        )

        self.stream = pyte.Stream(self.screen)
        self.scroll_offset = 0

    def feed(self, data):
        if isinstance(data, bytes):
            data = data.decode(
                "utf-8",
                errors="replace"
            )

        history_length = len(self.screen.history.top)
        self.stream.feed(data)
        if self.scroll_offset:
            added_lines = len(self.screen.history.top) - history_length
            if added_lines > 0:
                self.scroll_offset = min(
                    len(self.screen.history.top),
                    self.scroll_offset + added_lines
                )

    def get_display(self):
        history = self.screen.history.top
        offset = min(self.scroll_offset, len(history))
        if offset == 0:
            return "\n".join(self.screen.display)

        start = len(history) - offset
        end = min(len(history), start + self.screen.lines)
        lines = [
            "".join(line[x].data for x in range(self.screen.columns))
            for line in islice(history, start, end)
        ]
        lines.extend(self.screen.display[:self.screen.lines - len(lines)])
        return "\n".join(lines)

    def get_styled_display(self):
        """
        Return the current visible terminal content as
        rows containing pyte character cells.
        Respects the current scroll position.
        """

        lines = []

        # Live screen
        if self.scroll_offset == 0:
            source_lines = [
                self.screen.buffer[y]
                for y in range(self.screen.lines)
            ]

    # Scrollback + screen
        else:
            history = list(self.screen.history.top)

            combined = history + [
                self.screen.buffer[y]
                for y in range(self.screen.lines)
            ]

            start = max(
                0,
                len(combined) - self.screen.lines - self.scroll_offset
            )

            source_lines = combined[
                start:start + self.screen.lines
            ]

        for line in source_lines:
            styled_line = []

            for x in range(self.screen.columns):
                char = line[x]

                styled_line.append({
                "char": char.data,
                "fg": char.fg,
                "bg": char.bg,
                "bold": char.bold,
                "italics": char.italics,
                "underscore": char.underscore,
                "reverse": char.reverse,
                })

            lines.append(styled_line)

        return lines

 
    def scroll_up(self, lines=3):
        self.scroll_offset = min(
            len(self.screen.history.top),
            self.scroll_offset + max(0, lines)
        )

    def scroll_down(self, lines=3):
        self.scroll_offset = max(0, self.scroll_offset - max(0, lines))

    def get_cursor_display_row(self, row):
        display_row = row + min(
            self.scroll_offset,
            len(self.screen.history.top)
        )
        if 0 <= display_row < self.screen.lines:
            return display_row
        return None

    def resize(self, columns, rows):
        self.screen.resize(
            lines=rows,
            columns=columns
        )

    def reset(self):
        self.screen.reset()
        self.scroll_offset = 0
