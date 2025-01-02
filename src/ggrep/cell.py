import re


class Cell:
    def __init__(self, value: str, pattern: re.Pattern):
        self.value = value
        self.matched = pattern.search(value)

    def format(self, missing: str | None, color: str | None) -> str:
        if self.matched:
            start, end = self.matched.start(), self.matched.end()
            return (
                self.value[:start] +
                (f"[{color}]" if color else "") +
                self.value[start: end] +
                (f"[/{color}]" if color else "") +
                self.value[end:]
            )
        else:
            if missing is None:
                return self.value
            else:
                return missing
