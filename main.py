from vector import Vector
from solar_system import Solar_system
from body import solar_sys_body
solar_sys = Solar_system(400)
body = solar_sys_body(solar_sys, 100, velocity=(1,1,1))
body2 = solar_sys_body(solar_sys, 20, (0.5, 0.5, 0.5), (0, 0, 0))
for _ in range(100):
    solar_sys.update_all()
    solar_sys.draw_all()