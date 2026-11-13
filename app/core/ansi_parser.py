import copy
from itertools import islice

import pyte
from pyte import modes as pyte_modes


class _TerminalScreen(pyte.HistoryScreen):
    _ALTERNATE_SCREEN_MODES = {47, 1047, 1049}
    _SCREEN_STATE_ATTRIBUTES = (
        "buffer",
        "columns",
        "cursor",
        "dirty",
        "g0_charset",
        "g1_charset",
        "icon_name",
        "lines",
        "margins",
        "mode",
        "savepoints",
        "saved_columns",
        "tabstops",
        "title",
        "charset",
        "_dec_1048_state",
    )

    def __init__(self, columns, lines, history):
        self.alternate_screen_active = False
        self._main_screen_state = None
        self._alternate_screen_state = None
        self._dec_1048_state = None
        super().__init__(columns, lines, history=history)

    def _capture_screen_state(self):
        state = {
            attribute: getattr(self, attribute)
            for attribute in self._SCREEN_STATE_ATTRIBUTES
        }
        state["buffer"] = copy.deepcopy(self.buffer)
        state["cursor"] = copy.copy(self.cursor)
        state["dirty"] = self.dirty.copy()
        state["mode"] = self.mode.copy()
        state["savepoints"] = copy.deepcopy(self.savepoints)
        state["tabstops"] = self.tabstops.copy()
        state["_dec_1048_state"] = copy.deepcopy(self._dec_1048_state)
        return state

    def _restore_screen_state(self, state):
        for attribute in self._SCREEN_STATE_ATTRIBUTES:
            setattr(self, attribute, state[attribute])

    def _enter_alternate_screen(self, clear):
        if self.alternate_screen_active:
            return

        self._main_screen_state = self._capture_screen_state()
        self.alternate_screen_active = True

        if clear or self._alternate_screen_state is None:
            self._dec_1048_state = None
            pyte.Screen.reset(self)
            self.savepoints = []
        else:
            self._restore_screen_state(self._alternate_screen_state)

        self.dirty.update(range(self.lines))

    def _leave_alternate_screen(self, clear):
        if not self.alternate_screen_active:
            return

        if not clear:
            self._alternate_screen_state = self._capture_screen_state()
        else:
            self._alternate_screen_state = None

        main_state = self._main_screen_state
        self._main_screen_state = None
        self.alternate_screen_active = False
        self._restore_screen_state(main_state)
        self.dirty.update(range(self.lines))

    def set_mode(self, *modes, **kwargs):
        if not kwargs.get("private"):
            return super().set_mode(*modes, **kwargs)

        alternate_modes = self._ALTERNATE_SCREEN_MODES.intersection(modes)
        if alternate_modes:
            self._enter_alternate_screen(
                clear=bool(alternate_modes.intersection({1047, 1049}))
            )

        if 1048 in modes:
            self._dec_1048_state = (
                copy.copy(self.cursor),
                self.g0_charset,
                self.g1_charset,
                self.charset,
                pyte_modes.DECOM in self.mode,
                pyte_modes.DECAWM in self.mode,
            )

        forwarded_modes = tuple(mode for mode in modes if mode != 1048)
        if forwarded_modes:
            super().set_mode(*forwarded_modes, **kwargs)

    def reset_mode(self, *modes, **kwargs):
        if not kwargs.get("private"):
            return super().reset_mode(*modes, **kwargs)

        if 1048 in modes and self._dec_1048_state is not None:
            (
                cursor,
                self.g0_charset,
                self.g1_charset,
                self.charset,
                origin_mode,
                wrap_mode,
            ) = self._dec_1048_state
            if origin_mode:
                self.set_mode(pyte_modes.DECOM)
            else:
                self.reset_mode(pyte_modes.DECOM)
            if wrap_mode:
                self.set_mode(pyte_modes.DECAWM)
            else:
                self.reset_mode(pyte_modes.DECAWM)
            self.cursor = copy.copy(cursor)
            self.ensure_hbounds()
            self.ensure_vbounds(use_margins=True)
            self._dec_1048_state = None

        forwarded_modes = tuple(mode for mode in modes if mode != 1048)
        if forwarded_modes:
            super().reset_mode(*forwarded_modes, **kwargs)

        if self._ALTERNATE_SCREEN_MODES.intersection(modes):
            self._leave_alternate_screen(clear=1047 in modes)

    def index(self):
        if self.alternate_screen_active:
            return pyte.Screen.index(self)
        return super().index()

    def reverse_index(self):
        if self.alternate_screen_active:
            return pyte.Screen.reverse_index(self)
        return super().reverse_index()

    def erase_in_display(self, how=0, *args, **kwargs):
        if self.alternate_screen_active:
            return pyte.Screen.erase_in_display(self, how, *args, **kwargs)
        return super().erase_in_display(how, *args, **kwargs)

    def resize(self, lines=None, columns=None):
        target_lines = lines or self.lines
        target_columns = columns or self.columns
        super().resize(lines=target_lines, columns=target_columns)

        if self._main_screen_state is not None:
            self._main_screen_state = self._resize_saved_state(
                self._main_screen_state,
                target_lines,
                target_columns
            )

        if self._alternate_screen_state is not None:
            self._alternate_screen_state = self._resize_saved_state(
                self._alternate_screen_state,
                target_lines,
                target_columns
            )

    def _resize_saved_state(self, state, lines, columns):
        if state["lines"] == lines and state["columns"] == columns:
            return state

        active_state = self._capture_screen_state()
        self._restore_screen_state(state)
        try:
            pyte.Screen.resize(self, lines=lines, columns=columns)
            return self._capture_screen_state()
        finally:
            self._restore_screen_state(active_state)


class ANSIParser:
    def __init__(self, columns=120, rows=30):
        self.screen = _TerminalScreen(
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

        was_alternate = self.screen.alternate_screen_active
        history_length = len(self.screen.history.top)
        self.stream.feed(data)
        if was_alternate != self.screen.alternate_screen_active:
            self.scroll_offset = 0
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
        if self.screen.alternate_screen_active:
            return

        self.scroll_offset = min(
            len(self.screen.history.top),
            self.scroll_offset + max(0, lines)
        )

    def scroll_down(self, lines=3):
        if self.screen.alternate_screen_active:
            return

        self.scroll_offset = max(0, self.scroll_offset - max(0, lines))

    @property
    def mouse_tracking_enabled(self):
        return any(
            mode << 5 in self.screen.mode
            for mode in (1000, 1002, 1003)
        )

    @property
    def application_cursor_keys(self):
        return 1 << 5 in self.screen.mode

    @property
    def sgr_mouse_enabled(self):
        return 1006 << 5 in self.screen.mode

    def mouse_wheel_sequence(self, direction, column, row):
        button = 64 if direction > 0 else 65

        if self.sgr_mouse_enabled:
            return f"\x1b[<{button};{column};{row}M".encode("ascii")

        return bytes((
            0x1B,
            ord("["),
            ord("M"),
            button + 32,
            min(column + 32, 255),
            min(row + 32, 255),
        ))

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
