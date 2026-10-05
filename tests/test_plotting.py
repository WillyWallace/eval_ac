"""Tests of the plotting routines."""
import matplotlib.pyplot as plt
import pytest

from eval_ac.convert_abscal_his import read_abscal_his
from eval_ac.plotting import DEFAULT_VARIABLES, plot_calibration_history


@pytest.mark.parametrize('n_samples', [1, 2, 3, 16])
def test_plot_with_few_entries(abscal_his, n_samples):
    """Plot works for any number of calibration entries."""
    data_set = read_abscal_his(abscal_his).isel(
        n_samples=slice(-n_samples, None))
    figure = plot_calibration_history(data_set)
    axes = figure.get_axes()
    assert len(axes) == 2 * len(DEFAULT_VARIABLES)
    labels = [text.get_text() for text in axes[0].get_legend().get_texts()]
    assert labels[-1] == 'latest (2026-04-29)'
    assert len(axes[0].get_lines()) == n_samples
    plt.close(figure)


def test_plot_selected_variables(abscal_his):
    """Only the requested variables are plotted."""
    figure = plot_calibration_history(read_abscal_his(abscal_his),
                                      variables=['gain'])
    assert len(figure.get_axes()) == 2
    plt.close(figure)
