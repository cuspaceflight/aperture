from math import sqrt
import sys
import json

import em_calcs

from plot import *

spec = {}


# reads file specified in command line argument
def read_specification_file():
    if len(sys.argv) < 2:
        print("No specification file provided")
        return 0
    
    filename = sys.argv[1]

    try:
        specification_file = open(filename)
    except IOError:
        print("Specification file not found")
        return 0

    try:
        data = json.load(specification_file)
    except json.decoder.JSONDecodeError:
        print("Selectected file is not valid JSON")
        return 0

    # check each parameter is present
    required_parameters = ["frequency", "body_radius", "dielectric_thickness", "dielectric_constant", "copper_thickness", "polarisation", "patch_count"]
    for param in required_parameters:
        if param not in data:
            print("Required parameter \"" + param + "\" missing in specification file")
            return 0

    return data


if __name__ == "__main__":

    # read data from file
    spec = read_specification_file()
    if spec == 0: 
        print("Critcal specification file error, quitting")
        quit()

    
    patch_dimensions = em_calcs.microstrip_patch(spec)
    patch_impedance = em_calcs.microstrip_patch_impedance(patch_dimensions[0], spec)

    print("50 ohm width: ",em_calcs.microstrip_width(50, spec))
    print("Linear patch dimensions [width, length]: ",patch_dimensions)
    print("Patch input impedance: ", patch_impedance)
    match_width = em_calcs.microstrip_width(sqrt(patch_impedance*50), spec)
    print("Quarter wave match length: ",em_calcs.effective_wavelength(match_width, spec)/4)
    print("Quarter wave match width: ", match_width)


    tree = construct_array(spec)

    generate_file(spec, tree, sys.argv[1].replace("json", "kicad_pcb"))
    print("Output file generated at " + sys.argv[1].replace("json", "kicad_pcb"))