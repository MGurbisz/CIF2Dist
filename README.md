# CIF2Dist

**CIF2Dist** is a command-line tool and python package for calculating interatomic distances from a CIF (crystallography information file). It is authored by Marco Gurbisz and Tom Förster.

## Installation
To use **CIF2Dist**, you need
- Python 3.8 or later installed
- pip (Python's package installer)

For installation, you can either 
1. clone the git repository and install the package locally:
```bash
git clone https://github.com/MGurbisz/CIF2Dist.git
cd CIF2Dist
pip install .
```
2. Or install using pip directly
```bash
pip install CIF2Dist
```
Then run from command line
```bash
CIF2Dist --help
```
If the CIF2Dist command is not found, you may need to add Python's Scripts Folder to your Path:
For Windows, search for 'Environment Variables' and open 'Edit the system environment variables'. There open 'Environment Variables'. Under 'User Variables' find Path and click Edit. Select 'New' and add this:
```
%LOCALAPPDATA%\Packages\PythonSoftwareFoundation.Python.3.###\LocalCache\local-packages\Python3###\Scripts
```
Alternatively, you can run it using:
```bash
python -m cif2dist.cli --help
```
## Input
Input a CIF using its path and filename, and specify a site with -s to calculate the distance to its neighbors. For the stom site input you can use the atom label (e. g. "Y1") directly. Otherwise stating the Wyckoff site (e. g. '4a') or Wyckoff letter (e. g. 'a') or the element (e. g. 'Y') can be done, if it's unambiguous (i. e. there is only one match for the input and a atom label). 
## Arguments
The tool supports multiple Arguments
### Help --help, -h
Displays the help site and exits
### Version --version, -v
Displays the version number and exits
### Center site --site, -s
Specifies center site for calculation. See Subsection 'Input'
### Cutoff Distance --cutoff, -c
Specifies cutoff distance for the calculation. The default value is 10 Ångstrom.
### Filter --filter, -f
Specifies the output filter. It accepts Wyckoff sites and letters, site labels and elements. The output will contain the specified site distances only.
### No Version Check --no-version-check
Disables automatic version check.
## Output
 After running the code, you'll get an output file called 'summary.txt'. It contains the Site labels, the number of atoms on this site at the same distance and then the distance itself in Å all separated by a tab space character.