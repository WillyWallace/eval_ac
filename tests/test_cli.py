"""Tests of the command line interface."""
import pytest

from eval_ac import __version__
from eval_ac.cli import main


def test_writes_netcdf_and_plots(abscal_his, tmp_path):
    """All output files are written."""
    netcdf = tmp_path / 'abscal.nc'
    plot = tmp_path / 'plot.png'
    drift = tmp_path / 'drift.png'
    assert main([str(abscal_his), '--netcdf', str(netcdf),
                 '--plot', str(plot), '--drift-plot', str(drift)]) == 0
    for path in (netcdf, plot, drift):
        assert path.stat().st_size > 0


def test_no_plot(abscal_his, tmp_path, monkeypatch):
    """With --no-plot nothing is written."""
    monkeypatch.chdir(tmp_path)
    assert main([str(abscal_his), '--no-plot']) == 0
    assert not list(tmp_path.iterdir())


def test_missing_input(tmp_path, capsys):
    """A missing input file gives an error message without traceback."""
    assert main([str(tmp_path / 'missing.his'), '--no-plot']) == 1
    assert 'eval-ac: error:' in capsys.readouterr().err


def test_version(capsys):
    """--version prints the package version."""
    with pytest.raises(SystemExit):
        main(['--version'])
    assert __version__ in capsys.readouterr().out


def test_drift_report_and_exit_code(abscal_his, capsys):
    """Exceedances are reported; --fail-on-drift sets exit code 2."""
    args = [str(abscal_his), '--no-plot', '-t', 'gain=1.5']
    assert main(args) == 0
    out = capsys.readouterr().out
    assert '3 channel(s) of the latest calibration exceed' in out
    assert main(args + ['--fail-on-drift']) == 2


def test_no_drift(abscal_his, capsys):
    """With the default thresholds the example file is within limits."""
    assert main([str(abscal_his), '--no-plot', '--fail-on-drift']) == 0
    assert 'within the thresholds' in capsys.readouterr().out


def test_reports_not_calibrated(modified_his, capsys):
    """Flag 0 channels of the latest calibration are reported."""
    path = modified_his(flags={(15, 2): 0})
    assert main([str(path), '--no-plot']) == 0
    out = capsys.readouterr().out
    assert '1 channel(s) of the latest calibration were not calibrated' in out
    assert '23.84 GHz  receiver 1' in out


def test_no_ln2_calibration(modified_his, capsys):
    """A file without LN2 calibrations gives an error."""
    path = modified_his(cal_types={(sample, receiver): 2
                                   for sample in range(16)
                                   for receiver in (1, 2)})
    assert main([str(path), '--no-plot']) == 1
    assert '--all-cal-types' in capsys.readouterr().err
    assert main([str(path), '--no-plot', '--all-cal-types']) == 0


@pytest.mark.parametrize('threshold', ['gain', 'gain=x', 'foo=1'])
def test_invalid_threshold(abscal_his, threshold):
    """Invalid thresholds are rejected by the argument parser."""
    with pytest.raises(SystemExit):
        main([str(abscal_his), '-t', threshold])
