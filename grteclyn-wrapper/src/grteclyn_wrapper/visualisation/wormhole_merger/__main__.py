"""`python -m grteclyn_wrapper.visualisation.wormhole_merger` lists the modules.

The package holds several unrelated figures, so a bare invocation cannot mean
one of them. Name the module you want.
"""

import sys

from . import __all__, __doc__ as _doc


def main() -> int:
    print(_doc.rstrip() if _doc else "")
    print("\nRun one of:")
    for m in __all__:
        if m != "run_tree":
            print(f"  python -m grteclyn_wrapper.visualisation.wormhole_merger.{m} --help")
    return 0


if __name__ == "__main__":
    sys.exit(main())
