# ANSI Colored Output Documentation

`AnsiStyle` and `AnsiRenderer` provide TTY-aware color application independent of logging. The logger uses the same colors for its levels, listed in the [logging documentation](log-doc.md#custom-log-levels), and the [comment banners](banner-doc.md) accept an `AnsiRenderer` too.

```python
import sys
import kamilog

renderer = kamilog.AnsiRenderer(sys.stdout)
S = kamilog.AnsiStyle

# apply a named color
print(renderer.color("hello", S.CYAN))

# combine flags with `|` — foreground, background, bold, underline
print(renderer.color("hello", S.BOLD | S.GREEN | S.BG_BLUE))

# apply grey (used internally for timestamps and source labels)
print(renderer.color_grey("muted text"))

# color a triage tag, hue picked by tag type (BUG/FIXME/TODO/HACK)
print(renderer.color_triage_tag("TODO"))
```

`AnsiRenderer` detects TTY status once at construction. When `stream` is not a TTY (e.g. piped output), all methods return their input unchanged — no escape codes are emitted.

`AnsiStyle` is a combinable `Flag` enum. Foreground members: `RED`, `BRIGHT_RED`, `YELLOW`, `BRIGHT_YELLOW`, `GREEN`, `BRIGHT_GREEN`, `CYAN`, `BRIGHT_CYAN`, `BLUE`, `BRIGHT_BLUE`, `MAGENTA`, `BRIGHT_MAGENTA`, `BLACK`, `GREY`, `WHITE`, `BRIGHT_WHITE`. Each has a `BG_`-prefixed background counterpart (e.g. `BG_RED`, `BG_BRIGHT_CYAN`). Style members: `BOLD`, `UNDERLINE`.

`color_triage_tag(triage_tag)` colors any of the 12 triage-tag strings — `BUG`/`Bug`/`bug`, `FIXME`/`Fixme`/`fixme`, `TODO`/`Todo`/`todo`, `HACK`/`Hack`/`hack` — using one hue per tag type, with contrast escalating for louder (more-capitalized) tiers. Raises `ValueError` for any other string.
