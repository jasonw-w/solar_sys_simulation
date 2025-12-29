import matplotlib.pyplot as plt
import math
from body import solar_sys_body
import itertools
from solar_system import SolarSystemSimulation
from loadplanets import json_loader
import time
import matplotlib.animation as animation
G = 1
# log_path = r"simulation.txt"
log_path = None
dt = 1e-7
record = False
solarsys = SolarSystemSimulation(10, G, log_path, dt)
loader = json_loader(r"solar_system.json", solarsys, G, log_path, dt)
planets = loader.load_data()
# for planet in planets:
#     solarsys.add_body(planet)
# counter = 0
# while True:
#     draw = (counter % 100 == 0)
#     solarsys.calculate_body_interactions()
#     solarsys.update_all(draw)
#     if draw:
#         solarsys.draw_all()
#     counter += 1
def update(frame):
    for _ in range(100):
        solarsys.calculate_body_interactions()
        solarsys.update_all(draw=False)
    solarsys.update_all(draw=True)
    solarsys.draw_all()
anim = animation.FuncAnimation(
    fig=solarsys.fig,
    func=update,
    frames=15*100,
    interval=1
)
if record:
    print("Recording")
    anim.save(
    'simulation.gif',
    writer='pillow',
    fps=15
    )
    print("video saved")
else:
    plt.show()