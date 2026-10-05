# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.2.0] - 2026-10-05

### Added
- Command line interface `eval-ac` (also `python -m eval_ac`):
  `eval-ac ABSCAL.HIS --netcdf abscal.nc --plot results_ln2_cal.png`.
  Options `--no-plot`, `--show` and `--version`. Errors (missing file,
  invalid file) are reported as one line on stderr with exit code 1.
- Functional API: `read_abscal_his()`, `write_netcdf()`, `read_raw()`,
  `records_to_dataset()` in `eval_ac.convert_abscal_his` and
  `plot_calibration_history()` in the new module `eval_ac.plotting`.
- Coordinate `time` (datetime of each calibration, decoded from
  `time_of_rec_1`, seconds since 2001-01-01).
- Coordinate `receiver` (1 or 2) along `freq`, derived from the channel
  numbers stored in the file.
- Validation of the input file: file code (39583209), length of every
  record, truncated files, and identical channels in all entries.
- Tests (pytest) for reader, NetCDF output, plotting and CLI, including a
  regression test against the output of version 0.1.0
  (`example_data/abscal.nc`).
- `pyproject.toml` with the entry point `eval-ac` and the extras `test`
  and `dev`.
- `CHANGELOG.md`.

### Changed
- `HatproBinAbscalHis(filename, filename_out=None)`: the NetCDF file is
  only written if `filename_out` is given. Before, the output file was
  mandatory.
- `HatproBinAbscalHis.header` now holds plain integers
  (`{'file_code': 39583209, 'n_samples': 16}`) instead of numpy arrays, and
  the key `_n_samples` is renamed to `n_samples`. `HatproBinAbscalHis.data`
  is now a list with one dictionary per calibration entry.
- The reader reads the file once into memory and parses it with explicit
  little-endian types instead of calling `np.fromfile` for every value.
  The values are identical to version 0.1.0 (checked by a test).
- Plot: the split into the two receivers is taken from the file instead of
  fixed channel indices 0-6 / 7-13. The plot works for any number of
  calibration entries (before, at least four were needed). The legend shows
  the dates of the latest and previous calibration, the axes are labelled
  with name and unit.
- `evaluate_absolute_calibration.py` no longer contains hard coded paths
  and no longer runs on import. It now calls the CLI, i.e.
  `python eval_ac/evaluate_absolute_calibration.py ABSCAL.HIS`.
- Global NetCDF attributes follow CF/ACDD names: `Conventions` (was
  `conventions`), `date_created` in ISO 8601 (was `date of creation`), new
  `title`. `history` contains time stamp, source file and eval_ac version.
  The empty attribute `comments` was removed.
- CI: tests and a CLI run are executed on every push/PR, Python 3.9-3.12,
  `actions/checkout@v4` and `actions/setup-python@v5`. Pylint checks
  `eval_ac` and `tests`.
- Minimum Python version is 3.9 (was 3.8; Python 3.8 is end of life).
- The example plot moved to `docs/images/results_ln2_cal.png`.

### Fixed
- The test called the class with one argument although two were required
  and depended on the working directory; it was not run in CI.
- `long_name` of `cold_load_temp_1/2` said "hot load".
- Invalid CF `standard_name` "reveiver gain" of `gain` removed.
- Unit of the non-linearity factor `alpha` changed from `K` to `1`
  (dimensionless, values around 0.97). Please verify with the RPG manual.
- Typo "micorwave" in the `source` attribute.
- `datetime.utcnow()` (deprecated since Python 3.12) replaced.
- `datetime` removed from the dependencies (it is part of the standard
  library); `netCDF4` added (needed to write NetCDF files).
- Version numbers were inconsistent (`setup.py`: 1.0, `__init__.py`:
  0.1.0); the version is now only defined in `eval_ac/__init__.py`.
- README: download badge pointed to a foreign repository.

### Removed
- `setup.py` (replaced by `pyproject.toml`). Install with `pip install .`
  instead of `python setup.py install`.
- Duplicate `results_ln2_cal.png` in the repository root and in the
  package directory.

### Migration from 0.1.0
| 0.1.0 | 0.2.0 |
| --- | --- |
| edit paths in `evaluate_absolute_calibration.py`, run it | `eval-ac ABSCAL.HIS --netcdf abscal.nc` |
| `python setup.py install` | `pip install .` |
| `HatproBinAbscalHis(f_in, f_out).xrdata` | `read_abscal_his(f_in)` (+ `write_netcdf(ds, f_out)`) |
| `obj.header['_n_samples'][0]` | `obj.header['n_samples']` |
| `ds.attrs['conventions']` | `ds.attrs['Conventions']` |

The distribution name changed from `evaluation-of-absolute-calibration-results`
to `eval-ac`; the import name `eval_ac` is unchanged.

## [0.1.0]

- First version: reading of ABSCAL.HIS, conversion to NetCDF and plot of
  the calibration history.
