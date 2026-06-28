# kamilog Installation Guide

choose the method that fits your project:

| method | best for |
|---|---|
| [Package Install → From GitHub](#from-github) | using kamilog as a dependency |
| [Package Install → Local Development](#local-development) | developing or patching kamilog itself |
| [Copy Install → As Script](#as-script) | zero-dependency single-file embed |
| [Copy Install → As Module](#as-module) | embedding the full package into a project |













## Package Install

install kamilog via `pip`. After either method below, import with:

```python
import kamilog
```





### From GitHub

```bash
pip install git+https://github.com/kami-lel/kamilog.git
```





### Local Development

clone the repository:

```bash
git clone https://github.com/kami-lel/kamilog.git
```

Install:

```bash
cd kamilog
pip install .
```













## Copy Install

embed kamilog directly into your project — no `pip` required.





### As Script

copy the single file into your project root:

```
your_project/
├── kamilog.py
└── main.py
```

import:

```python
import kamilog
```





### As Module

copy the entire folder into your project's source directory:

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

import:

```python
from project_abc import kamilog
```
