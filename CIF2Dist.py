import argparse
from pymatgen.core import Structure
from pymatgen.core.structure import Structure, PeriodicSite
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.analysis.structure_matcher import StructureMatcher
from pymatgen.io.cif import CifParser
from collections import defaultdict
import os
import re
import math
import numpy as np

remove_int_from_str = r'[0-9]'

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("cif", help="Input CIF file")
    parser.add_argument("--site", required=True, help="Wyckoff label (e.g., '4a') or Atom site (e.g., Al1)")
    parser.add_argument("--cutoff", required=False, help="cutoff distance in Angstrom, default 10 A")
    args = parser.parse_args()
    

    # DEBUG
    # export_to_txt(compute_distances("bsp.cif","Y",4))

    export_to_txt(compute_distances(args.cif, args.site, args.cutoff))

def compute_distances(cif_path, user_site: str, cutoff_dist: float) -> list[tuple[str, int, float]]:
    """
    Main Method. Compute distances using cif, site information and cutoff distance
    """
    if cutoff_dist is None:
        cutoff_dist = 10.0  # default
    site_class, site_label = classify_site(user_site)

    print("site class:", site_class)
    print("site_label:", site_label)

    if not os.path.exists(cif_path):
        raise FileNotFoundError(f"CIF not found at: {cif_path}")

    parser = CifParser(cif_path)
    structure = parser.get_structures(primitive=False)[0]
    analyzer = SpacegroupAnalyzer(structure, symprec=1e-3)
    wyckoff_data = analyzer.get_symmetry_dataset()
    wyckoff_letters = wyckoff_data["wyckoffs"]

    # DEBUG: Print general info
    print(f"\nSuccessfully loaded CIF: {cif_path}")
    print(f"Unit cell formula: {structure.composition.formula}")
    print(f"Number of atoms in full cell: {len(structure)}")

    if site_class == "atomsite":
        wyckoff, origin_fraccoord = get_wyckoff_fraccoords_for_atomsite(parser, structure, site_label, wyckoff_letters)
    else:
        # If it's a Wyckoff letter, just return it directly
        print(f"User provided Wyckoff label: {site_label}")
        wyckoff = site_label
        # resolve wyckoff letter to origin coords
        origin_fraccoord = get_asymmetric_coords_for_wyckoff(structure, wyckoff)

    # Now we have wyckoff letter disregarding user input
    # calculation of distances using the structure and get_neighbors
    # supercell apparently not needed for get_sites_in_sphere

    origin_cart = structure.lattice.get_cartesian_coords(origin_fraccoord)

    neighbors = structure.get_sites_in_sphere(origin_cart, cutoff_dist, True, True)

    # get site labels and distances from all found neighbors
    neighbor_distances = []
    for neighbor in range(len(neighbors)):
        distance = round(calc_distance(origin_cart, neighbors[neighbor].coords), 3)
        neighbor_distances.append([neighbors[neighbor].label, distance])

    sorted_neighbor_distances = sorted(neighbor_distances, key=lambda x: x[0]) # sort based on name first
    sorted_neighbor_distances = sorted(sorted_neighbor_distances, key=lambda x: x[1]) # sort based on distance, which comes second in the sublist

    # count all sites at the same distances given they have the same label
    results = []
    current_site = None
    site_count = 0
    for i in range(len(sorted_neighbor_distances)):
        key = (sorted_neighbor_distances[i][0], sorted_neighbor_distances[i][1])

        if key != current_site:
            if current_site is not None:
                results.append([current_site[0], site_count, current_site[1]])
            current_site = key
            site_count = 1
        else:
            site_count += 1
    
    if current_site is not None:
        results.append([current_site[0], site_count, current_site[1]])

    return results

def export_to_txt(results: list[tuple[str, int, float]], filename="summary.txt") -> None:
    """
    gives a txt file. input is the results list
    """
    with open(filename, 'w') as f:
        for row in results:
            line = '\t'.join(str(item) for item in row)
            f.write(line + '\n')
    print(f"output file written.")
    

def classify_site(user_site: str) -> tuple[str, str]:
    """
    Returns tuple of (wyckoff/atomsite, label). Distinguish user site input to either a wyckoff site, or a sepcified Atom site in CIF.
    """
    if len(user_site) >= 1 and user_site[-1].islower():
        prefix = user_site[:-1]
        if prefix.isdigit() or prefix == "":
            return ("wyckoff", user_site[-1])
        
    return ("atomsite", user_site)

def get_asymmetric_coords_for_wyckoff(structure, target_wyckoff: str) -> tuple[float, float, float]:
    sga = SpacegroupAnalyzer(structure, symprec=1e-3)
    symm_struct = sga.get_symmetrized_structure()

    for wyckoff_letter, site_group in zip(symm_struct.wyckoff_symbols, symm_struct.equivalent_sites):
        # wyckoff_letter has full name with multiplicity by dafault -> remove int from str to only match letter 
        if re.sub(remove_int_from_str, '', wyckoff_letter.lower()) == target_wyckoff.lower():
            return site_group[0].frac_coords

    raise ValueError(f"No site found for Wyckoff letter '{target_wyckoff}'.")

def get_wyckoff_fraccoords_for_atomsite(parser: CifParser, structure, site_label: str, wyckoff_letters: list) -> tuple[str, tuple[float, float, float]]:
    """
    Returns tuple of wyckoff letter and frac coords(as a tuple of three floats) of asymm unit. 
    Input the parser, structure, site_label and the wyckoff letter
    """
    # Extract CIF info for asymmetric unit
    cif_dict = parser.as_dict()
    data_block = list(cif_dict.values())[0]

    labels = data_block["_atom_site_label"]
    x = list(map(float, data_block["_atom_site_fract_x"]))
    y = list(map(float, data_block["_atom_site_fract_y"]))
    z = list(map(float, data_block["_atom_site_fract_z"]))
    asym_coords = list(zip(x, y, z))

    # Match site_label to label list.
    matching_labels = []
    for label in labels:
        if label.startswith(site_label):
            matching_labels.append(label)

    # site_label could be Al or Al1 at this point. If there is only one Al site matching_labels is of len 1 and therefore Al can be assigned to Al1, if there are more matching labels, lile user states Al, but there is Al1 and Al2 matching_labels will be at len 2 and raise error
    if site_label not in labels:
        if len(matching_labels) == 1:
            resolved_label = matching_labels[0]
            print(f"Inferred full label '{resolved_label}' from partial input '{site_label}'")
            site_label = resolved_label
        elif len(matching_labels) == 0:
            raise ValueError(f"No matching atom site found for prefix '{site_label}'.")
        else:
            raise ValueError(f"Ambiguous input '{site_label}'. Matches found: {matching_labels}")

    # gather all possible label coordinates of the asymm unit. and get coordinates for the site in question
    label_coords = dict(zip(labels, asym_coords))
    target_coord = np.array(label_coords[site_label])

    # go through list of all frac coords and get a match. output matched index and wyckoff letter indexed to it
    for i, coord in enumerate(structure.frac_coords):
        if np.allclose(coord, target_coord, atol=1e-3):
            wyckoff = wyckoff_letters[i]
            print(f"Found match for '{site_label}' at index {i} with Wyckoff letter {wyckoff}")
            return wyckoff, target_coord
    raise ValueError(f"Could not match coordinates for '{site_label}' to any atom in structure.")

def calc_distance (origin_coord: tuple[float, float, float], remote_coord: tuple[float, float, float]) -> float:
    diff = origin_coord - remote_coord
    squared_diff = diff ** 2
    sum_squared_diff = np.sum(squared_diff)
    distance = np.sqrt(sum_squared_diff)
    return distance

if __name__ == "__main__":
    main()