"""
comment banners: padded single lines and boxed multi-line (CB0) banners
"""

import sys

from .ansi import AnsiRenderer


# Comment Banner  ##############################################################


_CONTENT_SPACING = "  "
_PADDING_MAP = {1: "#", 2: "=", 3: "*", 4: "+", 5: "-"}


def _resolve_padding_preset(padding):
    """
    :raises ValueError: ``padding`` is an int outside 1~5
    :return: padding char for preset ``padding`` (1~5); any other
            ``padding`` unchanged
    :rtype: str
    """
    if not isinstance(padding, int):
        return padding
    if padding not in _PADDING_MAP:
        raise ValueError("param padding int must be 1~5")
    return _PADDING_MAP[padding]


def _check_banner_content(content, line_width):
    """
    raise ``ValueError`` unless ``content`` is one line fitting ``line_width``
    """
    if "\n" in content:
        raise ValueError("param content must be a single line")
    if len(content) > line_width:
        raise ValueError(
            "param content length {} exceeds line_width {}".format(
                len(content), line_width
            )
        )


def _check_padding_char(padding):
    """
    raise ``ValueError`` unless ``padding`` is one printable non-space char
    """
    if len(padding) != 1:
        raise ValueError("param padding must be a single character")
    if not padding.isprintable() or padding == " ":
        raise ValueError("param padding must be a normal printable character")


def _grey_fill(renderer, padding, n):
    """
    :return: ``padding`` repeated ``n`` times, colored grey
    :rtype: str
    """
    return renderer.color_grey(padding * n)


def _resolve_renderer(renderer, file):
    """
    :return: ``renderer``, or a new one for ``file`` when ``None``
    :rtype: AnsiRenderer
    """
    return AnsiRenderer(file) if renderer is None else renderer


def _gen_comment_banner_generic(
    mode,
    content,
    padding,
    *,
    line_width=80,
    horizontal_offset=0,
    file=sys.stdout,
    renderer=None,
):
    """
    return ``content`` padded to ``line_width``, aligned per ``mode``:
    ``"c"`` centered, ``"l"`` left-justified, ``"r"`` right-justified
    """
    padding = _resolve_padding_preset(padding)
    _check_banner_content(content, line_width)
    _check_padding_char(padding)
    renderer = _resolve_renderer(renderer, file)

    if mode in ("l", "r"):
        remaining = line_width - len(content) - len(_CONTENT_SPACING)
        fill = _grey_fill(renderer, padding, remaining)
        if mode == "l":
            return content + _CONTENT_SPACING + fill
        return fill + _CONTENT_SPACING + content

    # centered; horizontal_offset shifts content: -1 left, +1 right
    remaining = line_width - len(content) - len(_CONTENT_SPACING) * 2
    left = remaining // 2 + horizontal_offset
    right = remaining - left
    if left < 0 or right < 0:
        raise ValueError("param horizontal_offset out of range")
    return (
        _grey_fill(renderer, padding, left)
        + _CONTENT_SPACING
        + content
        + _CONTENT_SPACING
        + _grey_fill(renderer, padding, right)
    )


# Comment Banner Public API  ===================================================


def gen_comment_banner_centered(*args, **kwargs):
    """
    generate a line with ``content`` centered,
    filling both sides with ``padding`` to reach ``line_width``

    when the remaining width is odd, the extra character goes to the right


    :param content: text to pad; must be a single, non-empty line no
            longer than ``line_width``
    :type content: str
    :param padding: single printable non-space fill character, or int 1-5
            (1: #, 2: =, 3: *, 4: +, 5: -)
    :type padding: str or int
    :param line_width: total output width; default=80
    :type line_width: int, optional
    :param horizontal_offset: nudge the centered content sideways by this
            many columns; negative shifts left, positive shifts right;
            default=0
    :type horizontal_offset: int, optional
    :param file: output stream, used only for ANSI TTY detection;
            default=``sys.stdout``
    :type file: IO, optional
    :param renderer: ANSI color renderer;
            if ``None``, created from ``file`` argument; default=None
    :type renderer: AnsiRenderer or None, optional
    :raises ValueError: ``content`` contains ``"\\n"`` or exceeds
            ``line_width``
    :raises ValueError: ``padding`` is not exactly one printable non-space
            character, or is an int outside 1-5
    :raises ValueError: ``horizontal_offset`` pushes either fill side below
            zero
    :return: padded line content
    :rtype: str
    :example:
    >>> gen_comment_banner_centered("hi", "=", line_width=20)
    '=======  hi  ======='
    >>> gen_comment_banner_centered(
    ...     "hi", "=", line_width=20, horizontal_offset=2
    ... )
    '=========  hi  ====='
    >>> gen_comment_banner_centered("hi", 2, line_width=20)
    '=======  hi  ======='
    """
    return _gen_comment_banner_generic("c", *args, **kwargs)


def gen_comment_banner_left_just(*args, **kwargs):
    """
    generate a line with ``content`` left-justified,
    filling the right with ``padding``

    see :func:`gen_comment_banner_centered` for parameter and error
    details


    :return: padded line content
    :rtype: str
    :example:
    >>> gen_comment_banner_left_just("hi", "=", line_width=20)
    'hi  ================'
    >>> gen_comment_banner_left_just("hi", 2, line_width=20)
    'hi  ================'
    """
    return _gen_comment_banner_generic("l", *args, **kwargs)


def gen_comment_banner_right_just(*args, **kwargs):
    """
    generate a line with ``content`` right-justified,
    filling the left with ``padding``

    see :func:`gen_comment_banner_centered` for parameter and error
    details


    :return: padded line content
    :rtype: str
    :example:
    >>> gen_comment_banner_right_just("hi", "=", line_width=20)
    '================  hi'
    >>> gen_comment_banner_right_just("hi", 2, line_width=20)
    '================  hi'
    """
    return _gen_comment_banner_generic("r", *args, **kwargs)


def gen_comment_banner_zero(
    lines, *, line_width=80, file=sys.stdout, renderer=None
):
    """
    generate a multi-line boxed comment banner (CB0)

    wraps each line with `# `, framed by top and bottom `#` rulers


    :param lines: lines to include in the banner
    :type lines: iterable of str
    :param line_width: total output width; default=80
    :type line_width: int, optional
    :param file: output stream, used only for ANSI TTY detection;
            default=``sys.stdout``
    :type file: IO, optional
    :param renderer: ANSI color renderer;
            if ``None``, created from ``file`` argument; default=None
    :type renderer: AnsiRenderer or None, optional
    :raises ValueError: any line contains ``"\\n"`` or exceeds
            ``line_width - 2`` (reserved for `# ` prefix)
    :return: multi-line boxed banner as a string
    :rtype: str
    :example:
    >>> gen_comment_banner_zero(["line 1", "line 2"], line_width=20)
    ####################
    # line 1
    # line 2
    ####################
    """
    renderer = _resolve_renderer(renderer, file)

    ruler = renderer.color_grey("#" * line_width)
    formatted_lines = [ruler]

    for line in lines:
        if "\n" in line:
            raise ValueError("param lines must not contain newlines")
        if len(line) > line_width - 2:
            raise ValueError(
                "param line length {} exceeds line_width - 2 {}".format(
                    len(line), line_width - 2
                )
            )
        formatted_lines.append(renderer.color_grey("# ") + line)

    formatted_lines.append(ruler)
    return "\n".join(formatted_lines)
