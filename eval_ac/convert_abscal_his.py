"""Read the binary ABSCAL.HIS file of RPG microwave radiometers.

The ABSCAL.HIS file contains the history of all absolute calibrations
(e.g. with liquid nitrogen) of a Radiometer Physics GmbH (RPG) microwave
radiometer such as HATPRO.

Typical usage::

    from eval_ac.convert_abscal_his import read_abscal_his, write_netcdf

    ds = read_abscal_his('ABSCAL.HIS')
    write_netcdf(ds, 'abscal.nc')
"""

import datetime
import warnings
from pathlib import Path

import numpy as np
import xarray as xr

from eval_ac import __version__
from eval_ac.utils.attributes import FIELDS, ATTRIBUTES

#: File code (magic number) identifying an ABSCAL.HIS file.
FILE_CODE_ABSCAL_HIS = 39583209

#: Reference time of the RPG time stamps (seconds since this date, UTC).
TIME_REFERENCE = np.datetime64('2001-01-01T00:00:00', 's')

_INT = np.dtype('<i4')
_FLOAT = np.dtype('<f4')

# scalar fields at the start of each record: (name, dtype)
_RECORD_SCALARS = (
    ('radiometer_id', _INT),
    ('cal_type_1', _INT),
    ('cal_type_2', _INT),
    ('time_of_rec_1', _INT),
    ('time_of_rec_2', _INT),
    ('amb_temp_1', _FLOAT),
    ('amb_temp_2', _FLOAT),
    ('press_1', _FLOAT),
    ('press_2', _FLOAT),
    ('hot_load_temp_1', _FLOAT),
    ('hot_load_temp_2', _FLOAT),
    ('cold_load_temp_1', _FLOAT),
    ('cold_load_temp_2', _FLOAT),
)

# per-channel fields at the end of each record: (name, dtype)
_RECORD_CHANNELS = (
    ('calibration_flag', _INT),
    ('gain', _FLOAT),
    ('temp_noise', _FLOAT),
    ('temp_sys', _FLOAT),
    ('alpha', _FLOAT),
)

_N_SPARE = 5


class _BinaryCursor:
    """Sequential reader on an in-memory byte buffer."""

    def __init__(self, buffer: bytes, filename):
        self.buffer = buffer
        self.filename = filename
        self.position = 0

    def read(self, dtype: np.dtype, count: int = 1) -> np.ndarray:
        """Reads ``count`` values of type ``dtype`` and advances the cursor."""
        n_bytes = dtype.itemsize * count
        if self.position + n_bytes > len(self.buffer):
            raise ValueError(
                f'{self.filename}: unexpected end of file at byte '
                f'{self.position} (file size {len(self.buffer)} bytes). '
                'The file seems to be truncated or corrupt.')
        values = np.frombuffer(self.buffer, dtype=dtype, count=count,
                               offset=self.position)
        self.position += n_bytes
        return values

    def read_scalar(self, dtype: np.dtype):
        """Reads a single value."""
        return self.read(dtype, 1)[0]


def read_header(cursor: _BinaryCursor) -> dict:
    """Reads and validates the file header.

    Args:
        cursor: Cursor positioned at the start of the file.

    Returns:
        Dictionary with ``file_code`` and ``n_samples``.

    Raises:
        ValueError: If the file code does not identify an ABSCAL.HIS file.
    """
    header = {
        'file_code': int(cursor.read_scalar(_INT)),
        'n_samples': int(cursor.read_scalar(_INT)),
    }
    if header['file_code'] != FILE_CODE_ABSCAL_HIS:
        raise ValueError(
            f'{cursor.filename}: unknown file code {header["file_code"]} '
            f'(expected {FILE_CODE_ABSCAL_HIS}). '
            'This does not seem to be an RPG ABSCAL.HIS file.')
    return header


def read_record(cursor: _BinaryCursor) -> dict:
    """Reads one calibration entry.

    Args:
        cursor: Cursor positioned at the start of a record.

    Returns:
        Dictionary with the scalar values and the per-channel arrays of
        one calibration.

    Raises:
        ValueError: If the record length stored in the file does not match
            the number of bytes read.
    """
    entry_len = int(cursor.read_scalar(_INT))
    start = cursor.position

    record = {name: cursor.read_scalar(dtype)
              for name, dtype in _RECORD_SCALARS}
    record['spare'] = cursor.read(_FLOAT, _N_SPARE)

    record['n_rec_1'] = int(cursor.read_scalar(_INT))
    record['freq_rec_1'] = cursor.read(_FLOAT, record['n_rec_1'])
    record['n_rec_2'] = int(cursor.read_scalar(_INT))
    record['freq_rec_2'] = cursor.read(_FLOAT, record['n_rec_2'])

    n_channels = record['n_rec_1'] + record['n_rec_2']
    for name, dtype in _RECORD_CHANNELS:
        record[name] = cursor.read(dtype, n_channels)

    if cursor.position - start != entry_len:
        raise ValueError(
            f'{cursor.filename}: record at byte {start - 4} has length '
            f'{cursor.position - start}, but the file states {entry_len}.')
    return record


def read_raw(filename) -> tuple:
    """Reads the ABSCAL.HIS file without any conversion.

    Args:
        filename: Path of the ABSCAL.HIS file.

    Returns:
        Tuple ``(header, records)`` with the header dictionary and a list
        of one dictionary per calibration entry.
    """
    buffer = Path(filename).read_bytes()
    cursor = _BinaryCursor(buffer, filename)
    header = read_header(cursor)
    records = [read_record(cursor) for _ in range(header['n_samples'])]
    if cursor.position != len(buffer):
        warnings.warn(
            f'{filename}: {len(buffer) - cursor.position} unread bytes at the '
            'end of the file.', stacklevel=2)
    return header, records


def _check_channels(records: list, filename) -> tuple:
    """Checks that all entries share the same channels.

    Returns:
        Tuple ``(freq_rec_1, freq_rec_2)`` of the first entry.
    """
    first = records[0]
    for i, record in enumerate(records[1:], start=1):
        if (record['n_rec_1'], record['n_rec_2']) != (first['n_rec_1'],
                                                      first['n_rec_2']):
            raise ValueError(
                f'{filename}: entry {i} has a different number of channels '
                f'({record["n_rec_1"]}+{record["n_rec_2"]}) than entry 0 '
                f'({first["n_rec_1"]}+{first["n_rec_2"]}).')
        if not (np.allclose(record['freq_rec_1'], first['freq_rec_1'])
                and np.allclose(record['freq_rec_2'], first['freq_rec_2'])):
            warnings.warn(
                f'{filename}: frequencies of entry {i} differ from entry 0. '
                'The frequencies of entry 0 are used.', stacklevel=3)
    return first['freq_rec_1'], first['freq_rec_2']


def records_to_dataset(header: dict, records: list, filename='') -> xr.Dataset:
    """Converts the raw records into an xarray Dataset with attributes.

    Args:
        header: Header dictionary as returned by :func:`read_raw`.
        records: List of records as returned by :func:`read_raw`.
        filename: Name of the source file, written to the history attribute.

    Returns:
        Dataset with dimensions ``n_samples`` (calibration entries) and
        ``freq`` (channels).
    """
    if not records:
        raise ValueError(f'{filename}: the file contains no calibration '
                         'entries.')
    freq_rec_1, freq_rec_2 = _check_channels(records, filename)

    data_vars = {
        name: (['n_samples'], np.array([rec[name] for rec in records]))
        for name, _ in _RECORD_SCALARS
    }
    data_vars.update({
        name: (['n_samples', 'freq'],
               np.stack([rec[name] for rec in records]))
        for name, _ in _RECORD_CHANNELS
    })

    seconds = data_vars['time_of_rec_1'][1].astype('timedelta64[s]')
    data_set = xr.Dataset(
        data_vars,
        coords={
            'n_samples': np.arange(header['n_samples']),
            'freq': np.concatenate((freq_rec_1, freq_rec_2)),
            'time': (['n_samples'],
                     (TIME_REFERENCE + seconds).astype('datetime64[ns]')),
            'receiver': (['freq'],
                         np.repeat(np.int32([1, 2]),
                                   [len(freq_rec_1), len(freq_rec_2)])),
        },
    )
    data_set['time'].encoding['units'] = 'seconds since 2001-01-01'

    for var in data_set.variables:
        add_attrs(var, data_set)
    add_global_attrs(data_set, filename)
    return data_set


def read_abscal_his(filename) -> xr.Dataset:
    """Reads an ABSCAL.HIS file into an xarray Dataset.

    Args:
        filename: Path of the ABSCAL.HIS file.

    Returns:
        Dataset with the calibration history, see
        :func:`records_to_dataset`.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file is not a valid ABSCAL.HIS file.
    """
    header, records = read_raw(filename)
    return records_to_dataset(header, records, filename)


def write_netcdf(data_set: xr.Dataset, filename) -> None:
    """Writes the dataset to a NetCDF file."""
    data_set.to_netcdf(filename)


def add_global_attrs(data_set: xr.Dataset, filename='') -> xr.Dataset:
    """Adds global attributes (in place)."""
    now = datetime.datetime.now(datetime.timezone.utc)
    timestamp = now.strftime('%Y-%m-%dT%H:%M:%SZ')
    data_set.attrs['Conventions'] = 'CF-1.8'
    data_set.attrs['title'] = ('Absolute calibration history of an RPG '
                               'microwave radiometer')
    data_set.attrs['source'] = ('microwave radiometer manufactured by '
                                'Radiometer Physics GmbH (RPG)')
    data_set.attrs['history'] = (f'{timestamp}: converted from {filename} '
                                 f'with eval_ac {__version__}')
    data_set.attrs['date_created'] = timestamp
    return data_set


def add_attrs(var, data_set):
    """Adds the attributes defined in ``ATTRIBUTES`` to variable ``var``."""
    if var in ATTRIBUTES:
        for field, value in zip(FIELDS, ATTRIBUTES[var]):
            if value is not None:
                data_set[var].attrs[field] = value
    return data_set


class HatproBinAbscalHis:  # pylint: disable=too-few-public-methods
    """HATPRO ABSCAL.HIS file reader.

    Kept for backwards compatibility. New code should use
    :func:`read_abscal_his` and :func:`write_netcdf`.

    Args:
        filename: Path of the ABSCAL.HIS file.
        filename_out: Optional path of a NetCDF file. If given, the data
            is written to this file.

    Attributes:
        header: Header dictionary.
        data: List of raw records (one dictionary per calibration entry).
        xrdata: Converted :class:`xarray.Dataset`.
    """

    def __init__(self, filename, filename_out=None):
        self.filename = filename
        self.filename_out = filename_out
        self.header, self.data = read_raw(filename)
        self.xrdata = records_to_dataset(self.header, self.data, filename)
        if filename_out is not None:
            self.write_nc()

    def write_nc(self, filename_out=None):
        """Writes the dataset to a NetCDF file."""
        write_netcdf(self.xrdata, filename_out or self.filename_out)
