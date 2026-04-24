"""
Quick training test to verify PPO works
"""
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from env import MDLASEnv
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env

print("Testing PPO Training Pipeline...")
print("=" * 60)

cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Sumo Files', 'Intersection.sumocfg'))

def make_env():
    return MDLASEnv(sumocfg_path=cfg_path, gui=False)

try:
    print("\n1. Creating environment wrapper...")
    vec_env = make_vec_env(make_env, n_envs=1)
    print("   OK - Environment wrapper created")
    
    print("\n2. Creating PPO model...")
    model = PPO('MlpPolicy', vec_env, verbose=0, learning_rate=0.0003)
    print("   OK - PPO model created successfully")
    print(f"   Policy network: {model.policy}")
    
    print("\n3. Running mini-training (256 timesteps)...")
    model.learn(total_timesteps=256)
    print("   OK - Training completed successfully")
    
    print("\n4. Testing prediction...")
    dummy_env = MDLASEnv(sumocfg_path=cfg_path, gui=False)
    obs, _ = dummy_env.reset()
    action, _ = model.predict(obs, deterministic=True)
    print(f"   OK - Prediction works: action={action}")
    dummy_env.close()
    
    print("\n5. Saving model...")
    test_path = os.path.join(os.path.dirname(__file__), 'Results', 'Models', 'test_model.zip')
    os.makedirs(os.path.dirname(test_path), exist_ok=True)
    model.save(test_path)
    print(f"   OK - Model saved to {test_path}")
    
    print("\n6. Loading model...")
    loaded_model = PPO.load(test_path)
    print("   OK - Model loaded successfully")
    
    print("\n7. Cleanup...")
    vec_env.close()
    print("   OK - Environment closed")
    
    print("\n" + "=" * 60)
    print("SUCCESS! Training pipeline works perfectly!")
    print("=" * 60)
    
except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
