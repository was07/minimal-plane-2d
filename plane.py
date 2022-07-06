

class Plane:
    """ Plane Data Calculator for Simulation
    """
    def __init__(self):
        self.cfg = {'ang': 0, 'hike': 1, 'power': 2, 'dir': 0, 'at': 10}
        self.cts = {'travel': 0, 'fuel': 10000}
        self.poses = []
    
    def __getitem__(self, item): return self.cfg[item] if item in self.cfg else self.cts[item]
    
    def __setitem__(self, key, value): self.cfg[key] = value
    
    def step(self):
        if self['fuel'] <= 0: return 'Fuel Ran Off'
        elif self['at'] <= 0: return 'Touch Down\nPlane Leaned and Crashed Into Ground'
        
        a, p, d = self['ang'], self['power'], self['dir']
        if a >= 40: self['ang'] = 40
        elif a <= -40: self['ang'] = -40
        if p < 1: self['power'] = 0; self['at'] -= .1
        elif 5 < p: self['power'] = 5
        self['dir'] += a / 30
        
        if d > 360: self['dir'] -= 360
        elif d < 0: self['dir'] = 360 + d

        self.poses.append((a / 30, self['power']))
        self['at'] += self['hike']/100
        self.cts['travel'] += self['power']
        self.cts['fuel'] -= self['power']


