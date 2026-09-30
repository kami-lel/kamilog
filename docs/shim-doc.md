# `kamilog_shim` Documentation

[`scripts/kamilog_shim.sh`](../scripts/kamilog_shim.sh) lets a shell script
call `kamilog` safely, even where it is not installed. Either **copy-paste**
the shim into your script, or `source` it:

```bash
source /path/to/kamilog_shim.sh

echo "hello" | kamilog
```

When `kamilog` is on `PATH`, calls are forwarded to it unchanged. Otherwise
the subcommand is not run, and piped stdin is printed with a simple fallback:

| Command | Fallback output |
|---|---|
| `kamilog cb ...` / `kamilog cb0 ...` | stdin, prefixed with `# ` |
| `kamilog logger <tag>` | stdin, prefixed with `<tag>:` and a tab |
| anything else | stdin, unchanged |

> [!NOTE]
> The prefix is added once, at the start of the piped text, not on every line.
