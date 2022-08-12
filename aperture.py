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

    print("\nUseful Parameters:")
    patch_dimensions = em_calcs.microstrip_patch(spec)
    patch_impedance = em_calcs.microstrip_patch_impedance(spec, patch_dimensions[0])
    print("50 ohm width: ",em_calcs.microstrip_width(50, spec))
    print("100 ohm width: ",em_calcs.microstrip_width(100, spec))
    print("wavelength: ", em_calcs.wavelength(spec))
    print("Patch dimensions [width, length]: ",patch_dimensions)
    print("Patch input impedance: ", patch_impedance)
    match_width = em_calcs.microstrip_width(sqrt(patch_impedance*50), spec)


    print("\nQuarter wave match length: ",em_calcs.effective_wavelength(match_width, spec)/4)
    print("Quarter wave 50 Ohm match width: ", match_width)
    print("50 Ohm patch inset distance: ", em_calcs.inset_distance(spec, 50))
    
    if spec["patch_count"] == 2:
        if spec["feed_type"] == "inset":
            tree = construct_array_2axial_inset(spec)
        elif spec["feed_type"] == "quarter_wave":
            tree = construct_array_2axial_quarter_wave(spec)
    elif spec["patch_count"] == 4:
        if spec["feed_type"] == "inset":
            tree = construct_array_4axial_inset(spec)
        elif spec["feed_type"] == "quarter_wave":
            tree = construct_array_4axial_quarter_wave(spec)

    print("\nFinished")
    generate_file(spec, tree, sys.argv[1].replace("json", "kicad_pcb"))
    print("Output file generated at " + sys.argv[1].replace("json", "kicad_pcb"))