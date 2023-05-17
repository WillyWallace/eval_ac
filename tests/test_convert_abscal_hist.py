"""
this file contains the unit test routines
"""
# import pytest
from eval_ac.convert_abscal_his import HatproBinAbscalHis


FILE = '../example_data/ABSCAL.HIS'


def test_hatpro_bin_abscal_his():
    '''unit test for main class'''
    obj = HatproBinAbscalHis(FILE)
    assert obj.filename is FILE
    assert ('gain' in obj.xrdata) is True
    assert ('temp_noise' in obj.xrdata) is True
    assert ('temp_sys' in obj.xrdata) is True
    assert ('alpha' in obj.xrdata) is True
