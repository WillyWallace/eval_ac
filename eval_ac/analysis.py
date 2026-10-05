"""Selection, quality control and drift analysis of the calibration history.

Typical usage::

    from eval_ac.convert_abscal_his import read_abscal_his
    from eval_ac.analysis import select_cal_type, calibration_drift, \
        drift_exceedances

    ds = select_cal_type(read_abscal_his('ABSCAL.HIS'))
    drift = calibration_drift(ds)
    for row in drift_exceedances(drift):
        print(row)
"""

import warnings

import numpy as np
import xarray as xr

#: Calibration types stored in ``cal_type_1`` and ``cal_type_2``.
CAL_TYPE_NONE = 0
CAL_TYPE_LN2 = 1
CAL_TYPE_SKY_TIPPING = 2

#: Value of ``calibration_flag`` for channels that were not calibrated.
FLAG_NOT_CALIBRATED = 0

#: Variables with one value per calibration entry and channel.
CHANNEL_VARIABLES = ('gain', 'temp_noise', 'temp_sys', 'alpha')

#: Default number of calibrations before the latest one that form the
#: reference of the drift analysis.
DEFAULT_N_REFERENCE = 5

#: Default thresholds of the drift analysis in percent. They are about the
#: 99th percentile of the deviations found in the example data of a HATPRO
#: (2018-2026) and should be adapted to the instrument.
DEFAULT_THRESHOLDS = {
    'gain': 10.0,
    'temp_noise': 2.5,
    'temp_sys': 2.5,
    'alpha': 0.5,
}


def receiver_masks(data_set: xr.Dataset) -> dict:
    """Returns a boolean channel mask for each receiver number."""
    if 'receiver' not in data_set.coords:
        return {1: np.ones(data_set.sizes['freq'], dtype=bool)}
    receiver = data_set['receiver'].values
    return {int(number): receiver == number for number in np.unique(receiver)}


def channel_cal_type(data_set: xr.Dataset) -> xr.DataArray:
    """Returns the calibration type of each entry and channel.

    Channels of receiver 1 get ``cal_type_1``, channels of receiver 2 get
    ``cal_type_2``.
    """
    cal_type = np.empty((data_set.sizes['n_samples'],
                         data_set.sizes['freq']), dtype=np.int32)
    for number, mask in receiver_masks(data_set).items():
        cal_type[:, mask] = data_set[f'cal_type_{number}'].values[:, None]
    return xr.DataArray(cal_type, dims=('n_samples', 'freq'))


def select_cal_type(data_set: xr.Dataset,
                    cal_type: int = CAL_TYPE_LN2) -> xr.Dataset:
    """Keeps only the calibrations of the given type.

    Entries in which no receiver has the requested calibration type are
    removed. If only one receiver of an entry has the requested type, the
    values of the other receiver are set to NaN.

    Args:
        data_set: Dataset as returned by
            :func:`eval_ac.convert_abscal_his.read_abscal_his`.
        cal_type: Calibration type to keep (default: liquid nitrogen).

    Returns:
        Dataset with the selected calibrations.
    """
    valid = channel_cal_type(data_set) == cal_type
    keep = valid.any('freq').values
    selected = data_set.isel(n_samples=keep)
    valid = valid.isel(n_samples=keep)
    for var in CHANNEL_VARIABLES:
        if var in selected:
            selected[var] = selected[var].where(valid.values,
                                                drop=False)
            selected[var].attrs = data_set[var].attrs
    return selected


def not_calibrated(data_set: xr.Dataset) -> np.ndarray:
    """Returns True for every entry and channel that was not calibrated."""
    if 'calibration_flag' not in data_set:
        return np.zeros((data_set.sizes['n_samples'],
                         data_set.sizes['freq']), dtype=bool)
    return data_set['calibration_flag'].values == FLAG_NOT_CALIBRATED


def valid_samples(values: np.ndarray) -> np.ndarray:
    """Returns the indices of the entries with at least one value."""
    return np.flatnonzero(~np.all(np.isnan(values), axis=1))


def _receiver_drift(values, flagged, n_reference):
    """Drift of one variable and one receiver.

    Returns:
        Tuple ``(reference, deviation, latest, n_used)``.
    """
    # the latest entry is defined without the flags, so that a latest
    # calibration without any calibrated channel is not silently skipped
    samples = valid_samples(values)
    values = np.where(flagged, np.nan, values)
    n_channels = values.shape[1]
    if samples.size == 0:
        return (np.full(n_channels, np.nan), np.full(values.shape, np.nan),
                -1, np.zeros(n_channels, dtype=np.int32))
    latest = samples[-1]
    reference_values = values[samples[-1 - n_reference:-1]]
    with warnings.catch_warnings():
        warnings.simplefilter('ignore', RuntimeWarning)  # all-NaN channels
        reference = np.nanmedian(reference_values, axis=0) \
            if reference_values.size else np.full(n_channels, np.nan)
    deviation = 100 * (values - reference) / reference
    n_used = np.sum(~np.isnan(reference_values), axis=0).astype(np.int32)
    return reference, deviation, latest, n_used


def calibration_drift(data_set: xr.Dataset,
                      variables=CHANNEL_VARIABLES,
                      n_reference: int = DEFAULT_N_REFERENCE) -> xr.Dataset:
    """Compares each calibration with the median of the previous ones.

    For each receiver, the reference is the median of the ``n_reference``
    calibrations before the latest one. Channels that were not calibrated
    (``calibration_flag == 0``) are neither used for the reference nor
    evaluated.

    Args:
        data_set: Dataset, typically after :func:`select_cal_type`.
        variables: Variables to analyse.
        n_reference: Number of calibrations forming the reference.

    Returns:
        Dataset with, for each variable ``var``:

        * ``var_reference`` (freq): reference value,
        * ``var_deviation`` (n_samples, freq): deviation of every entry from
          the reference in percent,

        and ``latest_sample`` (freq): position of the latest entry of each
        channel, ``n_reference_used`` (freq): number of values in the
        reference.
    """
    flagged = not_calibrated(data_set)
    n_samples, n_freq = data_set.sizes['n_samples'], data_set.sizes['freq']
    latest = np.full(n_freq, -1, dtype=np.int32)
    n_used = np.zeros(n_freq, dtype=np.int32)
    drift = xr.Dataset(coords={name: data_set.coords[name]
                               for name in data_set.coords})

    for var in variables:
        reference = np.full(n_freq, np.nan)
        deviation = np.full((n_samples, n_freq), np.nan)
        for mask in receiver_masks(data_set).values():
            (reference[mask], deviation[:, mask], latest[mask],
             n_used[mask]) = _receiver_drift(
                 data_set[var].values[:, mask].astype(float),
                 flagged[:, mask], n_reference)
        long_name = data_set[var].attrs.get('long_name', var)
        drift[f'{var}_reference'] = ('freq', reference, {
            'long_name': f'{long_name}, median of {n_reference} previous '
                         'calibrations',
            'units': data_set[var].attrs.get('units', '')})
        drift[f'{var}_deviation'] = (('n_samples', 'freq'), deviation, {
            'long_name': f'deviation of {long_name} from reference',
            'units': '%'})

    drift['latest_sample'] = ('freq', latest, {
        'long_name': 'position of the latest calibration along n_samples'})
    drift['n_reference_used'] = ('freq', n_used, {
        'long_name': 'number of calibrations in the reference'})
    drift.attrs['n_reference'] = n_reference
    return drift


def latest_not_calibrated(data_set: xr.Dataset, variable='gain') -> list:
    """Lists the channels of the latest calibration with flag 0.

    The latest calibration is determined per receiver.

    Returns:
        List of dictionaries with the keys ``freq`` and ``receiver``.
    """
    flagged = not_calibrated(data_set)
    rows = []
    for number, mask in receiver_masks(data_set).items():
        samples = valid_samples(data_set[variable].values[:, mask]
                                .astype(float))
        if samples.size == 0:
            continue
        for freq in data_set['freq'].values[mask][flagged[samples[-1],
                                                          mask]]:
            rows.append({'freq': float(freq), 'receiver': number})
    return rows


def drift_exceedances(drift: xr.Dataset, thresholds=None) -> list:
    """Lists the channels of the latest calibration exceeding a threshold.

    Args:
        drift: Dataset as returned by :func:`calibration_drift`.
        thresholds: Dictionary ``{variable: threshold in percent}``. Missing
            variables use :data:`DEFAULT_THRESHOLDS`.

    Returns:
        List of dictionaries with the keys ``variable``, ``freq``,
        ``receiver``, ``deviation`` and ``threshold``, sorted by variable
        and frequency.
    """
    thresholds = {**DEFAULT_THRESHOLDS, **(thresholds or {})}
    latest = drift['latest_sample'].values
    rows = []
    for var, threshold in thresholds.items():
        if f'{var}_deviation' not in drift:
            continue
        deviation = drift[f'{var}_deviation'].values
        for channel, sample in enumerate(latest):
            if sample < 0:
                continue
            value = deviation[sample, channel]
            if abs(value) > threshold:  # NaN never exceeds
                rows.append({
                    'variable': var,
                    'freq': float(drift['freq'].values[channel]),
                    'receiver': int(drift['receiver'].values[channel])
                    if 'receiver' in drift.coords else 1,
                    'deviation': float(value),
                    'threshold': float(threshold),
                })
    return rows
