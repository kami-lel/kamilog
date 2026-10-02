"""
diff-only compression: replace text shared with recent messages by markers
"""

import logging
from collections import deque

from .tab_align import _TabAlignedLine, _expand_tabs


class _DiffOnlyEngine:  # ******************************************************
    """
    engine for diff-only compression of log message text


    :param formatter: formatter used to measure the prefix width and
            apply ``color_grey`` to compression markers
    :type formatter: _LogFormatter
    :param threshold: number of prior messages held for comparison
    :type threshold: int
    """

    _FALLBACK_TAB_SPAN = 2
    _COMPRESSION_MARKER = "〃\t"  # visual width matches one TAB_SIZE block
    _MARKER_CHAR = "〃"
    _MARKER_WIDTH = 2  # rendered columns of _MARKER_CHAR
    _LEADER_MARKER_MIN = 4  # leader shorter than this becomes bare "\t"
    _LONG_LINE_COLS = 100  # wider rendered lines drop tab alignment
    _LONG_LINE_MARKER = "〃 "  # full-block ditto on a long line

    def __init__(self, formatter, threshold=3):
        self._formatter = formatter
        # each entry: one message split into its lines
        self._history = deque(maxlen=threshold)
        # _common[k][i] = shared char at position i of line k across all
        # history, or None where messages diverge or lengths differ; a
        # line missing from any history message has an empty list
        self._common = []

    def _update_common(self):
        """
        recompute ``_common`` from the current ``_history`` messages
        """
        history = list(self._history)
        if not history:
            self._common = []
            return
        n_lines = max(len(lines) for lines in history)
        self._common = [
            (
                self._calc_line_common([lines[k] for lines in history])
                if all(k < len(lines) for lines in history)
                else []
            )
            for k in range(n_lines)
        ]

    @staticmethod
    def _calc_line_common(texts):
        """
        :return: per-position shared char across ``texts``, ``None``
                where they diverge or lengths differ
        :rtype: list[str or None]
        """
        min_len = min(len(s) for s in texts)
        max_len = max(len(s) for s in texts)
        common = []
        for i in range(max_len):
            if i >= min_len:
                common.append(None)  # position missing in some texts
            else:
                ch = texts[0][i]
                common.append(
                    ch if all(s[i] == ch for s in texts[1:]) else None
                )
        return common

    @staticmethod
    def _is_word_char(ch):
        """
        :return: if ``ch`` is a word character (``0-9A-Za-z`` or ``-_``)
        :rtype: bool
        """
        return (ch.isascii() and ch.isalnum()) or ch in "-_"

    def _find_cut(self, message, run_s, run_e, prefix_len):
        """
        :return: cut index in ``[run_s, run_e]``, text before it replaceable
                and text from it kept printed; lands on the nearest non-word
                char scanning back from the run end, at most
                ``_FALLBACK_TAB_SPAN`` tab stops, else on that tab-aligned floor
        :rtype: int
        """
        block = _TabAlignedLine.TAB_SIZE
        col_e = prefix_len + run_e
        floor_col = (col_e // block - self._FALLBACK_TAB_SPAN) * block
        cut_min = max(run_s, floor_col - prefix_len)
        for b in range(run_e - 1, cut_min - 1, -1):
            if not self._is_word_char(message[b]):
                return b
        return cut_min

    def _compress(self, record, message):
        """
        compress ``message`` line by line against the matching history lines;
        only line 1 carries the record prefix, later lines start at column 0
        """
        prefix_len = self._formatter.engine.count_prefix_chars(record)
        lines = message.split("\n")
        return "\n".join(
            self._compress_line(
                line,
                self._common[k] if k < len(self._common) else [],
                prefix_len if k == 0 else 0,
            )
            for k, line in enumerate(lines)
        )

    @classmethod
    def _is_long_line(cls, line, prefix_len):
        """
        :return: if the rendered, uncompressed ``line`` starting at
                column ``prefix_len`` ends beyond ``_LONG_LINE_COLS``,
                embedded tabs expanded to tab stops
        :rtype: bool
        """
        return prefix_len + len(_expand_tabs(line, prefix_len)) > (
            cls._LONG_LINE_COLS
        )

    def _compress_line(self, message, common, prefix_len):
        """
        compress positions of one line matching ``common`` into ``〃\\t``
        markers; the replaceable span (``run_s`` to ``cut``) is split into
        ``_TabAlignedLine`` blocks anchored at its absolute column, so a short
        leading block (if any) is the leader, a short trailing block (if any)
        is the gap, and everything between is a whole replaceable tab stop
        """
        n_common = len(common)
        is_common = [
            i < n_common and common[i] is not None and common[i] == ch
            for i, ch in enumerate(message)
        ]
        is_long = self._is_long_line(message, prefix_len)
        result = []
        i = 0
        msg_len = len(message)
        while i < msg_len:
            if not is_common[i]:
                result.append(message[i])
                i += 1
            else:
                run_s = i
                while i < msg_len and is_common[i]:
                    i += 1
                result.append(
                    self._render_run(message, run_s, i, prefix_len, is_long)
                )
        return "".join(result)

    def _render_run(self, message, run_s, run_e, prefix_len, is_long):
        """
        render one common run as markers plus its kept tail;
        ``is_long`` flags a line wider than ``_LONG_LINE_COLS``
        """
        block = _TabAlignedLine.TAB_SIZE
        grey = self._formatter.palette.color_grey
        cut = self._find_cut(message, run_s, run_e, prefix_len)

        tal_blocks = list(
            _TabAlignedLine.parse(
                message[run_s:cut], start_offset=prefix_len + run_s
            )
        )
        leader = ""
        if tal_blocks and len(tal_blocks[0]) < block:
            leader = tal_blocks.pop(0)
        if tal_blocks and len(tal_blocks[-1]) < block:
            gap_block = tal_blocks.pop()
        else:
            gap_block = ""
        k = len(tal_blocks)  # remaining blocks are all full-width

        if k == 0:
            return message[run_s:run_e]
        result = []
        gap = len(gap_block)
        block_marker = (
            self._LONG_LINE_MARKER if is_long else self._COMPRESSION_MARKER
        )
        # leader: common chars before the first tab stop are never
        # printed; short ones become a bare tab jump, longer ones earn
        # their own marker; a long line has no tab stops to jump to
        if len(leader) >= self._LEADER_MARKER_MIN:
            result.append(grey(block_marker))
        elif leader and not is_long:
            result.append("\t")
        result.append(grey(block_marker * k))
        # partial block: marker + spaces padding to the cut; a long line
        # keeps the marker and its one space, no padding
        if gap >= self._MARKER_WIDTH:
            if is_long:
                result.append(grey(block_marker))
            else:
                result.append(grey(self._MARKER_CHAR))
                result.append(" " * (gap - self._MARKER_WIDTH))
        elif not is_long:
            result.append(" " * gap)
        result.append(message[cut:run_e])
        return "".join(result)

    def process(self, record):
        """
        :return: message of the record compressed against history; unchanged
                during warmup
        :rtype: str
        """
        message = record.getMessage()

        if len(self._history) == self._history.maxlen:
            masked = self._compress(record, message)
        else:
            masked = message

        self._history.append(message.split("\n"))
        self._update_common()
        return masked


class _DiffOnlyMsgFilter(logging.Filter):  # ***********************************
    """
    ``logging.Filter`` adapter that applies ``_DiffOnlyEngine`` to records


    :param formatter: forwarded to ``_DiffOnlyEngine`` for prefix-width
            measurement; pass ``None`` to disable prefix alignment
    :type formatter: _LogFormatter or None
    :param threshold: forwarded to ``_DiffOnlyEngine`` as the history
            depth before compression activates
    :type threshold: int
    :param disable_diff_only_compression: whether turn off diff-ony compression
            and pass records through untouched
    :type disable_diff_only_compression: bool
    """

    def __init__(
        self, formatter, threshold=3, *, disable_diff_only_compression=False
    ):
        super().__init__()
        self._engine = (
            None
            if disable_diff_only_compression
            else _DiffOnlyEngine(formatter, threshold)
        )

    def filter(self, record):
        """
        :return: always ``True``; the filter compresses ``record.msg`` in place
                and never drops records
        :rtype: bool
        """
        if self._engine is None:  # compression disabled, pass through
            return True
        record.msg = self._engine.process(record)
        record.args = ()
        return True
