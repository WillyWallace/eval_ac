# Read the ABSCAL.HIS file and visualize the results of the absolute calibration with liquid nitrogen of an RPG microwave radiometer

<img src="results_ln2_cal.png">

<!-- GETTING STARTED -->
## Getting Started

The examples given use hourly radar spectra files in there specific file formats, i.e. LV0 binaries form RPG-FMCW94 and NetCDF files from KAZR. Th Cloudnet categorization file provides the temporal resolution where the high resolution radar profiels are mappend onto the 30 sec Cloudnet grid. Additionately, radar reflectivity and attenuated backscatter coefficient are plotted.


### Installation

_Below is an example of how run the example script, which prepares the data, makes predictions and plots quicklooks. This method relies on external dependencies such as torch, xarray and others (see `setup.py`)._

1. Clone the repo
   ```sh
   git clone https://github.com/remsens-lim/Voodoo.git
   ```

2. Install the package
   ```sh
   python setup.py install
   ```

<p align="right">(<a href="#top">back to top</a>)</p>
