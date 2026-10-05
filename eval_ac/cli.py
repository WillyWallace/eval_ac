"""Command line interface of eval_ac.

Example::

    eval-ac ABSCAL.HIS --netcdf abscal.nc --plot results_ln2_cal.png
"""

import argparse
import sys

from eval_ac import __version__


def build_parser() -> argparse.ArgumentParser:
    """Creates the argument parser."""
    parser = argparse.ArgumentParser(
        prog='eval-ac',
        description='Read the ABSCAL.HIS file of an RPG microwave radiometer '
                    '(e.g. HATPRO) and plot the history of the absolute '
                    'calibration with liquid nitrogen.')
    parser.add_argument('input', help='path of the ABSCAL.HIS file')
    parser.add_argument('-n', '--netcdf', metavar='FILE',
                        help='write the converted data to this NetCDF file')
    parser.add_argument('-p', '--plot', metavar='FILE',
                        default='results_ln2_cal.png',
                        help='save the plot to this file '
                             '(default: %(default)s)')
    parser.add_argument('--no-plot', action='store_true',
                        help='do not create a plot')
    parser.add_argument('--show', action='store_true',
                        help='show the plot in a window')
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {__version__}')
    return parser


def main(argv=None) -> int:
    """Runs the command line interface.

    Args:
        argv: Command line arguments (default: ``sys.argv[1:]``).

    Returns:
        Exit code (0 on success, 1 on error).
    """
    args = build_parser().parse_args(argv)

    # pylint: disable=import-outside-toplevel
    import matplotlib
    if not args.show:
        matplotlib.use('Agg')  # no display needed, e.g. on servers
    from eval_ac.convert_abscal_his import read_abscal_his, write_netcdf

    try:
        data_set = read_abscal_his(args.input)
    except (OSError, ValueError) as error:
        print(f'eval-ac: error: {error}', file=sys.stderr)
        return 1
    print(f'read {data_set.sizes["n_samples"]} calibration entries '
          f'from {args.input}')

    if args.netcdf:
        write_netcdf(data_set, args.netcdf)
        print(f'wrote {args.netcdf}')

    if not args.no_plot:
        import matplotlib.pyplot as plt
        from eval_ac.plotting import plot_calibration_history
        figure = plot_calibration_history(data_set)
        figure.savefig(args.plot)
        print(f'wrote {args.plot}')
        if args.show:
            plt.show()
        plt.close(figure)
    return 0


if __name__ == '__main__':
    sys.exit(main())
