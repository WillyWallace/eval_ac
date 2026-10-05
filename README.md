[![Python package](https://github.com/WillyWallace/eval_ac/actions/workflows/python-package.yml/badge.svg)](https://github.com/WillyWallace/eval_ac/actions/workflows/python-package.yml)
[![Pylint](https://github.com/WillyWallace/eval_ac/actions/workflows/pylint.yml/badge.svg)](https://github.com/WillyWallace/eval_ac/actions/workflows/pylint.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Github all releases](https://img.shields.io/github/downloads/WillyWallace/eval_ac/total.svg)](https://github.com/WillyWallace/eval_ac/releases/)
[![Open Source? Yes!](https://badgen.net/badge/Open%20Source%20%3F/Yes%21/blue?icon=github)](https://github.com/Naereen/badges/)
[![Maintenance](https://img.shields.io/badge/Maintained%3F-yes-green.svg)](https://github.com/WillyWallace/eval_ac/graphs/commit-activity)
![Mastodon Follow](https://img.shields.io/mastodon/follow/109461236453474330?domain=https%3A%2F%2Fmeteo.social&logoColor=%230066cc&style=social)

<!-- [![Release][release-shield]][release-url] -->
<!-- [![PyPi version](https://badgen.net/pypi/v/pip/)](https://pypi.com/project/pip) -->

<!-- [![Twitter](https://img.shields.io/twitter/follow/RSAtmos_LIM?style=for-the-badge)](https://twitter.com/RSAtmos_LIM) -->

# Read the ABSCAL.HIS file and visualize the results of the absolute calibration with liquid nitrogen of an RPG microwave radiometer

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li><a href="#Introduction">Introduction</a></li>
    <li><a href="#getting-started">Getting Started</a></li>
    <li><a href="#Usage">Usage</a></li>
    <li><a href="#roadmap">Roadmap</a></li>
    <!-- <li><a href="#contributing">Contributing</a></li> -->
    <li><a href="#license">License</a></li>
    <li><a href="#contact">Contact</a></li>
    <li><a href="#acknowledgments">Acknowledgments</a></li>
  </ol>
</details>

<!-- Introduction -->
## Introduction

This repository was created to display the results of the absolute calibration with liquid nitrogen of the microwave radiometer HATPRO manufactured by Radiometer Physics GmbH. For this purpose, the binary file ABSCAL.HIS is read in and converted into an xarray. Then the receiver gain, the temperature of the noise diode, the temperature of the system noise and the non-linearity factor are displayed in comparison to the previous and other prior calibrations.

<!-- GETTING STARTED -->
## Getting Started

### Installation

eval_ac requires Python 3.9 or newer. The dependencies (numpy, xarray, matplotlib, netCDF4) are installed automatically.

1. Clone the repo
   ```sh
   git clone https://github.com/WillyWallace/eval_ac.git
   cd eval_ac
   ```

2. Install the package
   ```sh
   pip install .
   ```
   For development (editable install with test and lint tools):
   ```sh
   pip install -e ".[dev]"
   ```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->
## Usage

### Command line

```sh
eval-ac path/to/ABSCAL.HIS --netcdf abscal.nc
```

This writes the NetCDF file, the history plot `results_ln2_cal.png`, the drift plot `results_ln2_drift.png` and prints a short quality report of the latest calibration:

```text
read 16 calibration entries from path/to/ABSCAL.HIS
16 of them are calibrations with liquid nitrogen
drift: all channels of the latest calibration are within the thresholds
```

| Option | Description |
| --- | --- |
| `input` | path of the ABSCAL.HIS file (required) |
| `-n`, `--netcdf FILE` | write the converted data (all calibration types) to a NetCDF file |
| `-p`, `--plot FILE` | file name of the history plot (default: `results_ln2_cal.png`) |
| `-d`, `--drift-plot FILE` | file name of the drift plot (default: `results_ln2_drift.png`) |
| `--no-plot` | do not create any plot |
| `--show` | additionally show the plots in a window |
| `--all-cal-types` | use all calibrations instead of only those with liquid nitrogen |
| `--n-reference N` | number of calibrations before the latest one forming the drift reference (default: 5) |
| `-t`, `--threshold VAR=PERCENT` | drift threshold, e.g. `-t gain=8 -t temp_sys=2`; variables: `gain`, `temp_noise`, `temp_sys`, `alpha` |
| `--fail-on-drift` | exit with code 2 if the latest calibration exceeds a threshold (e.g. for cron jobs) |
| `--version` | print the version |

`python -m eval_ac ...` works as well. Try it with the example file:

```sh
eval-ac example_data/ABSCAL.HIS
```

#### History plot

The plot shows the receiver gain, the noise diode temperature, the system noise temperature and the non-linearity factor of both receivers. The latest and the previous calibration of each receiver are highlighted with their dates, all older calibrations are drawn in grey. Channels that were not calibrated (`calibration_flag` = 0) are marked with a red cross. By default, only calibrations with liquid nitrogen are used (`cal_type` = 1); if only one receiver of an entry was calibrated with liquid nitrogen, only this receiver is used.

<img src="docs/images/results_ln2_cal.png" width="70%">

#### Drift plot

For each receiver, the latest calibration is compared with the median of the 5 calibrations before it (deviation in percent). Channels that were not calibrated are excluded. The dashed red lines are the thresholds, channels of the latest calibration exceeding them are circled and listed in the report.

The default thresholds are gain 10 %, noise diode temperature 2.5 %, system noise temperature 2.5 % and non-linearity factor 0.5 %. They correspond to about the 99th percentile of the deviations in the example data of a HATPRO (2018–2026) and should be adapted to your instrument with `--threshold`.

<img src="docs/images/results_ln2_drift.png" width="70%">

### Python

```python
from eval_ac.convert_abscal_his import read_abscal_his, write_netcdf
from eval_ac.analysis import select_cal_type, calibration_drift, drift_exceedances
from eval_ac.plotting import plot_calibration_history, plot_drift

ds = read_abscal_his("ABSCAL.HIS")   # xarray.Dataset, all calibration types
write_netcdf(ds, "abscal.nc")

ln2 = select_cal_type(ds)            # only calibrations with liquid nitrogen
fig = plot_calibration_history(ln2, variables=["gain", "temp_sys"])
fig.savefig("gain_tsys.png")

drift = calibration_drift(ln2, n_reference=5)
for row in drift_exceedances(drift, thresholds={"gain": 8}):
    print(row)
plot_drift(drift, thresholds={"gain": 8}).savefig("drift.png")
```

The dataset has the dimensions `n_samples` (calibration entries, oldest first) and `freq` (channels). The coordinate `time` holds the date of each calibration, the coordinate `receiver` (1 or 2) assigns each channel to its receiver.

### Running the tests

```sh
pip install -e ".[test]"
pytest
```

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ROADMAP -->
## Roadmap

- [x] add meaningful docstrings
- [ ] make documentation --> readthedocs
- [x] enable pip install ...
- [ ] publish on PyPI
- [ ] Released version 1
- [x] Add Tests

See the [open issues](https://github.com/WillyWallace/eval_ac/issues) for a full list of proposed features (and known issues) and [CHANGELOG.md](CHANGELOG.md) for the changes of each version.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.

<p align="right">(<a href="#top">back to top</a>)</p>

<!-- CONTACT -->
## Contact

[Andreas Foth](https://www.uni-leipzig.de/personenprofil/mitarbeiter/dr-andreas-foth)


<p align="right">(<a href="#top">back to top</a>)</p>

<!-- ACKNOWLEDGMENTS -->
## Acknowledgments

Special thanks for templates and help during implementation.

* [Readme Template](https://github.com/othneildrew/Best-README-Template)
* [cloudnetpy GitHub](https://github.com/actris-cloudnet/cloudnetpy.git)

<p align="right">(<a href="#top">back to top</a>)</p>

