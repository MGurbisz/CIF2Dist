#cif2dist/cli.py
import argparse
from cif2dist.core import compute_distances, export_to_txt
from cif2dist import __version__
import requests

def main():
    parser = argparse.ArgumentParser(prog="CIF2Dist")
    parser.add_argument('-v', '--version', action='version', version=f'%(prog)s {__version__}', help="show program's version number and exit")
    parser.add_argument("cif", help="Input CIF file")
    parser.add_argument('-s', "--site", required=True, help="input wyckoff label (e.g., '4a'), atom site (e.g., Al1) or chem. element if unique")
    parser.add_argument('-c', "--cutoff", required=False, help="cutoff distance in angstrom, default: 10 A", default=10, type=float)
    parser.add_argument('-f', "--filter", required=False, help="target atom/site/element filter (e.g., Al -> return distances to all Al-Sites, Al1 -> return all distances to Al1-sites). default: None", default=None)
    parser.add_argument("--no-version-check", required=False, help="Disables automatic version check", action="store_true")

    args = parser.parse_args()
    # if user did not input -n, --no-version-check, do version check
    if not args.no_version_check:
        notify_if_outdated("CIF2Dist")

    try: 
        distances = compute_distances(args.cif, args.site, args.cutoff, args.filter)
        export_to_txt(distances)
    except Exception as e:
        print(f"Error: {e}")

def get_latest_version_from_pypi(package_name: str) -> str:
    """
    returns version number of latest version of input package_name on PyPI.
    """
    try:
        url = f"https://pypi.org/pypi/{package_name}/json"
        response = requests.get(url, timeout=2)
        response.raise_for_status()
        return response.json()["info"]["version"]
    except requests.RequestException:
        return None
    
def notify_if_outdated(package_name: str):
    latest = get_latest_version_from_pypi(package_name)
    if latest and latest != __version__:
        print(f"You are using {package_name} v{__version__}, but version {latest} is available. Run 'pip install -U {package_name}' to upgrade")