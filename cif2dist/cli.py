import argparse
from cif2dist.core import compute_distances, export_to_txt
from cif2dist import __version__

def main():
    parser = argparse.ArgumentParser(prog="CIF2Dist")
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}', help="show program's version number and exit")
    parser.add_argument("cif", help="Input CIF file")
    parser.add_argument('-s', "--site", required=True, help="input wyckoff label (e.g., '4a'), atom site (e.g., Al1) or chem. element if unique")
    parser.add_argument('-c', "--cutoff", required=False, help="cutoff distance in angstrom, default: 10 A", default=10, type=float)
    parser.add_argument('-f', "--filter", required=False, help="target atom/site/element filter (e.g., Al -> return distances to all Al-Sites, Al1 -> return all distances to Al1-sites). default: None", default=None)
    
    args = parser.parse_args()
    try: 
        distances = compute_distances(args.cif, args.site, args.cutoff, args.filter)
        export_to_txt(distances)
    except Exception as e:
        print(f"Error: {e}")