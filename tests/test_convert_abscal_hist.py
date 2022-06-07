"""
this file contains the unit test routines
"""
# import pytest
from eval_ac.convert_abscal_his import HatproBinAbscalHis


FILE = '../example_data/ABSCAL.HIS'


def test_hatpro_bin_abscal_his():
    '''unit test of the HatproBinAbscalHis class'''
    obj = HatproBinAbscalHis(FILE)
    assert obj.filename == FILE
    assert 'gain' in obj.xrdata == True
    assert 'temp_noise' in obj.xrdata == True
    assert 'temp_sys' in obj.xrdata == True
    assert 'alpha' in obj.xrdata == True
