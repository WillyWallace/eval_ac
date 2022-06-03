"""
this file contains the unit test routines
"""
<<<<<<< HEAD
# import pytest
from eval_ac.convert_abscal_his import HatproBinAbscalHis
=======
import pytest
from eval_ac import convert_abscal_his
>>>>>>> 7f6339c (add first unit test)


FILE = '../example_data/ABSCAL.HIS'

<<<<<<< HEAD

def test_hatpro_bin_abscal_his():
    '''unit test of the HatproBinAbscalHis class'''
    obj = HatproBinAbscalHis(FILE)
    assert obj.filename == FILE
    assert 'gain' in obj.xrdata == True
    assert 'temp_noise' in obj.xrdata == True
    assert 'temp_sys' in obj.xrdata == True
    assert 'alpha' in obj.xrdata == True
=======
def test_HatproBinAbscalHis(FILE):
    obj = convert_abscal_his.HatproBinAbscalHis(FILE)
    assert obj.filename == 'ABSCAL.HIS'

>>>>>>> 7f6339c (add first unit test)
