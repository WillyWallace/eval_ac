"""Command line interface of eval_ac.

Example::

    eval-ac ABSCAL.HIS --netcdf abscal.nc --plot results_ln2_cal.png
"""

import argparse
import sys

from eval_ac import __version__

#: Exit code if the latest calibration exceeds a drift threshold and
#: ``--fail-on-drift`` is given.
EXIT_DRIFT = 2


def _threshold(text: str) -> tuple:
    """Parses 'VARIABLE=PERCENT'."""
    # pylint: disable=import-outside-toplevel
    from eval_ac.analysis import DEFAULT_THRESHOLDS
    try:
        name, value = text.split('=')
        value = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError(
            f'expected VARIABLE=PERCENT, got {text!r}') from error
    if name not in DEFAULT_THRESHOLDS:
        raise argparse.ArgumentTypeError(
            f'unknown variable {name!r}, choose from '
            f'{", ".join(DEFAULT_THRESHOLDS)}')
    return name, value


def build_parser() -> argparse.ArgumentParser:
    """Creates the argument parser."""
    parser = argparse.ArgumentParser(
        prog='eval-ac',
        description='Read the ABSCAL.HIS file of an RPG microwave radiometer '
                    '(e.g. HATPRO) and plot the history of the absolute '
                    'calibration with liquid nitrogen.')
    parser.add_argument('input', help='path of the ABSCAL.HIS file')
    parser.add_argument('-n', '--netcdf', metavar='FILE',
                        help='write the converted data (all calibration '
                             'types) to this NetCDF file')
    parser.add_argument('-p', '--plot', metavar='FILE',
                        default='results_ln2_cal.png',
                        help='save the history plot to this file '
                             '(default: %(default)s)')
    parser.add_argument('-d', '--drift-plot', metavar='FILE',
                        default='results_ln2_drift.png',
                        help='save the drift plot to this file '
                             '(default: %(default)s)')
    parser.add_argument('--no-plot', action='store_true',
                        help='do not create any plot')
    parser.add_argument('--show', action='store_true',
                        help='show the plots in a window')
    parser.add_argument('--all-cal-types', action='store_true',
                        help='use all calibrations instead of only those '
                             'with liquid nitrogen')

    drift = parser.add_argument_group('drift analysis')
    drift.add_argument('--n-reference', type=int, default=5, metavar='N',
                       help='number of calibrations before the latest one '
                            'forming the reference (default: %(default)s)')
    drift.add_argument('-t', '--threshold', type=_threshold, action='append',
                       default=[], metavar='VARIABLE=PERCENT',
                       help='drift threshold in percent, e.g. gain=8; can be '
                            'given several times (defaults: gain=10, '
                            'temp_noise=2.5, temp_sys=2.5, alpha=0.5)')
    drift.add_argument('--fail-on-drift', action='store_true',
                       help=f'exit with code {EXIT_DRIFT} if the latest '
                            'calibration exceeds a threshold')

    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {__version__}')
    return parser


def _print_report(data_set, exceedances, flagged):
    """Prints the quality and drift summary of the latest calibration."""
    units = data_set['freq'].attrs.get('units', '')
    if flagged:
        print(f'warning: {len(flagged)} channel(s) of the latest calibration '
              'were not calibrated (flag 0):')
        for row in flagged:
            print(f'  {row["freq"]:7.2f} {units}  receiver {row["receiver"]}')
    if not exceedances:
        print('drift: all channels of the latest calibration are within '
              'the thresholds')
        return
    print(f'warning: {len(exceedances)} channel(s) of the latest '
          'calibration exceed the drift threshold:')
    for row in exceedances:
        print(f'  {row["variable"]:<11} {row["freq"]:7.2f} {units}  '
              f'receiver {row["receiver"]}  {row["deviation"]:+7.2f} % '
              f'(threshold ±{row["threshold"]:g} %)')


def _load(args):
    """Reads the file and selects the calibration type.

    Returns:
        Dataset, or None after printing an error message.
    """
    # pylint: disable=import-outside-toplevel
    from eval_ac import analysis
    from eval_ac.convert_abscal_his import read_abscal_his, write_netcdf

    try:
        data_set = read_abscal_his(args.input)
    except (OSError, ValueError) as error:
        print(f'eval-ac: error: {error}', file=sys.stderr)
        return None
    print(f'read {data_set.sizes["n_samples"]} calibration entries '
          f'from {args.input}')

    if args.netcdf:
        write_netcdf(data_set, args.netcdf)
        print(f'wrote {args.netcdf}')

    if not args.all_cal_types:
        data_set = analysis.select_cal_type(data_set, analysis.CAL_TYPE_LN2)
        print(f'{data_set.sizes["n_samples"]} of them are calibrations with '
              'liquid nitrogen')
        if data_set.sizes['n_samples'] == 0:
            print('eval-ac: error: no calibrations with liquid nitrogen '
                  'found (use --all-cal-types)', file=sys.stderr)
            return None
    return data_set


def _save_plots(args, data_set, drift, thresholds):
    """Creates, saves and optionally shows the plots."""
    # pylint: disable=import-outside-toplevel
    import matplotlib.pyplot as plt
    from eval_ac.plotting import plot_calibration_history, plot_drift

    figures = [
        (plot_calibration_history(data_set), args.plot),
        (plot_drift(drift, thresholds=thresholds), args.drift_plot),
    ]
    for figure, filename in figures:
        figure.savefig(filename)
        print(f'wrote {filename}')
    if args.show:
        plt.show()
    for figure, _ in figures:
        plt.close(figure)


def main(argv=None) -> int:
    """Runs the command line interface.

    Args:
        argv: Command line arguments (default: ``sys.argv[1:]``).

    Returns:
        Exit code (0 on success, 1 on error, 2 on drift with
        ``--fail-on-drift``).
    """
    args = build_parser().parse_args(argv)

    # pylint: disable=import-outside-toplevel
    import matplotlib
    if not args.show:
        matplotlib.use('Agg')  # no display needed, e.g. on servers
    from eval_ac import analysis

    data_set = _load(args)
    if data_set is None:
        return 1

    thresholds = dict(args.threshold)
    drift = analysis.calibration_drift(data_set, n_reference=args.n_reference)
    exceedances = analysis.drift_exceedances(drift, thresholds)
    _print_report(data_set, exceedances,
                  analysis.latest_not_calibrated(data_set))

    if not args.no_plot:
        _save_plots(args, data_set, drift, thresholds)

    if args.fail_on_drift and exceedances:
        return EXIT_DRIFT
    return 0


if __name__ == '__main__':
    sys.exit(main())
