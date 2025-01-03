from ggrep.cell import Cell


class Col:
    def __init__(self, index: int, invert: bool):
        self.index = index
        self.invert = invert
        self.numeric = True
        self.cells = []

    def __iter__(self):
        return iter(self.cells)

    @property
    def matched(self):
        if self.invert:
            return not any(cell.matched for cell in self)
        else:
            return any(cell.matched for cell in self)

    def append(self, cell: Cell) -> None:
        self.cells.append(cell)
        if not isinstance(cell.value, (float, int)):
            self.numeric = False
