"""
this file contains the unit test routines
"""
import pytest
from eval_ac import convert_abscal_his


FILE = '../example_data/ABSCAL.HIS'

def test_HatproBinAbscalHis(FILE):
    obj = convert_abscal_his.HatproBinAbscalHis(FILE)
    assert obj.filename == 'ABSCAL.HIS'

