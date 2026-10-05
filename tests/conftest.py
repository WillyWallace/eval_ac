"""Shared test fixtures."""
from pathlib import Path

import matplotlib
import numpy as np
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


# byte layout of the example file: header of 8 bytes, then 16 records of
# 420 bytes (7 + 7 channels)
_HEADER_BYTES = 8
_RECORD_BYTES = 420
_CAL_TYPE_OFFSET = {1: 8, 2: 12}
_FLAG_OFFSET = 140


@pytest.fixture(name='modified_his')
def fixture_modified_his(abscal_his, tmp_path):
    """Factory writing a copy of the example file with changed values.

    Usage: ``modified_his(cal_types={(sample, receiver): 2},
    flags={(sample, channel): 0})``.
    """
    def _write(cal_types=None, flags=None):
        content = bytearray(abscal_his.read_bytes())
        for (sample, receiver), value in (cal_types or {}).items():
            pos = (_HEADER_BYTES + sample * _RECORD_BYTES
                   + _CAL_TYPE_OFFSET[receiver])
            content[pos:pos + 4] = np.int32(value).tobytes()
        for (sample, channel), value in (flags or {}).items():
            pos = (_HEADER_BYTES + sample * _RECORD_BYTES + _FLAG_OFFSET
                   + 4 * channel)
            content[pos:pos + 4] = np.int32(value).tobytes()
        path = tmp_path / 'modified.his'
        path.write_bytes(bytes(content))
        return path
    return _write
