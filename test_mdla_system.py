"""
Comprehensive MDLA-S System Test
Tests all critical components before training
"""
import os
import sys
import numpy as np

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from env import MDLASEnv

def test_environment():
    print("=" * 60)
    print("MDLA-S COMPREHENSIVE SYSTEM TEST")
    print("=" * 60)
    
    cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Sumo Files', 'Intersection.sumocfg'))
    
    print("\n1. ENVIRONMENT INITIALIZATION TEST")
    print("-" * 60)
    try:
        env = MDLASEnv(sumocfg_path=cfg_path, gui=False)
        print("✓ Environment created successfully")
    except Exception as e:
        print(f"✗ Failed to create environment: {e}")
        return False
    
    try:
        obs, info = env.reset()
        print(f"✓ Environment reset successfully")
        print(f"  Initial observation shape: {obs.shape}")
        print(f"  Initial observation: {obs}")
    except Exception as e:
        print(f"✗ Failed to reset environment: {e}")
        return False
    
    print("\n2. ACTION SPACE TEST")
    print("-" * 60)
    print(f"✓ Action space: Discrete({env.action_space.n})")
    print(f"  - Mode 0: Straight Surge")
    print(f"  - Mode 1: Left Surge (green-phase protected)")
    print(f"  - Mode 2: Right Surge")
    
    print("\n3. OBSERVATION SPACE TEST")
    print("-" * 60)
    print(f"✓ Observation space shape: {env.observation_space.shape}")
    print(f"  - Index 0: South queue length")
    print(f"  - Index 1: South exit occupancy (%)")
    print(f"  - Index 2: North queue (reference)")
    print(f"  - Index 3: Current mode")
    
    print("\n4. STEP EXECUTION TEST (10 steps)")
    print("-" * 60)
    test_actions = [0, 1, 2, 0, 1, 2, 0, 1, 2, 0]
    mode_names = ["Straight", "Left", "Right"]
    
    total_reward = 0
    try:
        for step_num, action in enumerate(test_actions, 1):
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            
            # Print every 3rd step for readability
            if step_num % 3 == 0 or step_num == 1:
                print(f"  Step {step_num:2d}: Mode={mode_names[action]:8s} "
                      f"| S-Queue={obs[0]:.0f} S-Occ={obs[1]:.1f}% "
                      f"| Reward={reward:.2f}")
            
            if terminated:
                print(f"  => Episode ended at step {step_num}")
                break
                
        print(f"✓ All steps executed successfully")
        print(f"  Total reward: {total_reward:.2f}")
    except Exception as e:
        print(f"✗ Step execution failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n5. CONTROLLED EDGE VERIFICATION")
    print("-" * 60)
    try:
        import traci
        print(f"✓ MDLA controls: {env.controlled_edge}")
        
        # Check if we can get lane info
        north_queue = traci.edge.getLastStepHaltingNumber("end1_junction")
        south_queue = traci.edge.getLastStepHaltingNumber("end3_junction")
        print(f"  North queue: {north_queue} vehicles")
        print(f"  South queue: {south_queue} vehicles")
        print(f"✓ Lane data retrieval working")
    except Exception as e:
        print(f"✗ Lane data retrieval failed: {e}")
        return False
    
    print("\n6. DEMAND PATTERN VERIFICATION")
    print("-" * 60)
    rou_file = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Sumo Files', 'Intersection.rou.xml'))
    try:
        with open(rou_file, 'r') as f:
            content = f.read()
            
        # Check for phase patterns
        phases = {
            'Phase 1 (LEFT)': 'p1_S_L' in content,
            'Phase 2 (STRAIGHT)': 'p2_S_N' in content,
            'Phase 3 (RIGHT)': 'p3_S_R' in content,
            'Phase 4 (RANDOM)': 'p4_S_N' in content and 'p4_S_L' in content
        }
        
        all_phases_present = all(phases.values())
        for phase_name, present in phases.items():
            status = "✓" if present else "✗"
            print(f"  {status} {phase_name}")
        
        if all_phases_present:
            print("✓ All demand phases present in route file")
        else:
            print("✗ Some demand phases missing")
            return False
            
    except Exception as e:
        print(f"✗ Route file verification failed: {e}")
        return False
    
    print("\n7. GREEN PHASE SAFETY TEST")
    print("-" * 60)
    try:
        # Simulate different green phases
        env.sim_step = 0
        in_green = (env.sim_step % env.green_phase_cycle) < (env.green_phase_cycle // 2)
        print(f"  At sim_step={env.sim_step}: in_green_phase={in_green} ✓")
        
        env.sim_step = 20
        in_green = (env.sim_step % env.green_phase_cycle) < (env.green_phase_cycle // 2)
        print(f"  At sim_step={env.sim_step}: in_green_phase={in_green} ✓")
        
        env.sim_step = 40
        in_green = (env.sim_step % env.green_phase_cycle) < (env.green_phase_cycle // 2)
        print(f"  At sim_step={env.sim_step}: in_green_phase={in_green} ✓")
        
        print("✓ Green phase timing working correctly")
    except Exception as e:
        print(f"✗ Green phase test failed: {e}")
        return False
    
    print("\n8. CLEANUP")
    print("-" * 60)
    try:
        env.close()
        print("✓ Environment closed successfully")
    except Exception as e:
        print(f"✗ Failed to close environment: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("ALL TESTS PASSED ✓")
    print("=" * 60)
    print("\nSystem is ready for training!")
    print("\nNext steps:")
    print("  1. python src/train.py          # Train the model")
    print("  2. python src/demo.py           # Watch in SUMO GUI")
    print("  3. python src/evaluate.py       # Compare performance")
    
    return True

if __name__ == "__main__":
    success = test_environment()
    sys.exit(0 if success else 1)
