import matplotlib.pyplot as plt
import math
from body import solar_sys_body
import itertools
class Solar_system:

    def __init__(self, size):
        self.size = size
        self.bodies = []
        self.fig, self.ax = plt.subplots(
            1,
            1,
            subplot_kw={"projection" : "3d"},
            figsize=(self.size/50, self.size/50)
        )
        self.fig.tight_layout()
        self.ax.view_init(0, 0)

    def add_body(self, body):
        self.bodies.append(body)

    def update_all(self):
        for body in self.bodies:
            body.move()
            body.draw()

    def draw_all(self):
        self.ax.set_xlim((-self.size/2, self.size/2))
        self.ax.set_ylim((-self.size/2, self.size/2))
        self.ax.set_zlim((-self.size/2, self.size/2))
        plt.pause(0.001)
        self.ax.clear()
        for body in self.bodies:
            if len(body.position_history) > 2500:  # Limit history size
                body.position_history = body.position_history[-2500:]
    
    def calculate_body_interactions(self):
        copy = self.bodies.copy()
        for idx, first in enumerate(copy):
            for second in copy[idx+1:]:
                first.acceleration(second)

class Sun(solar_sys_body):
    def __init__(self, solarsys, mass=1e6, position=(0,0,0), velocity=(0,0,0),):
        super(Sun, self).__init__(solarsys, mass, position, velocity)
        self.colour = "yellow"

class Planet(solar_sys_body):
    colours = itertools.cycle([(1, 0, 0), (0, 1, 0), (0, 0, 1)])
    def __init__(self, solarsys, mass=10, position=(0,0,0), velocity=(0,0,0)):
        super(Planet, self).__init__(solarsys, mass, position, velocity)
        self.colour = next(Planet.colours)

if __name__ == "__main__":
    solarsys = Solar_system(8000)
    sun = Sun(solarsys)
    r1 = 200
    r2 = 400
    v1_mag = math.sqrt(sun.mass/r1)
    v2_mag = math.sqrt(sun.mass/r2)
    planets = (
        Planet(
            solarsys,
            mass = 5,
            position=(100 ,150, 100),
            velocity=(0, v1_mag, 0)
        ),
        Planet(
            solarsys,
            mass = 5,
            position=(200, -120, 150),
            velocity=(v2_mag, 0.0, 0)
        )
    )
    while True:
        solarsys.calculate_body_interactions()
        solarsys.update_all()
        solarsys.draw_all()