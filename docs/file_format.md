# File format and dataset

## ABSCAL.HIS

`ABSCAL.HIS` is a binary file in the RPG-Radiometer directory of the radiometer PC. It stores all absolute calibrations, including successful sky tipping calibrations (RPG manual RPG-MWR-STD-SW, sections 4.5 and 4.6). The format is described in appendix A20 of the manual. All values are little-endian; `int` is a 4 byte signed integer, `float` a 4 byte IEEE float.

### Header

| Offset | Type | Name in the manual | Description |
| --- | --- | --- | --- |
| 0 | int | HISCode | file code, always 39583209 |
| 4 | int | N | number of calibration entries |

The header is followed by `N` records.

### Record

`N1` and `N2` are the numbers of channels of receiver 1 and 2 and `N = N1 + N2`. The offsets are relative to the start of the record. Variable names are those of the eval_ac dataset (see below).

| Offset | Type | Name in the manual | eval_ac variable | Description |
| --- | --- | --- | --- | --- |
| 0 | int | EntryLen | – | length of the record in bytes, without this field |
| 4 | int | Radiometer-ID | `radiometer_id` | 1 = TEMPRO, 2 = HUMPRO, 3 = HATPRO, 4 = RPG-15-90, 5 = LHATPRO, … |
| 8 | int | Cal1Type | `cal_type_1` | calibration type receiver 1: 0 = no calibration, 1 = liquid nitrogen, 2 = sky tipping |
| 12 | int | Cal2Type | `cal_type_2` | calibration type receiver 2 |
| 16 | int | T1 | `time_of_rec_1` | time of calibration receiver 1, seconds since 2001-01-01 |
| 20 | int | T2 | `time_of_rec_2` | time of calibration receiver 2 |
| 24 | float | ATemp1 | `amb_temp_1` | ambient temperature receiver 1 [K] |
| 28 | float | ATemp2 | `amb_temp_2` | ambient temperature receiver 2 [K] |
| 32 | float | P1 | `press_1` | barometric pressure receiver 1 [mbar] |
| 36 | float | P2 | `press_2` | barometric pressure receiver 2 [mbar] |
| 40 | float | HLTemp1 | `hot_load_temp_1` | hot load temperature receiver 1 [K] |
| 44 | float | HLTemp2 | `hot_load_temp_2` | hot load temperature receiver 2 [K] |
| 48 | float | CLTemp1 | `cold_load_temp_1` | cold load temperature receiver 1 [K] |
| 52 | float | CLTemp2 | `cold_load_temp_2` | cold load temperature receiver 2 [K] |
| 56 | 5 × float | Spare | – | spare |
| 76 | int | NRec1Ch | – | number of channels of receiver 1 (`N1`) |
| 80 | N1 × float | ChF1 | `freq` | frequencies of receiver 1 [GHz] |
| 80 + 4·N1 | int | NRec2Ch | – | number of channels of receiver 2 (`N2`) |
| 84 + 4·N1 | N2 × float | ChF2 | `freq` | frequencies of receiver 2 [GHz] |
| 84 + 4·N | N × int | Calibrated | `calibration_flag` | 0 = not calibrated, 1 = calibrated |
| 84 + 8·N | N × float | Gain | `gain` | receiver gain [V/K] |
| 84 + 12·N | N × float | NoiseT | `temp_noise` | noise diode temperature [K] |
| 84 + 16·N | N × float | TSys | `temp_sys` | system noise temperature [K] |
| 84 + 20·N | N × float | Alpha | `alpha` | non-linearity factor |

A record is `84 + 24·N` bytes long, i.e. 420 bytes for a HATPRO with 7 + 7 channels. The value of `EntryLen` does not include the field itself (416 for a HATPRO); this is not stated in the manual but found in the example file. eval_ac checks the file code, the length of every record and whether the file ends after the last record, and reports truncated files.

## Dataset

{func}`eval_ac.convert_abscal_his.read_abscal_his` returns an {class}`xarray.Dataset` with the dimensions `n_samples` (calibration entries, oldest first) and `freq` (channels of both receivers). {func}`eval_ac.convert_abscal_his.write_netcdf` writes it to a NetCDF file following the CF conventions.

| Name | Dimensions | Units | Description |
| --- | --- | --- | --- |
| `n_samples` (coordinate) | n_samples | | number of the calibration entry |
| `freq` (coordinate) | freq | GHz | frequency |
| `time` (coordinate) | n_samples | | time of calibration (receiver 1), decoded |
| `receiver` (coordinate) | freq | 1 | receiver number (1 or 2) |
| `radiometer_id` | n_samples | 1 | radiometer ID |
| `cal_type_1`, `cal_type_2` | n_samples | 1 | calibration type of receiver 1 and 2 |
| `time_of_rec_1`, `time_of_rec_2` | n_samples | seconds since 2001-01-01 | time of calibration of receiver 1 and 2 |
| `amb_temp_1`, `amb_temp_2` | n_samples | K | ambient temperature |
| `press_1`, `press_2` | n_samples | mbar | barometric pressure |
| `hot_load_temp_1`, `hot_load_temp_2` | n_samples | K | hot load temperature |
| `cold_load_temp_1`, `cold_load_temp_2` | n_samples | K | cold load temperature |
| `calibration_flag` | n_samples, freq | 1 | 0 = not calibrated, 1 = calibrated |
| `gain` | n_samples, freq | V K-1 | receiver gain |
| `temp_noise` | n_samples, freq | K | noise diode temperature |
| `temp_sys` | n_samples, freq | K | system noise temperature |
| `alpha` | n_samples, freq | 1 | non-linearity factor (0.9 ≤ α < 1) |

When the NetCDF file is opened with xarray, `time_of_rec_1` and `time_of_rec_2` are decoded to datetimes because of their `units` attribute.
