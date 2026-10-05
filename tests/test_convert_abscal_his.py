"""Tests of the ABSCAL.HIS reader."""
import numpy as np
import pytest
import xarray as xr

from eval_ac.convert_abscal_his import (HatproBinAbscalHis, read_abscal_his,
                                        write_netcdf)


def test_dimensions_and_variables(abscal_his):
    """Example file contains 16 calibrations with 2 x 7 channels."""
    data_set = read_abscal_his(abscal_his)
    assert data_set.sizes == {'n_samples': 16, 'freq': 14}
    for var in ('gain', 'temp_noise', 'temp_sys', 'alpha',
                'calibration_flag'):
        assert data_set[var].dims == ('n_samples', 'freq')
    assert list(data_set['receiver'].values) == [1] * 7 + [2] * 7


def test_physical_plausibility(abscal_his):
    """Values are in a physically plausible range."""
    data_set = read_abscal_his(abscal_his)
    assert np.all(np.diff(data_set['freq'].values[:7]) > 0)
    assert np.all(np.diff(data_set['freq'].values[7:]) > 0)
    assert np.all(data_set['gain'] > 0)
    assert np.all(data_set['temp_sys'] > 0)
    assert np.all(abs(data_set['cold_load_temp_1'] - 77) < 1)  # LN2


def test_time_is_decoded(abscal_his):
    """Calibration times are seconds since 2001-01-01."""
    data_set = read_abscal_his(abscal_his)
    assert data_set['time'].values[0] == np.datetime64('2018-08-22T07:31:25')
    assert data_set['time'].values[-1] == np.datetime64('2026-04-29T09:32:38')
    assert np.all(np.diff(data_set['time'].values) > np.timedelta64(0))


def test_matches_reference(abscal_his, reference_nc):
    """Values are identical to the output of eval_ac 0.1.0."""
    data_set = read_abscal_his(abscal_his)
    with xr.open_dataset(reference_nc, decode_times=False) as reference:
        for var in reference.variables:
            np.testing.assert_array_equal(data_set[var].values,
                                          reference[var].values, err_msg=var)


def test_netcdf_round_trip(abscal_his, tmp_path):
    """Written NetCDF file can be read again with all attributes."""
    data_set = read_abscal_his(abscal_his)
    out = tmp_path / 'abscal.nc'
    write_netcdf(data_set, out)
    with xr.open_dataset(out, decode_times=False) as result:
        xr.testing.assert_identical(result.drop_vars('time'),
                                    data_set.drop_vars('time'))
    with xr.open_dataset(out) as result:
        xr.testing.assert_identical(result['time'], data_set['time'])
        assert result.attrs['Conventions'] == 'CF-1.8'
        assert result['gain'].attrs['units'] == 'V K-1'


def test_wrong_file_code(abscal_his, tmp_path):
    """A file with another file code is rejected."""
    content = bytearray(abscal_his.read_bytes())
    content[:4] = np.int32(12345).tobytes()
    bad = tmp_path / 'bad.his'
    bad.write_bytes(bytes(content))
    with pytest.raises(ValueError, match='unknown file code 12345'):
        read_abscal_his(bad)


def test_truncated_file(abscal_his, tmp_path):
    """A truncated file gives a readable error."""
    bad = tmp_path / 'truncated.his'
    bad.write_bytes(abscal_his.read_bytes()[:-10])
    with pytest.raises(ValueError, match='unexpected end of file'):
        read_abscal_his(bad)


def test_missing_file(tmp_path):
    """A missing file raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        read_abscal_his(tmp_path / 'does_not_exist.his')


def test_legacy_class_without_output(abscal_his, tmp_path, monkeypatch):
    """The legacy class only writes a file when asked to."""
    monkeypatch.chdir(tmp_path)
    obj = HatproBinAbscalHis(abscal_his)
    assert obj.filename == abscal_his
    assert obj.header['n_samples'] == 16
    for var in ('gain', 'temp_noise', 'temp_sys', 'alpha'):
        assert var in obj.xrdata
    assert not list(tmp_path.iterdir())


def test_legacy_class_with_output(abscal_his, tmp_path):
    """The legacy class writes the NetCDF file when filename_out is given."""
    out = tmp_path / 'abscal.nc'
    HatproBinAbscalHis(abscal_his, out)
    assert out.exists()
