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
_TIME_OFFSET = {1: 16, 2: 20}
_CHANNEL_OFFSET = {'calibration_flag': 140, 'alpha': 364}


def _put(content, pos, value, dtype):
    """Overwrites 4 bytes of ``content`` at ``pos``."""
    content[pos:pos + 4] = np.array(value, dtype=dtype).tobytes()


@pytest.fixture(name='modified_his')
def fixture_modified_his(abscal_his, tmp_path):
    """Factory writing a copy of the example file with changed values.

    Usage: ``modified_his(cal_types={(sample, receiver): 2},
    flags={(sample, channel): 0}, times={(sample, receiver): seconds},
    alpha={(sample, channel): 0.85})``.
    """
    def _write(cal_types=None, flags=None, times=None, alpha=None):
        content = bytearray(abscal_his.read_bytes())

        def record(sample):
            return _HEADER_BYTES + sample * _RECORD_BYTES

        for (sample, receiver), value in (cal_types or {}).items():
            _put(content, record(sample) + _CAL_TYPE_OFFSET[receiver], value,
                 '<i4')
        for (sample, receiver), value in (times or {}).items():
            _put(content, record(sample) + _TIME_OFFSET[receiver], value,
                 '<i4')
        for (sample, channel), value in (flags or {}).items():
            _put(content, record(sample) + _CHANNEL_OFFSET['calibration_flag']
                 + 4 * channel, value, '<i4')
        for (sample, channel), value in (alpha or {}).items():
            _put(content, record(sample) + _CHANNEL_OFFSET['alpha']
                 + 4 * channel, value, '<f4')
        path = tmp_path / 'modified.his'
        path.write_bytes(bytes(content))
        return path
    return _write
