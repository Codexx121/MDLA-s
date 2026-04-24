import os
import time
import sys

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.path.append(os.path.join('C:\\', 'Program Files (x86)', 'Eclipse', 'Sumo', 'tools'))

import traci
from stable_baselines3 import PPO
from env import MDLASEnv

def run_demo():
    print("Initializing MDLA-S GUI Demonstration...")
    
    cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Sumo Files', 'Intersection.sumocfg'))
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Results', 'Models', 'mdlas_ppo_final.zip'))
    
    if not os.path.exists(model_path):
        print(f"Error: Model not found at {model_path}. Please train the model first.")
        return

    print("Loading RL Model...")
    model = PPO.load(model_path)
    
    print("Launching SUMO-GUI... (Please switch to the SUMO window and press the green PLAY button)")
    # Initialize the environment with GUI enabled
    env = MDLASEnv(sumocfg_path=cfg_path, gui=True)
    obs, _ = env.reset()
    
    terminated = False
    
    try:
        # Run the simulation until it finishes
        while not terminated:
            # Ask the RL model what to do based on the current traffic queues
            action, _ = model.predict(obs, deterministic=True)
            
            # Apply the action and advance the simulation
            obs, reward, terminated, truncated, info = env.step(int(action))
            
            mode_names = ["Default", "Left Surge", "Right Surge", "Straight Surge Right", "Straight Surge Left"]
            
            # obs: [Q_North, Q_East, Q_South, Q_West, Occ_N, Occ_E, Occ_S, Occ_W, Mode]
            q_n, q_e, q_s, q_w = obs[0], obs[1], obs[2], obs[3]
            
            # Determine demand phase for context
            phase_msg = "Random Background"
            if 0 <= env.sim_step < 200: phase_msg = "Custom Phase 1: RIGHT Surge"
            elif 200 <= env.sim_step < 400: phase_msg = "Custom Phase 2: STRAIGHT Surge"
            elif 400 <= env.sim_step < 600: phase_msg = "Custom Phase 3: LEFT Surge"
            elif 600 <= env.sim_step < 800: phase_msg = "Custom Phase 4: STRAIGHT Surge"

            print(f"\n--- Simulation Time: {env.sim_step}s | Phase: {phase_msg} ---")
            print(f"Queues -> North: {q_n:.1f} | East: {q_e:.1f} | South: {q_s:.1f} | West: {q_w:.1f}")
            print(f"Decision: {mode_names[action]} (Applied to ALL 4 Approaches simultaneously)")
            
            # Adding a slight delay so it's easier to watch in the GUI
            time.sleep(0.05)
            
        print("Demonstration Complete!")
    except traci.exceptions.FatalTraCIError:
        print("\nSimulation closed by user.")
    finally:
        env.close()

if __name__ == "__main__":
    run_demo()
