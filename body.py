from vector import Vector
import math

import matplotlib.pyplot as plt
class solar_sys_body:
    #consts
    minimum_display_size = 10
    display_log_base = 1.3

    def __init__(
            self,
            solar_system,
            mass,
            position=Vector(0,0,0),
            velocity=Vector(0,0,0)
        ):
        self.solarsys = solar_system
        self.mass = mass
        self.position = position
        self.velocity = Vector(*velocity)
        self.solarsys.add_body(self)
        self.display_size = max(math.log(self.mass, self.display_log_base), self.minimum_display_size)
        self.colour = "black"
        self.position_history = []
    
    def draw(self):
        self.solarsys.ax.plot(
        *self.position,
        marker = "o",
        markersize = self.display_size,
        color=self.colour
        )
        if len(self.position_history) > 1:
            positions = self.position_history[-2000:]
            x_vals = [p[0] for p in positions]
            y_vals = [p[1] for p in positions]
            z_vals = [p[2] for p in positions]
            self.solarsys.ax.plot(x_vals, y_vals, z_vals, color=self.colour, alpha=0.3, linewidth=3)
    def move(self):
        self.position = Vector (
            self.position[0] + self.velocity[0],
            self.position[1] + self.velocity[1],
            self.position[2] + self.velocity[2]
        )
        self.position_history.append(self.position + self.velocity)

    def acceleration(self, other):
        distance = Vector(*other.position) - Vector(*self.position)
        dist_mag = distance.get_magnitude()
        force_mag = self.mass*other.mass/(dist_mag**2)
        force = distance.normalise()*force_mag
        reverse = 1
        for body in self, other:
            acceleration = force / body.mass
            body.velocity += acceleration*reverse
            reverse = -1

