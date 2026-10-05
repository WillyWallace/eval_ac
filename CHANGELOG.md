# Changelog

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [0.3.0] - 2026-10-05

### Added
- Selection of the calibration type: by default only calibrations with
  liquid nitrogen (`cal_type` = 1) are plotted and analysed. Entries in
  which no receiver was calibrated with liquid nitrogen are removed; if
  only one receiver was, the values of the other receiver are set to NaN.
  CLI option `--all-cal-types` disables the selection. Python:
  `eval_ac.analysis.select_cal_type()`.
- Quality flags: channels with `calibration_flag` = 0 (not calibrated) are
  marked with a red cross in the history plot, excluded from the drift
  analysis and listed in the report if they belong to the latest
  calibration. Python: `eval_ac.analysis.latest_not_calibrated()`.
- Drift analysis: the latest calibration of each receiver is compared with
  the median of the `N` calibrations before it (deviation in percent).
  Python: `eval_ac.analysis.calibration_drift()` and
  `eval_ac.analysis.drift_exceedances()`. Default thresholds: gain 10 %,
  noise diode temperature 2.5 %, system noise temperature 2.5 %,
  non-linearity factor 0.5 % (about the 99th percentile of the example
  data, adapt them to the instrument).
- Drift plot in the style of the history plot (`results_ln2_drift.png`),
  Python: `eval_ac.plotting.plot_drift()`.
- CLI options `-d/--drift-plot`, `--n-reference`, `-t/--threshold
  VARIABLE=PERCENT` (repeatable), `--max-age DAYS` and
  `--fail-on-warning` (exit code 2 if the report contains a warning).
- CLI prints a quality report of the latest calibration of each receiver:
  date and age, channels with flag 0, alpha out of range and drift.
- Age check: warning if the latest calibration of a receiver is older than
  183 days (RPG recommends an absolute calibration every 5 to 6 months,
  manual section 3.1.3). The age is computed from `time_of_rec_1/2` of the
  respective receiver. Python: `eval_ac.analysis.calibration_age()`.
- Range check of the non-linearity factor: warning if alpha of the latest
  calibration is outside 0.9 <= alpha < 1 (manual section 3.1.3.1).
  Python: `eval_ac.analysis.alpha_out_of_range()`.
- README section "Interpreting the results" based on the RPG manual
  (RPG-MWR-STD-SW): meaning and operational use of G, Tsys, Tn and alpha,
  typical patterns in the drift plot, what to do with a suspicious
  calibration, how to adapt the thresholds and limitations.
- Tests with modified copies of the example file (other calibration
  types, flag 0, time stamps, alpha); 47 tests in total. The tests do not
  depend on the current date.

### Changed
- History plot: latest and previous calibration are determined per
  receiver, so a receiver that was not calibrated with liquid nitrogen in
  the latest entry shows its own latest calibration.
- History plot: one legend per receiver below the panels instead of one in
  every panel, so that the legend never hides data.
- `--no-plot` now suppresses both plots.
- The NetCDF file (`--netcdf`) still contains all calibration types.

### Fixed
- `calibration_flag` comment: the flag is 0 = not calibrated,
  1 = calibrated per channel (RPG manual, appendix A20), not an 8 bit
  array.
- `alpha`: comment with the detector model and the valid range added.

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
  (dimensionless).
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
