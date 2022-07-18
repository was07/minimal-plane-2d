class Plane:
    """ Plane Data Calculator for Simulation
    """
    def __init__(self):
        self.cfg = {'ang': 0, 'hike': 0, 'power': 2, 'dir': 0, 'at': 20}
        self.cts = {'travel': 0, 'fuel': 10000}
        self.poses = []  # history of all the positions the plane has been at
    
    def __getitem__(self, item): return self.cfg[item] if item in self.cfg else self.cts[item]
    
    def __setitem__(self, key, value): self.cfg[key] = value
    
    def step(self):
        if self['fuel'] <= 0: return 'Fuel Ran Off'
        elif self['at'] <= 1: return 'Touch Down\nPlane Leaned and Crashed Into Ground'
        
        a, p, d = self['ang'], self['power'], self['dir']
        
        # not letting angle get out of 0-40
        if a >= 40: self['ang'] = 40
        elif a <= -40: self['ang'] = -40
        
        # not letting hike get out of -20-20
        if self['hike'] >= 20: self['hike'] = 20
        elif self['hike'] <= -20: self['hike'] = -20
        
        # not letting power get of 0-5 (decreasing attitude if power is 0)
        if p < 1: self['power'] = 0; self['at'] -= .1
        elif 5 < p: self['power'] = 5
        self['dir'] += a / 30
        
        # Not letting dir get out of 0-360
        if d > 360: self['dir'] -= 360
        elif d < 0: self['dir'] = 360 + d
        
        # Not letting at get out of 1-70
        if self['at'] > 70: self['at'] = 70
        elif self['at'] < 1: self['at'] = 1

        self.poses.append((a / 30, self['power']))
        if self['power'] > 0:
            self['at'] += self['hike']/100
        self.cts['travel'] += self['power']/3
        self.cts['fuel'] -= self['power']/3
