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
eval-ac path/to/ABSCAL.HIS --netcdf abscal.nc --plot results_ln2_cal.png
```

| Option | Description |
| --- | --- |
| `input` | path of the ABSCAL.HIS file (required) |
| `-n`, `--netcdf FILE` | write the converted data to a NetCDF file |
| `-p`, `--plot FILE` | file name of the plot (default: `results_ln2_cal.png`) |
| `--no-plot` | do not create a plot |
| `--show` | additionally show the plot in a window |
| `--version` | print the version |

`python -m eval_ac ...` works as well. Try it with the example file:

```sh
eval-ac example_data/ABSCAL.HIS
```

The plot shows the receiver gain, the noise diode temperature, the system noise temperature and the non-linearity factor of both receivers. The latest and the previous calibration are highlighted with their dates, all older calibrations are drawn in grey.

<img src="docs/images/results_ln2_cal.png" width="70%">

### Python

```python
from eval_ac.convert_abscal_his import read_abscal_his, write_netcdf
from eval_ac.plotting import plot_calibration_history

ds = read_abscal_his("ABSCAL.HIS")   # xarray.Dataset
write_netcdf(ds, "abscal.nc")

fig = plot_calibration_history(ds, variables=["gain", "temp_sys"])
fig.savefig("gain_tsys.png")
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

- [ ] add meaningful docstrings (partly done in 0.2.0)
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

