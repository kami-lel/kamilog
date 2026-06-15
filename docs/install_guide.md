# kamilog Installation Guide

## Installation as Script

Copy the single script `./kamilog/kamilog.py` into your project folder.

Example directory structure:

```
your_project/
├── kamilog.py
└── main.py
```

In `main.py`, import the module as follows:

```python
import kamilog
```

## Installation as Module

Copy the entire `kamilog` folder into your project's source folder.

Example directory structure:

```
your_project/
├── project_abc/
│   ├── kamilog/
│   │   ├── __init__.py
│   │   └── kamilog.py
│   ├── module_a/
│   │   └── some_code.py
│   └── module_b/
│       └── other_code.py
└── setup.py
```

Then import `kamilog` anywhere within the project:

```python
from project_abc import kamilog
```
