from ggrep.cell import Cell


class Col:
    def __init__(self, index: int):
        self.index = index
        self.matched = False
        self.numeric = False
        self.cells = []

    def __iter__(self):
        return iter(self.cells)

    def append(self, cell: Cell) -> None:
        self.cells.append(cell)
        if cell.matched:
            self.matched = True
