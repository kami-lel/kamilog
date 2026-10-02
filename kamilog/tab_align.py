"""
tab-stop alignment helpers shared by the log formatter and the diff-only filter
"""


def _calc_tab_advance(col):
    """
    :return: columns from ``col`` to the next tab stop, a full
            ``TAB_SIZE`` when ``col`` already sits on one
    :rtype: int
    """
    return _TabAlignedLine.TAB_SIZE - col % _TabAlignedLine.TAB_SIZE


def _expand_tabs(line, start_offset):
    """
    :return: ``line`` with each tab replaced by spaces up to the next
            tab stop, ``line`` beginning at column ``start_offset``
    :rtype: str
    """
    expanded = []
    col = start_offset
    for ch in line:
        if ch == "\t":
            n_spaces = _calc_tab_advance(col)
            expanded.append(" " * n_spaces)
            col += n_spaces
        else:
            expanded.append(ch)
            col += 1
    return "".join(expanded)


class _TabAlignedLine(list):  # ************************************************
    """
    a line of text split into tab-stop-aligned string blocks
    """

    TAB_SIZE = 8

    @classmethod
    def parse(cls, line, *, start_offset=0):  # ++++++++++++++++++++++++++++++++
        """
        split a regular text line into ``TAB_SIZE``-wide blocks; the first is
        shortened by ``start_offset`` so later ones land on ``TAB_SIZE`` column
        boundaries, the last holds the remainder, and literal tabs in ``line``
        are expanded first
        """
        line = _expand_tabs(line, start_offset)

        # split blocks  --------------------------------------------------------
        n = len(line)
        blocks = []

        first_len = min(_calc_tab_advance(start_offset), n)
        pos = first_len
        blocks.append(line[:pos])

        while pos < n:
            end = min(pos + cls.TAB_SIZE, n)
            blocks.append(line[pos:end])
            pos = end

        return cls(blocks, start_offset=start_offset)

    def __init__(self, blocks, *, start_offset=0):
        super().__init__(blocks)
        self.start_offset = start_offset

    def render(self, *, insert_prefix=False, prefix_symbol=" "):
        """
        :return: the blocks joined into one line, ``start_offset`` copies of
                ``prefix_symbol`` prepended when ``insert_prefix``
        :rtype: str
        """
        line = "".join(self)
        if insert_prefix:
            return prefix_symbol * self.start_offset + line
        return line

    def __str__(self):
        return self.render()
