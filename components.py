from math import sqrt
import em_calcs as em


class Component:
    def __init__(self, spec, nodes=[]):
        self.name = "unnamed"
        self.spec = spec
        self.nodes = nodes
        self.points = []
    
    def translate(self, point):

        return [point[0] + self.start[0], point[1] + self.start[1]]
    
    def add_point(self, point):
        self.points.append(self.translate(point))
    
    def plot_child(self, child_number, node_location):
        if len(self.nodes) <= child_number: return

        child = self.nodes[child_number]
        self.points.extend(child.plot(self.translate(node_location)))





class MicrostripLine(Component):
    def __init__(self, spec, z, length, direction, nodes=[]):
        super().__init__(spec, nodes)
        self.z = z
        self.length = length
        self.direction = direction
        self.width = em.microstrip_width(z, spec)
    
    def plot(self, start):
        self.start = start
        self.add_point([0, self.width/2])
        self.add_point([self.length, self.width/2])
        if len(self.nodes) > 0: self.plot_child(self.nodes[0], [self.length, 0])
        self.add_point([self.length, -self.width/2])
        self.add_spoint([0, -self.width/2])

        return self.points


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
        self.add_point([0, self.width/2])
        self.add_point([length, self.width/2])
        self.plot_child(0, [length, 0])
        self.add_point([length, -self.width/2])
        self.add_point([0, -self.width/2])

        return self.points


class PowerSplitter2_pinfeed(Component):
    def __init__(self, spec, zin, zout, hole_size, direction, nodes=[]):
        super().__init__(spec, nodes)
        z = sqrt(zout*zin*2)
        self.width = em.microstrip_width(z, spec)
        self.branch_length = em.effective_wavelength(self.width, spec)/4

        self.hole_size = hole_size

    def plot(self, start):
        self.start = start

        
        self.add_point([self.branch_length, self.width/2])
        self.plot_child(0, [self.branch_length, 0])
        self.add_point([self.branch_length, -self.width/2])
        self.add_point([-self.branch_length, -self.width/2])
        self.plot_child(1, [-self.branch_length, 0])
        self.add_point([-self.branch_length, self.width/2])
        
        self.add_point([0, self.width/2])
        self.add_point([0, self.hole_size])
        self.add_point([-self.hole_size, 0])
        self.add_point([0, -self.hole_size])
        self.add_point([self.hole_size, 0])
        self.add_point([0, self.hole_size])
        self.add_point([0, self.width/2])

        return self.points

class PowerSplitter2_linefeed(Component):
    def __init__(self, spec, zin, zout, direction, nodes=[]):
        super().__init__(spec, nodes)
        z = sqrt(zout*zin*2)
        self.width = em.microstrip_width(z, spec)
        self.feed_width = em.microstrip_width(zin, spec)
        self.branch_length = em.effective_wavelength(self.width, spec)/4
    
    def plot(self, start):
        self.start = start

        self.add_point([self.feed_width/2, 0])
        self.add_point([self.feed_width/2, self.width/2])

        self.add_point([self.branch_length, self.width/2])
        self.plot_child(0, [self.branch_length, 0])
        self.add_point([self.branch_length, -self.width/2])
        self.add_point([-self.branch_length, -self.width/2])
        self.plot_child(1, [-self.branch_length, 0])
        self.add_point([-self.branch_length, self.width/2])

        self.add_point([-self.feed_width/2, self.width/2])
        self.add_point([-self.feed_width/2, 0])

        return self.points

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

        self.add_point([0, -self.width/2])
        self.add_point([length-sign*self.width/2, -self.width/2])

        self.add_point([length-sign*self.width/2, -self.height])
        self.plot_child(0, [length, -self.height])
        self.add_point([length+sign*self.width/2, -self.height])

        self.add_point([length+sign*self.width/2, -self.width/2-self.a])
        self.add_point([length-sign*self.width/2-self.a, self.width/2])

        self.add_point([0, self.width/2])
        return self.points