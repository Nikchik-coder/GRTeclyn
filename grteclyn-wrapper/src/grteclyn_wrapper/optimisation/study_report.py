"""Rebuild comparison plots from a study's persisted diagnostics."""

def plot_comparison(directory):
    from grteclyn_wrapper.visualisation.optimisation.plot_study import plot_comparison as plot
    plot(directory)

def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory')
    plot_comparison(parser.parse_args().directory)

if __name__=='__main__':
    main()
