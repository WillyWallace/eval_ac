"""Tests of the plotting routines."""
import matplotlib.pyplot as plt
import pytest

from eval_ac.analysis import (CAL_TYPE_SKY_TIPPING, calibration_drift,
                              select_cal_type)
from eval_ac.convert_abscal_his import read_abscal_his
from eval_ac.plotting import (DEFAULT_VARIABLES, plot_calibration_history,
                              plot_drift)


def _legend_labels(figure, col):
    """Returns the legend texts of a receiver column."""
    legend = figure.get_axes()[-2 + col].get_legend()
    return [text.get_text() for text in legend.get_texts()]


@pytest.mark.parametrize('n_samples', [1, 2, 3, 16])
def test_plot_with_few_entries(abscal_his, n_samples):
    """Plot works for any number of calibration entries."""
    data_set = read_abscal_his(abscal_his).isel(
        n_samples=slice(-n_samples, None))
    figure = plot_calibration_history(data_set)
    axes = figure.get_axes()
    assert len(axes) == 2 * len(DEFAULT_VARIABLES)
    assert 'latest (2026-04-29)' in _legend_labels(figure, 0)
    assert len(axes[0].get_lines()) == n_samples
    plt.close(figure)


def test_plot_selected_variables(abscal_his):
    """Only the requested variables are plotted."""
    figure = plot_calibration_history(read_abscal_his(abscal_his),
                                      variables=['gain'])
    assert len(figure.get_axes()) == 2
    plt.close(figure)


def test_plot_marks_not_calibrated(modified_his):
    """Channels with flag 0 are marked and explained in the legend."""
    path = modified_his(flags={(15, 2): 0})
    figure = plot_calibration_history(read_abscal_his(path))
    assert 'not calibrated (flag 0)' in _legend_labels(figure, 0)
    assert 'not calibrated (flag 0)' not in _legend_labels(figure, 1)
    plt.close(figure)


def test_plot_latest_per_receiver(modified_his):
    """Receiver 2 shows its own latest LN2 calibration."""
    path = modified_his(cal_types={(15, 2): CAL_TYPE_SKY_TIPPING})
    figure = plot_calibration_history(select_cal_type(read_abscal_his(path)))
    assert 'latest (2026-04-29)' in _legend_labels(figure, 0)
    assert 'latest (2026-03-19)' in _legend_labels(figure, 1)
    plt.close(figure)


def test_plot_drift(abscal_his):
    """Drift plot has the same layout and marks exceedances."""
    drift = calibration_drift(read_abscal_his(abscal_his))
    figure = plot_drift(drift, thresholds={'gain': 1.5})
    axes = figure.get_axes()
    assert len(axes) == 2 * len(DEFAULT_VARIABLES)
    assert axes[0].get_title() == 'receiver gain (threshold ±1.5 %)'
    assert 'latest exceeds threshold' in _legend_labels(figure, 0)
    plt.close(figure)


def test_plot_drift_without_exceedance(abscal_his):
    """Without exceedance, no marker is explained in the legend."""
    figure = plot_drift(calibration_drift(read_abscal_his(abscal_his)))
    assert 'latest exceeds threshold' not in _legend_labels(figure, 0)
    plt.close(figure)
