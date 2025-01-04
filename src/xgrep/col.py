from xgrep.cell import Cell
from xgrep.row import Row


class Col(Row):
    def __init__(self, index: int, invert: bool):
        super().__init__(index, invert)
        self.numeric = True

    def append(self, cell: Cell) -> None:
        super().append(cell)
        if not isinstance(cell.value, (float, int)):
            self.numeric = False
