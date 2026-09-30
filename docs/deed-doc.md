# Deeds Documentation

A **deed** is one common thing your program does, such as creating, copying, or deleting a file. Each deed has its own logger method that logs it in a fixed wording.

kamilog only reports deeds. Your code still does the work.













## Usage

```python
import kamilog

logger = kamilog.getLogger("copy")

logger.cp_file("a.txt", "backup/a.txt")
logger.rm_file("tmp/a.txt")
```

```text
INFO  copy: copy a.txt -> backup/a.txt
WARN. copy: delete tmp/a.txt
```

Log two deeds with two calls. Every deed method takes these arguments:

| Argument | Meaning |
| --- | --- |
| `*args` | the deed's own arguments |
| `level` | severity of the success line |
| `err_level` | (only track form) severity of the failure line |
| `suppress` | (only track form) `True` logs the failure and lets the program carry on |
| `badges` | extra [badges](badge-doc.md) for this line |
| `is_inheriting_badges` | whether this line also carries the logger's [badges](badge-doc.md) |













## Deeds

Each deed logs one fixed line. Pass its args positionally, in the order shown below.
The remark is the text that appears in the log.

| Deed | Args | Remark |
| --- | --- | --- |
| `create_file` | path | `create {path}` |
| `owr_file` | path | `overwrite {path}` |
| `append_file` | path | `append {path}` |
| `cp_file` | source, destination | `copy {source} -> {destination}` |
| `mv_file` | source, destination | `move {source} -> {destination}` |
| `chmod_file` | path, mode | `chmod {path} {mode}` |
| `rm_file` | path | `delete {path}` |
| `create_dir` | path | `create dir {path}` |
| `rm_dir` | path | `delete dir {path}` |
| `pack_files` | source, archive | `pack {source} -> {archive}` |
| `unpack_archive` | archive, destination | `unpack {archive} -> {destination}` |
| `download` | url, destination | `download {url} -> {destination}` |
| `upload` | source, url | `upload {source} -> {url}` |
| `run_command` | command | `run {command}` |
| `load_config` | path | `load {path}` |
| `save_config` | path | `save {path}` |
| `skip_file` | path | `skip {path}` |

Pass `chmod_file`'s mode as a string, such as `"755"` or `"+x"`: kamilog prints it as given, so an integer like `0o755` would show as `493`.

Every arg goes through `str()` once, when the deed is called or when `act.set` gives it. The line then keeps that text, even if the object changes before the block ends. `None` counts as omitted.

A deed logs at `WARNING` when it is destructive, and at `INFO` or `SKIP` otherwise.
A failed deed logs at `ERROR`, or at `WARNING` when the run can safely go on.

| Deed | Level | Error Level |
| --- | --- | --- |
| `create_file` | `INFO` | `ERROR` |
| `owr_file` | `WARNING` | `ERROR` |
| `append_file` | `INFO` | `ERROR` |
| `cp_file` | `INFO` | `ERROR` |
| `mv_file` | `INFO` | `ERROR` |
| `chmod_file` | `INFO` | `ERROR` |
| `rm_file` | `WARNING` | `WARNING` |
| `create_dir` | `INFO` | `ERROR` |
| `rm_dir` | `WARNING` | `WARNING` |
| `pack_files` | `INFO` | `ERROR` |
| `unpack_archive` | `INFO` | `ERROR` |
| `download` | `INFO` | `ERROR` |
| `upload` | `INFO` | `ERROR` |
| `run_command` | `INFO` | `ERROR` |
| `load_config` | `INFO` | `ERROR` |
| `save_config` | `INFO` | `ERROR` |
| `skip_file` | `SKIP` | `WARNING` |













## Failure Handling

Wrap the deed in `with logger.track.<method>(...)`. One line is logged when the block ends: the success line, or, if the block raised, a `fail to ...` line with the error and traceback. The error still propagates.

```python
import shutil

def back_up(src, dst):
    with logger.track.cp_file(src, dst):
        shutil.copy2(src, dst)
```

```text
INFO  backup: copy a.txt -> backup/a.txt
ERROR backup: fail to copy a.txt -> /root/a.txt: PermissionError: [Errno 13] Permission denied: '/root/a.txt'
```

Keep the block around the single deed, not a whole script.

- Recover: `suppress=True` logs the failure and lets the program carry on.
- Late Value: `act.set(destination=name)` supplies an argument known only after the deed starts.
- Failure without an Exception: `act.fail("reason")` marks the deed failed, for a command exit status or a bad HTTP status.

```python
with logger.track.download(url) as act:
    act.set(destination=fetch_to_named_file(url))

with logger.track.run_command("make") as act:
    proc = subprocess.run(["make"])
    if proc.returncode:
        act.fail("exit {}".format(proc.returncode))
```













## Shell CLI

Shell scripts use `kamilog deed <method>`, with the name in kebab case and the same arguments. The options are `--level` and `--err-level`.

```bash
kamilog deed create-file out/a.txt
kamilog deed cp-file a.txt backup/a.txt
kamilog deed cp-file a.txt backup/a.txt -- cp a.txt backup/a.txt
kamilog deed run-command -- make
```

Add `--` and a command to run it and log the outcome: exit status 0 logs success, anything else logs a failure, and the status is passed back to your shell.
