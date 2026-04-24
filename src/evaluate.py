import os
import numpy as np
import pandas as pd
import sys

# Ensure SUMO_HOME is in the path
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.path.append(os.path.join('C:\\', 'Program Files (x86)', 'Eclipse', 'Sumo', 'tools'))

import traci
from env import MDLASEnv
from stable_baselines3 import PPO

def evaluate_model(model=None, sumocfg_path="", mode_name="Baseline"):
    """
    Evaluates a specific model (or baseline if model is None) and returns metrics.
    """
    env = MDLASEnv(sumocfg_path=sumocfg_path, gui=False)
    obs, _ = env.reset()
    
    total_reward = 0
    metrics = {
        'queue_lengths': [],
        'wait_times': [],
        'throughput': 0,
        'conflicts_teleports': 0,
        'emergency_stops': 0,
    }
    
    step = 0
    terminated = False
    
    while not terminated:
        if model:
            action, _ = model.predict(obs, deterministic=True)
        else:
            action = 0 # Baseline always uses Default Mode 0
            
        obs, reward, terminated, truncated, info = env.step(int(action))
        total_reward += reward
        step += 1
        
        # Track Queue Lengths (first 4 elements of obs)
        metrics['queue_lengths'].append(np.mean(obs[0:4]))
        
        # Track wait times (from all incoming edges)
        wait_time = 0
        for edge in env.incoming_edges:
            wait_time += traci.edge.getWaitingTime(edge)
        metrics['wait_times'].append(wait_time)
        
        # Track Safety (Teleports due to collision or jamming)
        metrics['conflicts_teleports'] += traci.simulation.getStartingTeleportNumber()
        
        # Track Stability (emergency stops as a surrogate)
        metrics['emergency_stops'] += traci.simulation.getEmergencyStoppingVehiclesNumber()
        
        # Accumulate throughput
        metrics['throughput'] += traci.simulation.getArrivedNumber()
        
    env.close()
    
    # Compile Summary
    summary = {
        'Method': mode_name,
        'Avg Queue Length (veh)': np.mean(metrics['queue_lengths']),
        'Avg Intersection Wait Time (s)': np.mean(metrics['wait_times']),
        'Total Throughput (veh)': metrics['throughput'],
        'Safety (Collisions/Teleports)': metrics['conflicts_teleports'],
        'Emergency Stops (Stability)': metrics['emergency_stops'],
        'Total Reward': total_reward
    }
    
    return summary

if __name__ == "__main__":
    cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Sumo Files', 'Intersection.sumocfg'))
    model_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Results', 'Models', 'mdlas_ppo_final.zip'))
    
    print("=" * 60)
    print("  MDLA-S Evaluation: Baseline vs RL Agent")
    print("=" * 60)
    
    print("\n[1/2] Running Traditional Method (Baseline) Evaluation...")
    baseline_metrics = evaluate_model(model=None, sumocfg_path=cfg_path, mode_name="Traditional (Fixed Lanes)")
    print(f"      Done — Throughput: {baseline_metrics['Total Throughput (veh)']} veh")
    
    print("\n[2/2] Running MDLA-S Evaluation...")
    if os.path.exists(model_path):
        model = PPO.load(model_path)
        mdlas_metrics = evaluate_model(model=model, sumocfg_path=cfg_path, mode_name="MDLA-S (Dynamic RL)")
        print(f"      Done — Throughput: {mdlas_metrics['Total Throughput (veh)']} veh")
    else:
        print(f"Error: Model not found at {model_path}. Did training complete?")
        mdlas_metrics = {}

    # Compile Final Report
    if mdlas_metrics:
        df = pd.DataFrame([baseline_metrics, mdlas_metrics])
        
        # Save to CSV
        report_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Results', 'Reports'))
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, 'evaluation_report.csv')
        df.to_csv(report_path, index=False)
        
        print("\n" + "=" * 60)
        print("  EVALUATION REPORT")
        print("=" * 60)
        print(df.to_string(index=False))
        print("=" * 60)
        print(f"\nCSV saved to: {report_path}")
        
        # Improvement summary
        q_imp = baseline_metrics["Avg Queue Length (veh)"] - mdlas_metrics["Avg Queue Length (veh)"]
        t_imp = mdlas_metrics["Total Throughput (veh)"] - baseline_metrics["Total Throughput (veh)"]
        print(f"\nMDLA-S Improvement:")
        print(f"  Queue reduction:     {q_imp:+.2f} vehicles")
        print(f"  Throughput increase:  {t_imp:+d} vehicles")
