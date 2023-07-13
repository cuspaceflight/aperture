# Contains functions for calculating impedances, wavelengths etc.

from cmath import pi
from math import exp
from math import sqrt
from math import log

from numpy import arccos

c = 3e11 # mm/s

# calculates wavelength in mm
def wavelength(spec):
    f = spec["frequency"]
    k = spec["dielectric_constant"]
    return c / f / sqrt(k)

############################## microstrip transmission lines ##############################

# takes line width in mm and spec data
# returns effective wavelength in the microstrip line in mm
def effective_wavelength(width, spec):
    f = spec["frequency"]
    k = spec["dielectric_constant"]
    h = spec["dielectric_thickness"]

    if width/h < 1:
        keff = (k+1)/2 + (k-1)/2*(1/sqrt(1+12*h/width) + 0.04*(1-width/h)**2 )
    else:
        keff = (k+1)/2 + (k-1)/ (2*sqrt(1+12*h/width))

    return c / f / sqrt(keff)

# takes desired impedance z in ohms and spec data
# returns required microstrip line width in mm
# formula source: https://www.everythingrf.com, accessed June 2022
# this formula does not give good results in simulation
def microstrip_width_fast(z, spec):
    h = spec["dielectric_thickness"]
    k = spec["dielectric_constant"]
    t = spec["copper_thickness"]
    return 7.48*h / exp(z * sqrt(k+1.41)/87) - 1.25 * t

# takes width in mm and spec data
# returns impedance in ohms of microstrip line
# corroborates simulation
# formula source https://www.pasternack.com/t-calculator-microstrip.aspx, accessed June 2022
def microstrip_impedance(width, spec):
    h = spec["dielectric_thickness"]
    k = spec["dielectric_constant"]

    if width/h < 1:
        keff = (k+1)/2 + (k-1)/2*(1/sqrt(1+12*h/width) + 0.04*(1-width/h)**2 )
        return 60/sqrt(keff)*log(8*h/width + 0.25*width/h)

    else:
        keff = (k+1)/2 + (k-1)/ (2*sqrt(1+12*h/width))
        return 120*pi / sqrt(keff) / (width/h +1.393+2/3*log(width/h+1.444))
    

# takes desired impedance in ohms and spec data
# returns required line width in mm or 0 if not found
# uses binary search based on microstrip_impedance
def microstrip_width(zt, spec):
    h = spec["dielectric_thickness"]
    k = spec["dielectric_constant"]
    t = spec["copper_thickness"]

    # starting points
    low = 0.1
    high = 5

    # somewhat arbitrary parameters
    acceptable_error = 0.5 # ohm
    max_runs = 100
    
    for i in range(max_runs):
        mid = (low + high)/2
        z = microstrip_impedance(mid, spec)

        if abs(z - zt) < acceptable_error:
            return mid
        elif z > zt:
            low = mid
        else:
            high = mid 
    
    return 0 # not found


# takes line width and spec and calculates corner dimensions for ideal bend
#         ->| |<- a
# __________. .
#            *.
#             .*
#             .  * 
# ____________.    *
#             |      *
#             |        |
#             |        |
# formula source: https://www.everythingrf.com, accessed 2022
def mitred_corner(width, spec):
    h = spec["dielectric_thickness"]
    x = width * sqrt(2) * (0.52 + 0.65*exp(-1.35*width/h))
    a = x * sqrt(2) - width

    return a  



    
############################## patch antennas ##############################


# calculates patch dimensions for simple edge fed linear polarised patch
# formula source: https://www.everythingrf.com, accessed June 2022
def microstrip_patch(spec):
    h = spec["dielectric_thickness"]
    k = spec["dielectric_constant"]
    f = spec["frequency"]

    width = c / (2*f*sqrt((k+1)/2))
    keff = (k+1)/2 + (k-1)/ (2*sqrt(1+12*h/width))
    length = c / (2*f*sqrt(keff)) - 2*0.412*h*(keff+0.3)*(width/h+0.264)/(k - 0.258)/(width/h+0.8)    
    
    # override
    if "patch_length" in spec:
        length = spec["patch_length"]

    return [width, length]

# similar to above, but for a square patch
def square_patch(spec):
    h = spec["dielectric_thickness"]
    k = spec["dielectric_constant"]
    f = spec["frequency"]

    width = c / (2*f*sqrt(k)) # first pass width
    keff = (k+1)/2 + (k-1)/ (2*sqrt(1+12*h/width))
    length = c / (2*f*sqrt(keff)) - 2*0.412*h*(keff+0.3)*(width/h+0.264)/(k - 0.258)/(width/h+0.8)
    width = length
    
    # override
    if "patch_length" in spec:
        length = spec["patch_length"]
        width = spec["patch_length"]

    return [width, length]

# takes patch width and spec data
# returns approximate maximum edge impedance at resonance
# formula source: Balanis, C A 1982, "Antenna Theory: Analysis and Design"
def microstrip_patch_impedance(spec, width):
    h = spec["dielectric_thickness"]
    k = spec["dielectric_constant"]

    y = wavelength(spec)

    g = (width/(120*y))*(1-((1/24)*(k*h)**2))

    return abs(1/2/g)

# takes desired impedance and patch edge impedance
# returns inset distance required to achieve match
# assumes antenna parameters as per the above functions
# formula source: Balanis, C A 1982, "Antenna Theory: Analysis and Design"
def inset_distance(spec, zin):

    patch_dimensions = microstrip_patch(spec)

    zedge = microstrip_patch_impedance(spec, patch_dimensions[0])

    length = patch_dimensions[1]

    dist = length / pi * arccos(sqrt(zin/zedge))

    # override
    if "inset_distance" in spec:
        dist = spec["inset_distance"]

    return dist