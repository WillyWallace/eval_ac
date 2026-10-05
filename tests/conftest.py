"""Shared test fixtures."""
from pathlib import Path

import matplotlib
import pytest

matplotlib.use('Agg')

EXAMPLE_DATA = Path(__file__).resolve().parent.parent / 'example_data'


@pytest.fixture(name='abscal_his')
def fixture_abscal_his() -> Path:
    """Path of the example ABSCAL.HIS file."""
    return EXAMPLE_DATA / 'ABSCAL.HIS'


@pytest.fixture(name='reference_nc')
def fixture_reference_nc() -> Path:
    """NetCDF file written by eval_ac 0.1.0 from the example file."""
    return EXAMPLE_DATA / 'abscal.nc'
