# Installation

```{include} ../README.md
:start-after: <!-- docs-installation-start -->
:end-before: <!-- docs-installation-end -->
```

## Running the tests

```{include} ../README.md
:start-after: <!-- docs-tests-start -->
:end-before: <!-- docs-tests-end -->
```

## Building this documentation

```sh
pip install -e ".[docs]"
sphinx-build -W -b html docs docs/_build/html
```
