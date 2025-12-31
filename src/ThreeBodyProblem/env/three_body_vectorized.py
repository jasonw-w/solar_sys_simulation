import torch
from env.batch_quicksim import FastBatchSimulation
import torch._dynamo
class VectorizedThreeBodyEnv:
    def __init__(self, num_envs, device='cuda'):
        self.num_envs = num_envs
        self.device = device
        # Initialize masses (matches gym env logic if consistent)
        self.masses = torch.tensor([1, 1, 1], dtype=torch.float32).to(device)
        
        # Initial state placeholders
        init_pos = torch.randn(num_envs, 3, 3).to(device)*5.0
        init_v = torch.randn(num_envs, 3, 3).to(device)
    
        self.sim = FastBatchSimulation(self.masses, init_pos, init_v, batch_size=self.num_envs)
        self.total_rewards = torch.zeros(self.num_envs, device=self.device)
        self.active_mask = torch.ones(self.num_envs, dtype=torch.bool, device=self.device)
        self.steps_alive = torch.zeros(self.num_envs, device=self.device)
        self.step = torch.compile(self.step)
    
    def step(self, actions):
        # Update velocities from agent actions
        new_v = actions.view(self.num_envs, 3, 3)
        self.sim.v = new_v
        self.total_rewards.fill_(0)
        self.steps_alive.fill_(0)
        self.active_mask.fill_(True)
        T = 10000
        dt = 5e-3
        check_interval = 100
        sweet_spot_coef = torch.exp(torch.tensor(-0.5, device=self.device))
        r_survival = 0.01
        r_sweet = 0.01
        r_collision = -10.0 / T
        r_escape = -20.0
        r_toofar = -10.0 / T
        for t in range(T):
            # Optimization: If all envs have "crashed/escaped", stop simulating
            if t % check_interval == 0:
                if not self.active_mask.any():
                    break
            
            pos, v = self.sim.step(dt)
            active_f = self.sim.step(dt)
            self.steps_alive += active_f
            self.total_rewards += r_survival * active_f

            p1, p2, p3 = pos[:, 0], pos[:, 1], pos[:, 2]
            d12 = (p1 - p2).norm(dim=1)
            d23 = (p2 - p3).norm(dim=1)
            d13 = (p1 - p3).norm(dim=1)
            
            dists = torch.stack([d12, d23, d13], dim=1) # Shape: (Batch, 3)
            min_dist, _ = dists.min(dim=1)
            max_dist, _ = dists.max(dim=1)
            
            collision_mask = min_dist < 0.1
            escaped_mask = max_dist > 50
            too_far_mask = max_dist > 30
            sweet_spot_mask = (max_dist > 1) & (max_dist < 10)
            
            self.total_rewards += r_collision * collision_mask.float() * active_f

            valid_escape = escaped_mask & (~collision_mask)
            self.total_rewards += r_escape * valid_escape.float() * active_f
            
            self.active_mask &= ~valid_escape
            
            valid_toofar = too_far_mask & (~escaped_mask) & (~collision_mask)
            self.total_rewards += r_toofar * valid_toofar.float() * active_f
            
            valid_sweet = sweet_spot_mask & (~collision_mask)
            self.total_rewards += r_sweet * valid_sweet.float() * active_f

        obs_pos = self.sim.pos.reshape(self.num_envs, -1)
        obs_v = self.sim.v.reshape(self.num_envs, -1)
        obs_m = self.sim.masses.squeeze(2).reshape(self.num_envs, -1)
        
        next_obs = torch.cat([obs_pos, obs_v, obs_m], dim=1)
        terminated = torch.ones(self.num_envs, device=self.device)
        
        info = {
            "avg_steps": self.steps_alive.mean().item()
        }
        
        return next_obs, self.total_rewards, terminated, info
            
    def reset(self):
        # Re-initialize simulation with random states
        init_pos = torch.randn(self.num_envs, 3, 3).to(self.device)*5.0
        init_v = torch.randn(self.num_envs, 3, 3).to(self.device)
        self.sim.reset(new_pos=init_pos, new_v=init_v)
        
        obs_pos = self.sim.pos.reshape(self.num_envs, -1)
        obs_v = self.sim.v.reshape(self.num_envs, -1)
        obs_m = self.sim.masses.squeeze(2).reshape(self.num_envs, -1)
        
        observation = torch.cat([obs_pos, obs_v, obs_m], dim=1)
        return observation