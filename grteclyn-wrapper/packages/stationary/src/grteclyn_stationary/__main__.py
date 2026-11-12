"""Stationary solver commands; import and help never select a device."""
import argparse
import importlib


COMMANDS = {
    'optimize': 'commands.optimize_potential',
    'validate': 'commands.validate_candidate',
    'refine': 'commands.refine_study',
    'rings': 'commands.railgun',
    'continue-boson': 'commands.continue_boson',
}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('command', choices=COMMANDS)
    parser.add_argument('arguments', nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)
    module = importlib.import_module(f'grteclyn_stationary.{COMMANDS[args.command]}')
    return module.main(args.arguments)


if __name__ == '__main__':
    raise SystemExit(main())
