# Comment Banner Documentation

Three functions return fixed-width lines padded with a fill character: `gen_comment_banner_centered`, `gen_comment_banner_left_just`, `gen_comment_banner_right_just`. A two-space separator is always placed between content and fill. Print the result yourself. Colors come from the [ANSI renderer](ansi-doc.md), and the same banners are available in shell scripts through `kamilog cb` (see the [shell shim](shim-doc.md) for machines without `kamilog`):

```python
import kamilog

print(kamilog.gen_comment_banner_centered("hello", "="))
print(kamilog.gen_comment_banner_left_just("hello", "="))
print(kamilog.gen_comment_banner_right_just("hello", "="))
```













## Padding

The `padding` parameter accepts either a string (single character) or an integer (1-5):

| padding | character |
|---|---|
| `"#"` or `1` | `#` |
| `"="` or `2` | `=` |
| `"*"` or `3` | `*` |
| `"+"` or `4` | `+` |
| `"-"` or `5` | `-` |

```python
# String padding
print(kamilog.gen_comment_banner_centered("release", "="))

# Integer padding (shorter to type)
print(kamilog.gen_comment_banner_centered("release", 2))
```













## Renderer Reuse

All three functions accept `line_width` (default `80`), `file` (used only for ANSI TTY detection; defaults to `sys.stdout`), and an optional `renderer` kwarg. If you call any of them repeatedly, construct one `AnsiRenderer` up front and pass it in — this avoids re-detecting TTY state on every call:

```python
renderer = kamilog.AnsiRenderer(sys.stdout)
print(kamilog.gen_comment_banner_centered("section", 1, renderer=renderer))
print(kamilog.gen_comment_banner_centered("subsection", 5, renderer=renderer))

# custom width
print(kamilog.gen_comment_banner_centered("title", 3, line_width=40))
```













## Horizontal Offset

`gen_comment_banner_centered` accepts `horizontal_offset` (default `0`) to nudge the centered content sideways — negative shifts it left, positive shifts it right. This keeps a centered title aligned when the banner is printed after a left-hand prefix: shrink `line_width` by the prefix width and offset by half of it.

```python
# bare centered banner across the full width
print(kamilog.gen_comment_banner_centered("results", "="))

# 8-char prefix; width drops by 8, offset -4 realigns the title
print("phase 2 " + kamilog.gen_comment_banner_centered(
    "results", "=", line_width=72, horizontal_offset=-4
))
```

The offset applies only to centered banners; the left- and right-justified functions ignore it.













## Validation

All three raise `ValueError` when:
- `content` contains a newline
- `len(content)` exceeds `line_width`
- `padding` (string) is not exactly one printable non-space character
- `padding` (int) is not in range 1-5

`gen_comment_banner_centered` additionally raises when `horizontal_offset` pushes either fill side below zero.
