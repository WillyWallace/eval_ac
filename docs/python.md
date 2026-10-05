# Python interface

```{include} ../README.md
:start-after: <!-- docs-python-start -->
:end-before: <!-- docs-python-end -->
```

## API reference

### Reading ABSCAL.HIS

```{eval-rst}
.. automodule:: eval_ac.convert_abscal_his
   :members: read_abscal_his, write_netcdf, read_raw, records_to_dataset, HatproBinAbscalHis, FILE_CODE_ABSCAL_HIS, TIME_REFERENCE
```

### Selection, quality checks and drift

```{eval-rst}
.. automodule:: eval_ac.analysis
   :members:
```

### Plotting

```{eval-rst}
.. automodule:: eval_ac.plotting
   :members: plot_calibration_history, plot_drift, DEFAULT_VARIABLES
```

### Command line

```{eval-rst}
.. automodule:: eval_ac.cli
   :members: main, build_parser, EXIT_WARNING
```
