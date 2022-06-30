from math import sqrt
import em_calcs as em


class Component:
    def __init__(self, spec, nodes=[]):
        self.name = "unnamed"
        self.spec = spec
        self.nodes = nodes
    
    def translate(self, point):
        return [point[0] + self.start[0], point[1] + self.start[1]]


class MicrostripLine(Component):
    def __init__(self, spec, z, length, direction, nodes=[]):
        super().__init__(spec, nodes)
        self.z = z
        self.length = length
        self.direction = direction
        self.width = em.microstrip_width(z, spec)
    
    def plot(self, start):
        self.start = start
        output = []
        output.append(self.translate([0, self.width/2]))
        output.append(self.translate([self.length, self.width/2]))
        if len(self.nodes) > 0: output.extend(self.nodes[0].plot(self.translate([self.length, 0])))
        output.append(self.translate([self.length, -self.width/2]))
        output.append(self.translate([0, -self.width/2]))

        return output


class MatchLine(MicrostripLine):
    def __init__(self, spec, z1, z2, direction, nodes=[]):
        z = sqrt(z1*z2)
        width = em.microstrip_width(z, spec)
        length = em.effective_wavelength(width, spec)/4
        super().__init__(spec, z, length, direction, nodes)

class MicrostripToEnd(MicrostripLine):
    def __init__(self, spec, z, end, direction, nodes=[]):
        super().__init__(spec, z, 0, direction, nodes)
        self.end = end

    def plot(self, start):
        self.start = start
        length = self.end - start[0]
        output = []
        output.append(self.translate([0, self.width/2]))
        output.append(self.translate([length, self.width/2]))
        if len(self.nodes) > 0: output.extend(self.nodes[0].plot(self.translate([length, 0])))
        output.append(self.translate([length, -self.width/2]))
        output.append(self.translate([0, -self.width/2]))

        return output


class PowerSplitter2_pinfeed(Component):
    def __init__(self, spec, zin, zout, direction, nodes=[]):
        super().__init__(spec, nodes)
        z = sqrt(zout*zin*2)
        self.width = em.microstrip_width(z, spec)
        self.branch_length = em.effective_wavelength(self.width, spec)/4
    
    def plot(self, start):
        self.start = start
        output = []
        output.append(self.translate([-self.branch_length, self.width/2]))
        output.append(self.translate([self.branch_length, self.width/2]))
        if len(self.nodes) > 0: output.extend(self.nodes[0].plot(self.translate([self.branch_length, 0])))
        output.append(self.translate([self.branch_length, -self.width/2]))
        output.append(self.translate([-self.branch_length, -self.width/2]))
        if len(self.nodes) > 1: output.extend(self.nodes[1].plot(self.translate([-self.branch_length, 0])))

        return output

class PowerSplitter2_linefeed(Component):
    def __init__(self, spec, zin, zout, direction, nodes=[]):
        super().__init__(spec, nodes)
        z = sqrt(zout*zin*2)
        self.width = em.microstrip_width(z, spec)
        self.feed_width = em.microstrip_width(zin, spec)
        self.branch_length = em.effective_wavelength(self.width, spec)/4
    
    def plot(self, start):
        self.start = start
        output = []

        output.append(self.translate([self.feed_width/2, 0]))
        output.append(self.translate([self.feed_width/2, self.width/2]))

        output.append(self.translate([self.branch_length, self.width/2]))
        if len(self.nodes) > 0: output.extend(self.nodes[0].plot(self.translate([self.branch_length, 0])))
        output.append(self.translate([self.branch_length, -self.width/2]))
        output.append(self.translate([-self.branch_length, -self.width/2]))
        if len(self.nodes) > 1: output.extend(self.nodes[1].plot(self.translate([-self.branch_length, 0])))
        output.append(self.translate([-self.branch_length, self.width/2]))

        output.append(self.translate([-self.feed_width/2, self.width/2]))
        output.append(self.translate([-self.feed_width/2, 0]))

        return output

class MitredBendAtPoint(Component):
    def __init__(self, spec, z, point, height, direction, nodes=[]):
        super().__init__(spec, nodes)
        self.width = em.microstrip_width(z, spec)
        self.mitre = em.mitred_corner(self.width, spec)
        self.height = height
        self.a = em.mitred_corner(self.width, spec)
        self.point = point
    
    def plot(self, start):
        self.start = start
        length = self.point - start[0]
        sign = length/abs(length)
        output = []
        output.append(self.translate([0, -self.width/2]))
        output.append(self.translate([length-sign*self.width/2, -self.width/2]))

        output.append(self.translate([length-sign*self.width/2, -self.height]))
        if len(self.nodes) > 0: output.extend(self.nodes[0].plot(self.translate([length, -self.height])))
        output.append(self.translate([length+sign*self.width/2, -self.height]))

        output.append(self.translate([length+sign*self.width/2, -self.width/2-self.a]))
        output.append(self.translate([length-sign*self.width/2-self.a, self.width/2]))

        output.append(self.translate([0, self.width/2]))
        return output