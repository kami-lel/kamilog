# kamilog Installation Guide

Choose the method that fits your project:

| method | best for |
|---|---|
| [Package Install → From GitHub](#from-github) | using kamilog as a dependency |
| [Package Install → Local](#local-development) | developing or patching kamilog itself |
| [Copy Install → As Script](#as-script) | zero-dependency single-file embed |
| [Copy Install → As Module](#as-module) | embedding the full package into a project |














## Package Install

Install kamilog as a package via `pip`. After installing, import anywhere:

```python
import kamilog
```





### From GitHub

```bash
pip install git+https://github.com/kami-lel/kamilog.git
```





### Local Development

Clone the repository, then install into the current environment:

```bash
git clone https://github.com/kami-lel/kamilog.git
cd kamilog
pip install -e .
```

Use `-e` (editable mode) so local edits take effect without reinstalling.













## Copy Install

Embed kamilog directly into your project with no pip dependency.





### As Script

Copy the single file `kamilog/kamilog.py` into your project root:

```
your_project/
├── kamilog.py
└── main.py
```

```python
import kamilog
```





### As Module

Copy the entire `kamilog/` folder into your project's source directory:

```
your_project/
├── project_abc/
│   ├── kamilog/
│   │   ├── __init__.py
│   │   └── kamilog.py
│   ├── module_a/
│   └── module_b/
└── pyproject.toml
```

```python
from project_abc import kamilog
```
