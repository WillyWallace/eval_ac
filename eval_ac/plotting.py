"""Visualize the absolute calibration history of an RPG microwave radiometer."""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

#: Variables plotted by default (one row each).
DEFAULT_VARIABLES = ('gain', 'temp_noise', 'temp_sys', 'alpha')

#: Line styles of the latest, previous and all older calibrations.
LATEST_PLOT_KWARGS = {'lw': 2}
PREVIOUS_PLOT_KWARGS = {'lw': 2}
OLDER_PLOT_KWARGS = {'lw': 1, 'color': 'lightgrey'}


def _date_label(data_set: xr.Dataset, sample: int) -> str:
    """Returns the calibration date of entry ``sample`` as text."""
    if 'time' not in data_set.coords:
        return f'#{sample}'
    return str(np.datetime_as_string(data_set['time'].values[sample],
                                     unit='D'))


def _axis_label(data_array: xr.DataArray) -> str:
    """Returns 'long_name [units]' of a variable."""
    name = data_array.attrs.get('long_name', data_array.name)
    units = data_array.attrs.get('units')
    return f'{name} [{units}]' if units else name


def _receiver_slices(data_set: xr.Dataset) -> list:
    """Returns one boolean channel mask per receiver."""
    if 'receiver' not in data_set.coords:
        return [np.ones(data_set.sizes['freq'], dtype=bool)]
    receiver = data_set['receiver'].values
    return [receiver == number for number in np.unique(receiver)]


def _plot_panel(axis, data_set: xr.Dataset, variable: str, mask, styles):
    """Plots all calibrations of one variable and one receiver."""
    n_samples = data_set.sizes['n_samples']
    freq = data_set['freq'].values[mask]
    values = data_set[variable].values[:, mask]

    for sample in range(n_samples - 2):
        axis.plot(freq, values[sample],
                  label=f'older ({n_samples - 2})' if sample == 0 else None,
                  **styles['older'])
    if n_samples >= 2:
        axis.plot(freq, values[-2],
                  label=f'previous ({_date_label(data_set, -2)})',
                  **styles['previous'])
    axis.plot(freq, values[-1],
              label=f'latest ({_date_label(data_set, -1)})',
              **styles['latest'])
    axis.set_title(data_set[variable].attrs.get('long_name', variable))
    axis.set_xlabel(_axis_label(data_set['freq']))
    axis.set_ylabel(_axis_label(data_set[variable]))
    axis.legend(fontsize='small')


def plot_calibration_history(data_set: xr.Dataset,
                             variables=DEFAULT_VARIABLES,
                             latest_plot_kwargs=None,
                             previous_plot_kwargs=None,
                             older_plot_kwargs=None):
    """Plots the latest calibration in comparison to the previous ones.

    One row is drawn per variable and one column per receiver. The latest
    and the previous calibration are highlighted, all older calibrations
    are drawn in the background.

    Args:
        data_set: Dataset as returned by
            :func:`eval_ac.convert_abscal_his.read_abscal_his`.
        variables: Names of the variables to plot.
        latest_plot_kwargs: Matplotlib line options of the latest
            calibration.
        previous_plot_kwargs: Matplotlib line options of the previous
            calibration.
        older_plot_kwargs: Matplotlib line options of all older
            calibrations.

    Returns:
        :class:`matplotlib.figure.Figure` with the plots.
    """
    styles = {
        'latest': {**LATEST_PLOT_KWARGS, **(latest_plot_kwargs or {})},
        'previous': {**PREVIOUS_PLOT_KWARGS, **(previous_plot_kwargs or {})},
        'older': {**OLDER_PLOT_KWARGS, **(older_plot_kwargs or {})},
    }
    if data_set.sizes['n_samples'] == 0:
        raise ValueError('The dataset contains no calibration entries.')
    masks = _receiver_slices(data_set)

    figure, axes = plt.subplots(len(variables), len(masks),
                                figsize=(5 * len(masks),
                                         2.5 * len(variables)),
                                squeeze=False)
    for row, variable in enumerate(variables):
        for col, mask in enumerate(masks):
            _plot_panel(axes[row, col], data_set, variable, mask, styles)

    figure.tight_layout()
    return figure
