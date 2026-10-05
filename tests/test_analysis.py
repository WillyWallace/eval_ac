"""Tests of the selection, quality control and drift analysis."""
import numpy as np
import pytest

from eval_ac.analysis import (CAL_TYPE_SKY_TIPPING, DEFAULT_THRESHOLDS,
                              alpha_out_of_range, calibration_age,
                              calibration_drift, drift_exceedances,
                              latest_not_calibrated, select_cal_type)
from eval_ac.convert_abscal_his import read_abscal_his


def test_select_keeps_all_ln2(abscal_his):
    """The example file contains only calibrations with liquid nitrogen."""
    data_set = read_abscal_his(abscal_his)
    selected = select_cal_type(data_set)
    assert selected.sizes == data_set.sizes
    assert not np.any(np.isnan(selected['gain'].values))
    assert selected['gain'].attrs == data_set['gain'].attrs


def test_select_removes_entries_and_receivers(modified_his):
    """Entries without LN2 are removed, single receivers set to NaN."""
    path = modified_his(cal_types={(5, 1): CAL_TYPE_SKY_TIPPING,
                                   (5, 2): CAL_TYPE_SKY_TIPPING,
                                   (15, 2): CAL_TYPE_SKY_TIPPING})
    selected = select_cal_type(read_abscal_his(path))
    assert selected.sizes['n_samples'] == 15
    assert 5 not in selected['n_samples'].values
    gain = selected['gain'].sel(n_samples=15).values
    assert not np.any(np.isnan(gain[:7]))
    assert np.all(np.isnan(gain[7:]))


def test_select_sky_tipping(modified_his):
    """Other calibration types can be selected as well."""
    path = modified_his(cal_types={(5, 1): CAL_TYPE_SKY_TIPPING})
    selected = select_cal_type(read_abscal_his(path), CAL_TYPE_SKY_TIPPING)
    assert list(selected['n_samples'].values) == [5]


def test_drift_reference_is_median(abscal_his):
    """Reference is the median of the 5 entries before the latest."""
    data_set = read_abscal_his(abscal_his)
    drift = calibration_drift(data_set, n_reference=5)
    gain = data_set['gain'].values
    expected = np.median(gain[10:15], axis=0)
    np.testing.assert_allclose(drift['gain_reference'].values, expected,
                               rtol=1e-6)
    np.testing.assert_allclose(drift['gain_deviation'].values[-1],
                               100 * (gain[-1] - expected) / expected,
                               rtol=1e-5)
    assert np.all(drift['latest_sample'].values == 15)
    assert np.all(drift['n_reference_used'].values == 5)


def test_drift_ignores_flagged_values(modified_his):
    """Values with flag 0 are not part of the reference or the result."""
    path = modified_his(flags={(12, 3): 0, (15, 4): 0})
    data_set = read_abscal_his(path)
    drift = calibration_drift(data_set)
    gain = data_set['gain'].values
    expected = np.median(gain[[10, 11, 13, 14], 3])
    assert drift['gain_reference'].values[3] == pytest.approx(expected)
    assert drift['n_reference_used'].values[3] == 4
    assert np.isnan(drift['gain_deviation'].values[-1, 4])


def test_drift_per_receiver(modified_his):
    """The latest entry is determined per receiver."""
    path = modified_his(cal_types={(15, 2): CAL_TYPE_SKY_TIPPING})
    drift = calibration_drift(select_cal_type(read_abscal_his(path)))
    assert list(drift['latest_sample'].values) == [15] * 7 + [14] * 7


def test_drift_single_entry(abscal_his):
    """With one entry there is no reference, but no error either."""
    data_set = read_abscal_his(abscal_his).isel(n_samples=[0])
    drift = calibration_drift(data_set)
    assert np.all(np.isnan(drift['gain_reference'].values))
    assert not drift_exceedances(drift)


def test_exceedances(abscal_his):
    """Only channels above the threshold are reported."""
    drift = calibration_drift(read_abscal_his(abscal_his))
    assert not drift_exceedances(drift)
    rows = drift_exceedances(drift, {'gain': 1.5})
    assert [round(row['freq'], 2) for row in rows] == [23.84, 25.44, 53.86]
    assert all(abs(row['deviation']) > 1.5 for row in rows)
    assert rows[2]['receiver'] == 2


def test_default_thresholds_cover_variables():
    """All analysed variables have a default threshold."""
    assert set(DEFAULT_THRESHOLDS) == {'gain', 'temp_noise', 'temp_sys',
                                       'alpha'}


def test_latest_not_calibrated(modified_his):
    """Flag 0 channels of the latest entry of each receiver are listed."""
    path = modified_his(cal_types={(15, 2): CAL_TYPE_SKY_TIPPING},
                        flags={(15, 2): 0, (14, 10): 0, (13, 0): 0})
    rows = latest_not_calibrated(select_cal_type(read_abscal_his(path)))
    assert [(round(row['freq'], 2), row['receiver']) for row in rows] == [
        (23.84, 1), (54.94, 2)]


def test_calibration_age(abscal_his):
    """Age is counted from the latest calibration of each receiver."""
    rows = calibration_age(read_abscal_his(abscal_his),
                           now='2026-05-29T09:32:38')
    assert [row['receiver'] for row in rows] == [1, 2]
    assert rows[0]['time'] == np.datetime64('2026-04-29T09:32:38')
    assert rows[0]['age_days'] == pytest.approx(30.0)


def test_calibration_age_uses_receiver_time(modified_his):
    """Receiver 2 uses its own time stamp (time_of_rec_2)."""
    one_day_earlier = 799147958 - 86400
    path = modified_his(times={(15, 2): one_day_earlier})
    rows = calibration_age(read_abscal_his(path), now='2026-05-29T09:32:38')
    assert rows[0]['age_days'] == pytest.approx(30.0)
    assert rows[1]['age_days'] == pytest.approx(31.0)


def test_calibration_age_after_selection(modified_his):
    """Without LN2 in the latest entry, the entry before is used."""
    path = modified_his(cal_types={(15, 2): CAL_TYPE_SKY_TIPPING})
    rows = calibration_age(select_cal_type(read_abscal_his(path)))
    assert str(rows[0]['time'].astype('datetime64[D]')) == '2026-04-29'
    assert str(rows[1]['time'].astype('datetime64[D]')) == '2026-03-19'


def test_alpha_in_range(abscal_his):
    """All alpha values of the example file are valid."""
    assert not alpha_out_of_range(read_abscal_his(abscal_his))


def test_alpha_out_of_range(modified_his):
    """Values below 0.9 or from 1 on are reported, flag 0 is skipped."""
    path = modified_his(alpha={(15, 0): 0.85, (15, 8): 1.0, (15, 3): 0.8,
                               (14, 1): 0.5},
                        flags={(15, 3): 0})
    rows = alpha_out_of_range(read_abscal_his(path))
    assert [(round(row['freq'], 2), row['receiver']) for row in rows] == [
        (22.24, 1), (52.28, 2)]
    assert rows[0]['alpha'] == pytest.approx(0.85)
