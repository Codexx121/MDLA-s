import gymnasium as gym
from gymnasium import spaces
import numpy as np
import os
import sys

# Ensure SUMO_HOME is in the path to import traci
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.path.append(os.path.join('C:\\', 'Program Files (x86)', 'Eclipse', 'Sumo', 'tools'))

import traci

class MDLASEnv(gym.Env):
    """
    Gymnasium environment for MDLA-S.
    Action Space: 5 Modes
      0: Default (L0=R, L1=S, L2=L)
      1: Left Surge (L1=S+L)
      2: Right Surge (L1=S+R)
      3: Straight Surge Right (L0=R+S)
      4: Straight Surge Left (L2=L+S)
      
    Observation Space: 9 features
      4 incoming queue lengths
      4 outgoing edge occupancies (to detect spillback)
      1 current mode
    """
    def __init__(self, sumocfg_path, gui=False):
        super(MDLASEnv, self).__init__()
        
        self.sumocfg_path = sumocfg_path
        self.gui = gui
        
        # Action Space: 5 Discrete Modes
        self.action_space = spaces.Discrete(5)
        
        # Observation Space: 4 queues + 4 occupancies + 1 mode = 9 features
        self.observation_space = spaces.Box(
            low=0.0, high=np.inf, shape=(9,), dtype=np.float32
        )
        
        self.decision_interval = 10 
        
        self.incoming_edges = ["end1_junction", "end2_junction", "end3_junction", "end4_junction"]
        self.outgoing_edges = ["junction_end1", "junction_end2", "junction_end3", "junction_end4"]
        
        self.internal_links = {} # Will store the internal lane IDs for flexible connections

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        
        try:
            traci.close()
        except:
            pass
            
        sumo_binary = "sumo-gui" if self.gui else "sumo"
        traci.start([sumo_binary, "-c", self.sumocfg_path, "--no-step-log", "true", "--waiting-time-memory", "10000", "--no-warnings", "true"])
        
        self.current_mode = 0
        self.sim_step = 0
        
        # Discover internal lane IDs for flexible connections
        self._discover_internal_links()
        
        # Apply default mode
        self._apply_mode(0)
        
        obs = self._get_obs()
        return obs, {}
    
    def _discover_internal_links(self):
        """Find the internal lane IDs for all flexible connections we added via patch.con.xml."""
        for edge in self.incoming_edges:
            self.internal_links[edge] = {
                'L0_S': None,  # Lane 0 -> Straight (flex)
                'L1_R': None,  # Lane 1 -> Right (flex)
                'L1_L': None,  # Lane 1 -> Left (flex)
                'L2_S': None,  # Lane 2 -> Straight (flex)
            }
            # L0
            for link in traci.lane.getLinks(f"{edge}_0"):
                if link[6] == 's': self.internal_links[edge]['L0_S'] = link[4]
            # L1
            for link in traci.lane.getLinks(f"{edge}_1"):
                if link[6] == 'r': self.internal_links[edge]['L1_R'] = link[4]
                if link[6] == 'l': self.internal_links[edge]['L1_L'] = link[4]
            # L2
            for link in traci.lane.getLinks(f"{edge}_2"):
                if link[6] == 's': self.internal_links[edge]['L2_S'] = link[4]

    def _get_obs(self):
        queues = []
        for edge in self.incoming_edges:
            queues.append(traci.edge.getLastStepHaltingNumber(edge))
            
        occupancies = []
        for edge in self.outgoing_edges:
            # Occupancy is returned as a percentage [0, 1] by TraCI
            occupancies.append(traci.edge.getLastStepOccupancy(edge) * 100.0) 
            
        obs = np.array(queues + occupancies + [self.current_mode], dtype=np.float32)
        return obs

    def step(self, action):
        switch_penalty = 0
        
        if action != self.current_mode:
            self._apply_mode(action)
            self.current_mode = action
            switch_penalty = 5.0 # Penalty for instability
            
        for _ in range(self.decision_interval):
            traci.simulationStep()
            self.sim_step += 1
            
        obs = self._get_obs()
        
        # Negative reward for long queues
        queue_penalty = np.sum(obs[0:4]) * 0.5 
        # Negative reward if downstream is blocked (spillback)
        spillback_penalty = np.sum(np.where(obs[4:8] > 80.0, obs[4:8], 0)) * 0.5
        
        reward = -(queue_penalty + spillback_penalty + switch_penalty)
        
        terminated = traci.simulation.getMinExpectedNumber() <= 0 or self.sim_step >= 3600
        truncated = False
        
        return obs, float(reward), terminated, truncated, {}

    def _apply_mode(self, mode):
        # Modes: 0=Default, 1=LeftSurge, 2=RightSurge, 3=StraightRight, 4=StraightLeft
        for edge in self.incoming_edges:
            links = self.internal_links[edge]
            
            # Default: Disable all flex links
            traci.lane.setAllowed(links['L0_S'], [])
            traci.lane.setAllowed(links['L1_R'], [])
            traci.lane.setAllowed(links['L1_L'], [])
            traci.lane.setAllowed(links['L2_S'], [])
            
            if mode == 1: # Left Surge
                traci.lane.setAllowed(links['L1_L'], ["all"])
            elif mode == 2: # Right Surge
                traci.lane.setAllowed(links['L1_R'], ["all"])
            elif mode == 3: # Straight Surge Right
                traci.lane.setAllowed(links['L0_S'], ["all"])
            elif mode == 4: # Straight Surge Left
                traci.lane.setAllowed(links['L2_S'], ["all"])

    def close(self):
        try:
            traci.close()
        except:
            pass

if __name__ == "__main__":
    cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Sumo Files', 'Intersection.sumocfg'))
    print(f"Loading SUMO config from: {cfg_path}")
    
    env = MDLASEnv(sumocfg_path=cfg_path, gui=False)
    obs, info = env.reset()
    print("Initial State:", obs)
    
    for i in range(5):
        action = env.action_space.sample() 
        obs, reward, term, trunc, info = env.step(action)
        print(f"Step {i+1} | Action: {action} | State: {obs} | Reward: {reward}")
        
    env.close()
    print("Sanity check completed successfully!")
