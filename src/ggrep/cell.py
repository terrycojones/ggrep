import re
from typing import Any


class Cell:
    def __init__(self, value: Any, pattern: re.Pattern):
        self.value = value
        svalue = str(value)
        if match := pattern.search(svalue):
            self.matched = True
            start, end = match.start(), match.end()
            self._match = svalue[start: end]
            self._start, self._end = start, end
        else:
            self.matched = False

    def __str__(self) -> str:
        if self.matched:
            return f"<Cell value={self.value!r} matched={self._match!r}>"
        else:
            return f"<Cell value={self.value!r} matched=False>"

    def format(self, missing: str | None, color: str | None) -> str:
        value = str(self.value)
        if self.matched:
            return (
                value[:self._start] +
                (f"[{color}]" if color else "") +
                self._match +
                (f"[/{color}]" if color else "") +
                value[self._end:]
            )
        else:
            return value if missing is None else missing
