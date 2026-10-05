"""
Visualizes the results of the absolute calibration with liquid nitrogen of
the microwave radiometer HATPRO from RPG.

Kept for backwards compatibility, use the ``eval-ac`` command instead::

    eval-ac ABSCAL.HIS --netcdf abscal.nc --plot results_ln2_cal.png
"""
import sys

from eval_ac.cli import main

if __name__ == '__main__':
    sys.exit(main())
