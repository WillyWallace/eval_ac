"""
this file contains the unit test routines
"""
# import pytest
from eval_ac.convert_abscal_his import HatproBinAbscalHis


file = '../example_data/ABSCAL.HIS'


def test_HatproBinAbscalHis():
    obj = HatproBinAbscalHis(file)
    assert obj.filename == file
    assert 'gain' in obj.xrdata == True
    assert 'temp_noise' in obj.xrdata == True
    assert 'temp_sys' in obj.xrdata == True
    assert 'alpha' in obj.xrdata == True
