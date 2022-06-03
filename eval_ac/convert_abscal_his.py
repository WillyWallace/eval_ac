"""This file contains the read and conversion routines"""

import datetime
import numpy as np
import xarray as xr
from eval_ac.utils.attributes import FIELDS, ATTRIBUTES


class HatproBinAbscalHis:
    """HATPRO binary file reader."""

    def __init__(self, filename):
        self._file_position = None
        self.filename = filename
        # self._file_position = 0
        self.header = self.read_header()
        self.data = self.read_data()
        self.xrdata = self.convert_to_xarray()
        self.xrdata = self.add_var_attrs()
        self.xrdata = self.add_global_attrs()

        # write netcdf file
        self.write_nc()

    def aff_global_attrs(self):
        """Adds global attributes"""
        self.xrdata.attrs['history'] = 'Data converted from ' + self.filename
        self.xrdata.attrs['source'] = str('micorwave radiometer manufactured '
                                          + 'by Radiometer Physics GmbH (RPG)')
        self.xrdata.attrs['comments'] = ''
        self.xrdata.attrs['conventions'] = 'CF-1.8'
        self.xrdata.attrs['date of creation'] = str(datetime.datetime.utcnow())

        return self.xrdata

    def add_var_attrs(self):
        """Adds attributes"""
        for var in self.xrdata.data_vars:
            add_attrs(var, self.xrdata)

        for var in self.xrdata.coords:
            add_attrs(var, self.xrdata)

        return self.xrdata

    def read_header(self) -> dict:
        """Reads the header."""
        with open(self.filename, 'rb') as file:
            header = {
                'file_code': np.fromfile(file, np.int32, 1),
                '_n_samples': np.fromfile(file, np.int32, 1),
            }
            self._file_position = file.tell()
            file.close()
        return header

    def read_data(self) -> dict:
        """Reads the data."""
        with open(self.filename, 'rb') as file:
            file.seek(self._file_position)

            data = {
                'entry_len': np.zeros(self.header['_n_samples'],
                                      dtype=np.int32).tolist(),
                'radiometer_id': np.zeros(self.header['_n_samples'],
                                          dtype=np.int32).tolist(),
                'cal_type_1': np.zeros(self.header['_n_samples'],
                                       dtype=np.int32).tolist(),
                'cal_type_2': np.zeros(self.header['_n_samples'],
                                       dtype=np.int32).tolist(),
                'time_of_rec_1': np.zeros(self.header['_n_samples'],
                                          dtype=np.int32).tolist(),
                'time_of_rec_2': np.zeros(self.header['_n_samples'],
                                          dtype=np.int32).tolist(),
                'Amb_temp_1': np.zeros(self.header['_n_samples'],
                                       dtype=np.float32).tolist(),
                'Amb_temp_2': np.zeros(self.header['_n_samples'],
                                       dtype=np.float32).tolist(),
                'press_1': np.zeros(self.header['_n_samples'],
                                    dtype=np.float32).tolist(),
                'press_2': np.zeros(self.header['_n_samples'],
                                    dtype=np.float32).tolist(),

                'hot_load_temp_1': np.zeros(self.header['_n_samples'],
                                            dtype=np.float32).tolist(),
                'hot_load_temp_2': np.zeros(self.header['_n_samples'],
                                            dtype=np.float32).tolist(),
                'cold_load_temp_1': np.zeros(self.header['_n_samples'],
                                             dtype=np.float32).tolist(),
                'cold_load_temp_2': np.zeros(self.header['_n_samples'],
                                             dtype=np.float32).tolist(),

                'Spare': np.zeros((self.header['_n_samples'][0], 5),
                                  dtype=np.float32).tolist(),

                'N_rec_1': np.zeros(self.header['_n_samples'],
                                    dtype=np.int32).tolist(),
                'Freq_rec_1': np.zeros((self.header['_n_samples'][0], 14),
                                       dtype=np.float32).tolist(),
                'N_rec_2': np.zeros(self.header['_n_samples'],
                                    dtype=np.int32).tolist(),
                'Freq_rec_2': np.zeros((self.header['_n_samples'][0], 14),
                                       dtype=np.float32).tolist(),

                'flag': np.zeros((self.header['_n_samples'][0], 28),
                                 dtype=np.int32).tolist(),
                'gain': np.zeros((self.header['_n_samples'][0], 28),
                                 dtype=np.float32).tolist(),
                'temp_noise': np.zeros((self.header['_n_samples'][0], 28),
                                       dtype=np.float32).tolist(),
                'temp_sys': np.zeros((self.header['_n_samples'][0], 28),
                                     dtype=np.float32).tolist(),
                'alpha': np.zeros((self.header['_n_samples'][0], 28),
                                  dtype=np.float32).tolist(),
            }

            for sample in range(self.header['_n_samples'][0]):
                data['entry_len'][sample] = np.fromfile(file, np.int32, 1)
                data['radiometer_id'][sample] = np.fromfile(file, np.int32, 1)

                data['cal_type_1'][sample] = np.fromfile(file, np.int32, 1)
                data['cal_type_2'][sample] = np.fromfile(file, np.int32, 1)
                data['time_of_rec_1'][sample] = np.fromfile(file, np.int32, 1)
                data['time_of_rec_2'][sample] = np.fromfile(file, np.int32, 1)
                data['Amb_temp_1'][sample] = np.fromfile(file, np.float32, 1)
                data['Amb_temp_2'][sample] = np.fromfile(file, np.float32, 1)
                data['press_1'][sample] = np.fromfile(file, np.float32, 1)
                data['press_2'][sample] = np.fromfile(file, np.float32, 1)

                data['hot_load_temp_1'][sample] = np.fromfile(
                    file, np.float32, 1)
                data['hot_load_temp_2'][sample] = np.fromfile(
                    file, np.float32, 1)
                data['cold_load_temp_1'][sample] = np.fromfile(file,
                                                               np.float32, 1)
                data['cold_load_temp_2'][sample] = np.fromfile(file,
                                                               np.float32, 1)

                data['Spare'][sample] = np.fromfile(file, np.float32, 5)

                data['N_rec_1'][sample] = np.fromfile(file, np.int32, 1)
                data['Freq_rec_1'][sample] = np.fromfile(
                    file, np.float32,
                    int(data['N_rec_1'][sample][0]))
                data['N_rec_2'][sample] = np.fromfile(file, np.int32, 1)
                data['Freq_rec_2'][sample] = np.fromfile(
                    file, np.float32,
                    int(data['N_rec_2'][sample][0]))

                data['flag'][sample] = np.fromfile(
                    file, np.int32,
                    int(data['N_rec_1'][sample][0])
                    + int(data['N_rec_2'][sample][0]))
                data['gain'][sample] = np.fromfile(
                    file, np.float32,
                    int(data['N_rec_1'][sample][0])
                    + int(data['N_rec_2'][sample][0]))
                data['temp_noise'][sample] = np.fromfile(
                    file, np.float32,
                    int(data['N_rec_1'][sample][0])
                    + int(data['N_rec_2'][sample][0]))
                data['temp_sys'][sample] = np.fromfile(
                    file, np.float32,
                    int(data['N_rec_1'][sample][0])
                    + int(data['N_rec_2'][sample][0]))
                data['alpha'][sample] = np.fromfile(
                    file, np.float32,
                    int(data['N_rec_1'][sample][0])
                    + int(data['N_rec_2'][sample][0]))

            file.close()

        return data

    def convert_to_xarray(self):
        """Converts dict to xarray"""

        data_set = xr.Dataset(
            {
                'radiometer_id': (['n_samples'],
                                  np.asarray(
                                      self.data['radiometer_id'])[:, 0]),
                'cal_type_1': (['n_samples'],
                               np.asarray(
                                   self.data['cal_type_1'])[:, 0]),
                'cal_type_2': (['n_samples'],
                               np.asarray(
                                   self.data['cal_type_2'])[:, 0]),
                'time_of_rec_1': (['n_samples'],
                                  np.asarray(
                                      self.data['time_of_rec_1'])[:, 0]),
                'time_of_rec_2': (['n_samples'],
                                  np.asarray(
                                      self.data['time_of_rec_2'])[:, 0]),
                'amb_temp_1': (['n_samples'],
                               np.asarray(
                                   self.data['Amb_temp_1'])[:, 0]),
                'amb_temp_2': (['n_samples'],
                               np.asarray(self.data['Amb_temp_2'])[:, 0]),
                'press_1': (['n_samples'],
                            np.asarray(self.data['press_1'])[:, 0]),
                'press_2': (['n_samples'],
                            np.asarray(self.data['press_2'])[:, 0]),

                'hot_load_temp_1': (['n_samples'],
                                    np.asarray(
                                        self.data['hot_load_temp_1']
                                    )[:, 0]),
                'hot_load_temp_2': (['n_samples'],
                                    np.asarray(
                                        self.data['hot_load_temp_2']
                                    )[:, 0]),
                'cold_load_temp_1': (['n_samples'],
                                     np.asarray(
                                         self.data['cold_load_temp_1']
                                     )[:, 0]),
                'cold_load_temp_2': (['n_samples'],
                                     np.asarray(
                                         self.data['cold_load_temp_2']
                                     )[:, 0]),

                'calibration_flag': (['n_samples', 'freq'],
                                     np.asarray(self.data['flag'])[:, :]),
                'gain': (['n_samples', 'freq'],
                         np.asarray(self.data['gain'])[:, :]),
                'temp_noise': (['n_samples', 'freq'],
                               np.asarray(self.data['temp_noise'])[:, :]),
                'temp_sys': (['n_samples', 'freq'],
                             np.asarray(self.data['temp_sys'])[:, :]),
                'alpha': (['n_samples', 'freq'],
                          np.asarray(self.data['alpha'])[:, :]),
            },
            coords={
                'n_samples': np.arange(self.header['_n_samples'][0]),

                # 'freq_rec_1' : np.asarray(self.data['Freq_rec_1'])[0,0,:],
                # 'freq_rec_2' : np.asarray(self.data['Freq_rec_2'])[0,0,:],
                'freq': np.concatenate(
                    (np.asarray(self.data['Freq_rec_1'])[0, :],
                     np.asarray(self.data['Freq_rec_2'])[0, :]), axis=None),

            }
        )

        return data_set

    def _get_hatpro_version(self) -> int:
        """Get HATPRO version"""
        if self.header['file_code'][0] == 39583209:
            return 1
        # if self.header['file_code'][0] == 934501000:
            # return 2
        raise ValueError('Unknown HATPRO version.'
                         + f'{self.header["file_code"][0]}')


def add_attrs(var, data_set):
    """Loop over attributes"""
    if var in ATTRIBUTES:
        j = 0
        for i in ATTRIBUTES[var]:
            if i is not None:
                # print(field[j])
                # print(i)
                data_set[var].attrs[FIELDS[j]] = i
            j = j + 1
    return data_set
