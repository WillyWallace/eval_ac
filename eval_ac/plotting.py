"""Visualize the absolute calibration history of an RPG microwave radiometer."""

import numpy as np
import xarray as xr
import matplotlib.pyplot as plt

from eval_ac.analysis import (DEFAULT_THRESHOLDS, not_calibrated,
                              receiver_masks, valid_samples)

#: Variables plotted by default (one row each).
DEFAULT_VARIABLES = ('gain', 'temp_noise', 'temp_sys', 'alpha')

#: Line styles of the latest, previous and all older calibrations.
LATEST_PLOT_KWARGS = {'lw': 2}
PREVIOUS_PLOT_KWARGS = {'lw': 2}
OLDER_PLOT_KWARGS = {'lw': 1, 'color': 'lightgrey'}

#: Marker style of channels that were not calibrated (flag 0).
NOT_CALIBRATED_KWARGS = {'marker': 'x', 'color': 'red', 'ls': 'none',
                         'ms': 7, 'mew': 2, 'zorder': 5}

#: Marker style of channels exceeding the drift threshold.
EXCEEDANCE_KWARGS = {'marker': 'o', 'mfc': 'none', 'color': 'red',
                     'ls': 'none', 'ms': 10, 'mew': 2, 'zorder': 5}

#: Line style of the drift thresholds.
THRESHOLD_KWARGS = {'color': 'red', 'ls': '--', 'lw': 1}


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


def _styles(latest_plot_kwargs, previous_plot_kwargs, older_plot_kwargs):
    """Merges the user line styles with the defaults."""
    return {
        'latest': {**LATEST_PLOT_KWARGS, **(latest_plot_kwargs or {})},
        'previous': {**PREVIOUS_PLOT_KWARGS, **(previous_plot_kwargs or {})},
        'older': {**OLDER_PLOT_KWARGS, **(older_plot_kwargs or {})},
    }


def _plot_lines(axis, data_set, freq, values, styles):
    """Draws older, previous and latest entry; returns their positions.

    Entries without any value (e.g. removed by the calibration type
    selection) are skipped.
    """
    samples = valid_samples(values)
    for i, sample in enumerate(samples[:-2]):
        axis.plot(freq, values[sample],
                  label=f'older ({len(samples) - 2})' if i == 0 else None,
                  **styles['older'])
    if len(samples) >= 2:
        axis.plot(freq, values[samples[-2]],
                  label=f'previous ({_date_label(data_set, samples[-2])})',
                  **styles['previous'])
    if len(samples) >= 1:
        axis.plot(freq, values[samples[-1]],
                  label=f'latest ({_date_label(data_set, samples[-1])})',
                  **styles['latest'])
    return samples


def _mark_not_calibrated(axis, freq, values, flagged):
    """Marks all values with calibration flag 0."""
    if np.any(flagged & ~np.isnan(values)):
        rows, cols = np.nonzero(flagged)
        axis.plot(freq[cols], values[rows, cols],
                  label='not calibrated (flag 0)', **NOT_CALIBRATED_KWARGS)


def _column_legends(axes):
    """Draws one legend per column (receiver) below its bottom panel.

    The legend combines the entries of all panels of the column, so that
    markers appearing only in some panels are explained as well. It is
    placed outside the panels so that it never hides data.
    """
    for col in range(axes.shape[1]):
        entries = {}
        for axis in axes[:, col]:
            for handle, label in zip(*axis.get_legend_handles_labels()):
                entries.setdefault(label, handle)
        if entries:
            axes[-1, col].legend(entries.values(), entries.keys(),
                                 fontsize='small', ncol=2,
                                 loc='upper center',
                                 bbox_to_anchor=(0.5, -0.3))


def _subplots(n_rows, n_cols):
    """Creates the figure in the common layout."""
    return plt.subplots(n_rows, n_cols,
                        figsize=(5 * n_cols, 2.5 * n_rows), squeeze=False)


def _history_panel(axis, data_set, variable, mask, styles):
    """Draws one variable of one receiver in the history plot."""
    freq = data_set['freq'].values[mask]
    values = data_set[variable].values[:, mask].astype(float)
    _plot_lines(axis, data_set, freq, values, styles)
    _mark_not_calibrated(axis, freq, values,
                         not_calibrated(data_set)[:, mask])
    axis.set_title(data_set[variable].attrs.get('long_name', variable))
    axis.set_xlabel(_axis_label(data_set['freq']))
    axis.set_ylabel(_axis_label(data_set[variable]))


def plot_calibration_history(data_set: xr.Dataset,
                             variables=DEFAULT_VARIABLES,
                             latest_plot_kwargs=None,
                             previous_plot_kwargs=None,
                             older_plot_kwargs=None):
    """Plots the latest calibration in comparison to the previous ones.

    One row is drawn per variable and one column per receiver. The latest
    and the previous calibration of each receiver are highlighted, all
    older calibrations are drawn in the background. Channels that were not
    calibrated (``calibration_flag == 0``) are marked with a red cross.

    Args:
        data_set: Dataset as returned by
            :func:`eval_ac.convert_abscal_his.read_abscal_his`, optionally
            after :func:`eval_ac.analysis.select_cal_type`.
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
    if data_set.sizes['n_samples'] == 0:
        raise ValueError('The dataset contains no calibration entries.')
    styles = _styles(latest_plot_kwargs, previous_plot_kwargs,
                     older_plot_kwargs)
    masks = list(receiver_masks(data_set).values())

    figure, axes = _subplots(len(variables), len(masks))
    for row, variable in enumerate(variables):
        for col, mask in enumerate(masks):
            _history_panel(axes[row, col], data_set, variable, mask, styles)

    _column_legends(axes)
    figure.tight_layout()
    return figure


def _mark_exceedances(axis, freq, latest, threshold):
    """Draws the thresholds and circles the exceeding channels."""
    axis.axhline(threshold, label='threshold', **THRESHOLD_KWARGS)
    axis.axhline(-threshold, **THRESHOLD_KWARGS)
    if latest is None:
        return
    with np.errstate(invalid='ignore'):
        exceeded = np.abs(latest) > threshold
    if np.any(exceeded):
        axis.plot(freq[exceeded], latest[exceeded],
                  label='latest exceeds threshold', **EXCEEDANCE_KWARGS)


def _set_drift_ylim(axis, deviation, samples, threshold):
    """Scales the y-axis to the threshold and the two newest entries.

    Single outliers of older calibrations would otherwise hide the latest
    one; they are clipped.
    """
    newest = deviation[samples[-2:]]
    limit = 1.5 * (threshold or 0)
    if np.any(~np.isnan(newest)):
        limit = max(limit, 1.2 * float(np.nanmax(np.abs(newest))))
    if limit > 0:
        axis.set_ylim(-limit, limit)


def _drift_panel(axis, drift, variable, mask, options):
    """Draws one variable of one receiver in the drift plot.

    ``options`` holds the line ``styles`` and the ``threshold``.
    """
    threshold = options['threshold']
    freq = drift['freq'].values[mask]
    deviation = drift[f'{variable}_deviation'].values[:, mask]
    axis.axhline(0, color='black', lw=0.5)
    samples = _plot_lines(axis, drift, freq, deviation, options['styles'])
    if threshold is not None:
        _mark_exceedances(axis, freq,
                          deviation[samples[-1]] if samples.size else None,
                          threshold)
    _set_drift_ylim(axis, deviation, samples, threshold)

    title = drift[f'{variable}_reference'].attrs.get(
        'long_name', variable).split(',')[0]
    if threshold is not None:
        title += f' (threshold ±{threshold:g} %)'
    axis.set_title(title)
    axis.set_xlabel(_axis_label(drift['freq']))
    axis.set_ylabel('deviation [%]')


def plot_drift(drift: xr.Dataset,  # pylint: disable=too-many-arguments
               variables=DEFAULT_VARIABLES,
               thresholds=None,
               *,
               latest_plot_kwargs=None,
               previous_plot_kwargs=None,
               older_plot_kwargs=None):
    """Plots the deviation of each calibration from the reference.

    The layout is the same as in :func:`plot_calibration_history`. The
    y-axis shows the deviation from the median of the calibrations before
    the latest one in percent. The thresholds are drawn as dashed lines,
    channels of the latest calibration exceeding them are circled. The
    y-axis is scaled to the thresholds and the two newest calibrations, so
    outliers of older calibrations may be clipped.

    Args:
        drift: Dataset as returned by
            :func:`eval_ac.analysis.calibration_drift`.
        variables: Names of the variables to plot.
        thresholds: Dictionary ``{variable: threshold in percent}``. Missing
            variables use :data:`eval_ac.analysis.DEFAULT_THRESHOLDS`.
        latest_plot_kwargs: Matplotlib line options of the latest
            calibration.
        previous_plot_kwargs: Matplotlib line options of the previous
            calibration.
        older_plot_kwargs: Matplotlib line options of all older
            calibrations.

    Returns:
        :class:`matplotlib.figure.Figure` with the plots.
    """
    thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    styles = _styles(latest_plot_kwargs, previous_plot_kwargs,
                     older_plot_kwargs)
    masks = list(receiver_masks(drift).values())

    figure, axes = _subplots(len(variables), len(masks))
    for row, variable in enumerate(variables):
        options = {'styles': styles, 'threshold': thresholds.get(variable)}
        for col, mask in enumerate(masks):
            _drift_panel(axes[row, col], drift, variable, mask, options)

    _column_legends(axes)
    figure.suptitle('Deviation from the median of the '
                    f'{drift.attrs.get("n_reference", "")} calibrations '
                    'before the latest one')
    figure.tight_layout()
    return figure
