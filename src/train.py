import os
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.callbacks import CheckpointCallback

# Import our custom environment
from env import MDLASEnv

def make_env():
    cfg_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Sumo Files', 'Intersection.sumocfg'))
    return MDLASEnv(sumocfg_path=cfg_path, gui=False)

if __name__ == "__main__":
    print("Initializing MDLA-S Training...")
    
    # Define paths
    models_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Results', 'Models'))
    logs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Results', 'Logs'))
    os.makedirs(models_dir, exist_ok=True)
    os.makedirs(logs_dir, exist_ok=True)

    # Wrap environment
    vec_env = make_vec_env(make_env, n_envs=1)

    # Setup PPO Model
    model = PPO(
        "MlpPolicy",
        vec_env,
        verbose=1,
        learning_rate=0.0003,
        n_steps=1024,
        batch_size=64,
        n_epochs=10,
        gamma=0.99
    )

    # Save model periodically
    checkpoint_callback = CheckpointCallback(save_freq=5000, save_path=models_dir, name_prefix='mdlas_model')

    print("Starting Training (This will take a few minutes)...")
    try:
        model.learn(total_timesteps=10000, callback=checkpoint_callback, tb_log_name="PPO_MDLA_S")
        print("Training Complete!")
        
        # Save the final model
        final_model_path = os.path.join(models_dir, "mdlas_ppo_final")
        model.save(final_model_path)
        print(f"Final model saved to {final_model_path}.zip")
        
    except KeyboardInterrupt:
        print("Training interrupted manually.")
        model.save(os.path.join(models_dir, "mdlas_ppo_interrupted"))
    finally:
        vec_env.close()
