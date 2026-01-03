from ThreeBodyProblem.RL_agent.model import Actor_Critic
import os
import json
import torch
import numpy as np
from pathlib import Path


def create_body(name, body_id, mass, position, velocity, colour, simulation=1, create_stable_orbit=0, eccentricity=0, central_body_id=0):
    if central_body_id == body_id:
        central_body_id = None
    return {
        "name": name,
        "id": body_id,
        "mass": mass,
        "initial_position": position,
        "initial_velocity": velocity,
        "create_stable_orbit": create_stable_orbit,
        "eccentricity": eccentricity,
        "id_of_central_body": central_body_id,
        "colour": colour,
        "simulation": simulation,
    }


def main():
    masses_val = [1.0, 1.0, 1.0]
    base_dir = Path(__file__).resolve().parents[2]

    model_path = Path("best_agent.pth")
    if not model_path.exists():
        alt_model = base_dir.parent / "best_agent.pth"
        if alt_model.exists():
            model_path = alt_model

    if not model_path.exists():
        print("Error: best_agent.pth not found.")
        return

    data_dir = base_dir / "system_simulation" / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    output_path = data_dir / "predicted_system.json"

    device = "cuda" if torch.cuda.is_available() else "cpu"

    agent = Actor_Critic(21, 9).to(device)
    agent.load_state_dict(torch.load(model_path, map_location=device))
    agent.eval()

    abs_pos = torch.randn(3, 3).to(device) * 5.0

    r12 = abs_pos[0] - abs_pos[1]
    r23 = abs_pos[1] - abs_pos[2]
    r31 = abs_pos[2] - abs_pos[0]
    flat_rel_pos = torch.cat([r12, r23, r31])

    dummy_vel = torch.randn(3, 3).to(device)
    flat_vel = dummy_vel.flatten()

    mass_tensor = torch.tensor(masses_val, dtype=torch.float32).to(device)

    state_vector = torch.cat([flat_rel_pos, flat_vel, mass_tensor]).unsqueeze(0)

    with torch.no_grad():
        action_mean, _, _ = agent(state_vector)
        predicted_velocities = action_mean.cpu().numpy()[0].reshape(3, 3)

    positions_np = abs_pos.cpu().numpy()

    planets = []
    colors = ["yellow", "blue", "grey"]
    names = ["Star", "Planet1", "Planet2"]

    for i in range(3):
        body = create_body(
            name=names[i],
            body_id=i,
            mass=masses_val[i],
            position=positions_np[i].tolist(),
            velocity=predicted_velocities[i].tolist(),
            colour=colors[i],
            simulation=1,
            create_stable_orbit=0,
            eccentricity=0,
            central_body_id=0 if i > 0 else None,
        )
        planets.append(body)

    system_data = {"planets": planets}

    with open(output_path, "w") as f:
        json.dump(system_data, f, indent=2)

    print(f"Generated {output_path}")
    print(f"Body 0 Pos: {positions_np[0]}")
    print(f"Body 0 Vel: {predicted_velocities[0]}")


if __name__ == "__main__":
    main()
