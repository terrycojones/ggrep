def int_to_excel_column(column_num: int) -> str:
    assert column_num > 0
    # From https://blog.finxter.com/converting-integer-to-excel-column-name-in-python/
    column_chars = []
    while column_num > 0:
        column_num, remainder = divmod(column_num - 1, 26)
        column_chars.append(chr(65 + remainder))
    return "".join(reversed(column_chars))
