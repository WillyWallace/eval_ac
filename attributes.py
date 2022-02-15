"""This files contains the meta data definitions"""
from collections import namedtuple

FIELDS = (
    'long_name',
    'standard_name',
    'units',
    'comment',
    'definition',
    'references',
    'ancillary_variables',
    'positive',
    'axis',
    'calendar',
    'source')

MetaData = namedtuple('MetaData', FIELDS, defaults=(None,) * len(FIELDS))


DEFINITIONS = {
    'radiometer_id':
        ('Value 1: TEMPRO\n'
         'Value 2: HUMPRO\n'
         'Value 3: HATPRO\n'
         'Value 4: RPG-15-90\n'
         'Value 5: LHATPRO\n'
         'Value 6: RPG-150-90\n'
         'Value 7: RPG-36-90\n'
         'Value 8: RPG-LWP\n'
         'Value 9: RPG-LWP-U90\n'
         'Value 10: RPG-DP150-90\n'
         'Value 11: HALO-KV\n'
         'Value 12: HALO-183\n'
         'Value 13: HALO-119-90\n'),
    'calibration_type':
        ('Value 0: no calibration\n'
         'Value 1: Absolute calibration with liquid nitrogen \n'
         'Value 2: Sky tipping calibration'),
    'retrieval_method':
        ('Value 0: Linear Regression\n'
         'Value 1: Quadratic Regression\n'
         'Value 2: Neural Network'),
    'calibration_flag':
        ('value 0: not calibrated\n'
         'values 1: calibrated'),
}

ATTRIBUTES = {
    'file_code': MetaData(
        long_name='File code',
        comment='RPG HATPRO software version.',
        units="1"
    ),
    'n_samples': MetaData(
        long_name='Number of calibration entries',
    ),
    'radiometer_id': MetaData(
        long_name='Radiometer ID',
        definition=DEFINITIONS['radiometer_id'],
        units='1'
    ),
    'cal_type_1': MetaData(
        long_name='Calibration type receiver 1',
        definition=DEFINITIONS['calibration_type'],
        units='1'
    ),
    'cal_type_2': MetaData(
        long_name='Calibration type receiver 2',
        definition=DEFINITIONS['calibration_type'],
        units='1'
    ),
    'time_of_rec_1': MetaData(
        long_name='time of calibration receiver 1',
        units='seconds since 2001-01-01'
    ),
    'time_of_rec_2': MetaData(
        long_name='time of calibration receiver 2',
        units='seconds since 2001-01-01'
    ),
    'amb_temp_1': MetaData(
        long_name='ambient temperature receiver 1',
        units='K'
    ),
    'amb_temp_2': MetaData(
        long_name='ambient temperature receiver 2',
        units='K'
    ),
    'press_1': MetaData(
        long_name='barom. pressure receiver 1',
        units='mbar'
    ),
    'press_2': MetaData(
        long_name='barom. pressure receiver 2',
        units='mbar'
    ),
    'hot_load_temp_1': MetaData(
        long_name='hot load temperature receiver 1',
        units='K'
    ),
    'hot_load_temp_2': MetaData(
        long_name='hot load temperature receiver 2',
        units='K'
    ),
    'cold_load_temp_1': MetaData(
        long_name='hot load temperature receiver 1',
        units='K'
    ),
    'cold_load_temp_2': MetaData(
        long_name='hot load temperature receiver 2',
        units='K'
    ),
    'N_rec_1': MetaData(
        long_name='number of receiver 1 channels',
        units='1'
    ),
    'N_rec_2': MetaData(
        long_name='number of receiver 2 channels',
        units='1'
    ),
    'freq_rec_1': MetaData(
        long_name='frequencies of receiver 1',
        units='GHz'
    ),
    'freq_rec_2': MetaData(
        long_name='frequencies of receiver 2',
        units='GHz'
    ),
    'freq': MetaData(
        long_name='frequency',
        units='GHz'
    ),
    'gain': MetaData(
        standard_name='reveiver gain',
        long_name='receiver gain',
        units='V K-1'
    ),
    'temp_noise': MetaData(
        long_name='noise diode temperature',
        units='K'
    ),
    'temp_sys': MetaData(
        long_name='system noise temperature',
        units='K'
    ),
    'alpha': MetaData(
        long_name='non-linearity factor',
        units='K'
    ),
    'calibration_flag': MetaData(
        long_name='calibration flags',
        definition=DEFINITIONS['calibration_flag'],
        units='1',
        comment='Quality information as an 8 bit array.'
        + ' See RPG HATPRO manual for more information.'
    )

}
