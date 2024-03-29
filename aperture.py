from math import sqrt
import sys
import json

import em_calcs

from plot import *

spec = {}

def critical_error(desc):
    print("\n***** Critical Error *****")
    print("Error description: ", desc)
    print("Exiting program...")
    quit()

# reads file specified in command line argument
def read_specification_file():
    if len(sys.argv) < 2:
        critical_error("No specification file provided")
        return 0
    
    filename = sys.argv[1]

    try:
        specification_file = open(filename)
    except IOError:
        critical_error("Specification file not found")
        return 0

    try:
        data = json.load(specification_file)
    except json.decoder.JSONDecodeError:
        critical_error("Specification file is not valid JSON")
        return 0

    # check each parameter is present
    required_parameters = ["frequency", "body_radius", "dielectric_thickness", "dielectric_constant", "copper_thickness", "polarisation", "patch_count"]
    for param in required_parameters:
        if param not in data:
            critical_error("Required parameter \"" + param + "\" missing in specification file")
            return 0

    return data


if __name__ == "__main__":


    spec = read_specification_file()


    print("\nOverridden parameters:")
    if "patch_length" in spec:
        print("patch_length: ", spec["patch_length"])
    if "inset_distance" in spec:
        print("inset_distance: ", spec["inset_distance"])


    print("\nCalculated Parameters:")
    if spec["polarisation"] != "axial":
        patch_dimensions = em_calcs.square_patch(spec)
    else:
        patch_dimensions = em_calcs.microstrip_patch(spec)
    patch_impedance = em_calcs.microstrip_patch_impedance(spec, patch_dimensions[0])
    print("50 ohm width: ",em_calcs.microstrip_width(50, spec))
    print("100 ohm width: ",em_calcs.microstrip_width(100, spec))
    print("wavelength: ", em_calcs.wavelength(spec))
    print("Patch dimensions [width, length]: ",patch_dimensions)
    print("Patch input impedance: ", patch_impedance)
    
    print("\nFor patch impedance matching:")
    match_width = em_calcs.microstrip_width(sqrt(patch_impedance*50), spec)
    print("Quarter wave match length: ",em_calcs.effective_wavelength(match_width, spec)/4)
    print("Quarter wave 50 Ohm match width: ", match_width)
    print("50 Ohm patch inset distance: ", em_calcs.inset_distance(spec, 50))

    print("\nFor power splitter:")
    match_width = em_calcs.microstrip_width(sqrt(100*50), spec)
    print("100 to 50 Ohm match width: ", match_width)
    print("Quarter wave match length: ", em_calcs.effective_wavelength(match_width, spec)/4)
    
    # the actual synthesis of the antenna (see plot.py)
    tree = construct_array(spec)
    points = tree.plot([0, 0])

    print("\nFinished")
    generate_file(spec, points, sys.argv[1].replace("json", "kicad_pcb"))
    generate_dxf(spec, points, sys.argv[1].replace("json", "dxf"))
    print("Output files generated at " + sys.argv[1].replace("json", "kicad_pcb") + ", " + sys.argv[1].replace("json", "dxf"))