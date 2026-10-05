"""Tests of the command line interface."""
import pytest

from eval_ac import __version__
from eval_ac.cli import main


def test_writes_netcdf_and_plot(abscal_his, tmp_path):
    """Both output files are written."""
    netcdf = tmp_path / 'abscal.nc'
    plot = tmp_path / 'plot.png'
    assert main([str(abscal_his), '--netcdf', str(netcdf),
                 '--plot', str(plot)]) == 0
    assert netcdf.stat().st_size > 0
    assert plot.stat().st_size > 0


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
