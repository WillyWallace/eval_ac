# Releasing (maintainers)

Releases are published to [PyPI](https://pypi.org/p/eval-ac) by the GitHub workflow `.github/workflows/publish.yml` with [trusted publishing](https://docs.pypi.org/trusted-publishers/): PyPI trusts the workflow of this repository, no password or API token is stored.

## One-time setup

1. **PyPI:** log in at <https://pypi.org> (two-factor authentication is required), open *Your account → Publishing* and add a **pending publisher**:

   | Field | Value |
   | --- | --- |
   | PyPI project name | `eval-ac` |
   | Owner | `WillyWallace` |
   | Repository name | `eval_ac` |
   | Workflow name | `publish.yml` |
   | Environment name | `pypi` |

2. **TestPyPI:** the same at <https://test.pypi.org> (separate account) with the environment name `testpypi`.
3. **GitHub:** *Settings → Environments* → create the environments `pypi` and `testpypi`. For `pypi`, *Required reviewers* (yourself) is recommended: every upload to PyPI then has to be confirmed in the Actions tab.

## Test upload to TestPyPI

*Actions → Publish → Run workflow* builds the package and uploads it to TestPyPI. Check the result:

```sh
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ eval-ac
eval-ac --version
```

Each version can be uploaded to TestPyPI (and to PyPI) only once. For a second test upload, increase the version, e.g. `0.3.1.dev1`.

## Release

1. Set the version in `eval_ac/__init__.py` (e.g. `__version__ = "0.4.0"`).
2. In `CHANGELOG.md`, rename *Unreleased* to the version and date.
3. Merge into `main`.
4. On GitHub: *Releases → Draft a new release*, tag **`v` + version** (e.g. `v0.4.0`) on `main`, paste the changelog section as description, *Publish release*.

The workflow checks that the tag matches the package version, builds sdist and wheel, checks them with `twine check` and uploads them to PyPI. Read the Docs builds the documentation of the tag automatically.

Versions follow [semantic versioning](https://semver.org): until 1.0 the interface may still change between minor versions.
