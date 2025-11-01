import numpy as np
import os
import sys
from stable_baselines3 import PPO
import argparse
import json

# --- Make the script project-aware ---
# This adds the main project directory to Python's path,
# allowing it to find the `mcp_client` and other top-level modules.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# --- Now, the imports will work correctly ---
from rl_env.complex_env import ComplexEnv
from stable_baselines3.common.callbacks import BaseCallback

# --- The "Flight Recorder": A professional callback for logging the reward curve ---
class RewardCurveCallback(BaseCallback):
    """
    A custom callback to log the reward curve to a structured JSONL file.
    """
    def __init__(self, log_path: str, verbose=0):
        super(RewardCurveCallback, self).__init__(verbose)
        self.log_path = log_path
        # Clear the log file at the beginning of each training run
        if os.path.exists(self.log_path):
            os.remove(self.log_path)

    def _on_step(self) -> bool:
        # Check if the mean reward is available in the logs (it becomes available every rollout)
        if 'rollout/ep_rew_mean' in self.locals['infos'][0]:
            mean_reward = self.locals['infos'][0]['rollout/ep_rew_mean']
            
            log_entry = {
                "timestep": self.num_timesteps,
                "mean_reward": round(mean_reward, 2)
            }
            
            # Append the log entry to the file
            with open(self.log_path, "a") as f:
                f.write(json.dumps(log_entry) + "\n")
                
        return True # Tell Stable-Baselines to continue training

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train a city-adaptive RL agent.")
    parser.add_argument("--city", type=str, default="Mumbai", help="The city to train an expert agent for (e.g., Mumbai, Pune).")
    args = parser.parse_args()

    CITY_TO_TRAIN = args.city.capitalize()
    print(f"\n--- Starting Training for City: {CITY_TO_TRAIN} ---")

    # --- Create the City-Specific Environment ---
    # We now pass the city name when creating the environment.
    env = ComplexEnv(city=CITY_TO_TRAIN)

    # --- Create the "Flight Recorder" Callback ---
    log_dir = "reports"
    os.makedirs(log_dir, exist_ok=True)
    reward_log_path = os.path.join(log_dir, f"rl_training_log_{CITY_TO_TRAIN.lower()}.jsonl")
    callback = RewardCurveCallback(log_path=reward_log_path)

    # --- Create and Train the Agent with the "Smarter Brain" ---
    # This uses the advanced configuration to encourage exploration and prevent a "lazy" agent.
    policy_kwargs = dict(net_arch=dict(pi=[128, 128], vf=[128, 128]))
    agent = PPO(
        "MlpPolicy", 
        env, 
        policy_kwargs=policy_kwargs, 
        ent_coef=0.01, # The "curiosity" bonus
        verbose=0
    ) 

    print(f"\n--- Starting Human-in-the-Loop RL Training for {CITY_TO_TRAIN} (100k steps)... ---")
    agent.learn(total_timesteps=100000, callback=callback)
    print("--- Training Complete. ---")

    # --- Save the Final, City-Specific Model ---
    output_path = f"rl_env/ppo_{CITY_TO_TRAIN.lower()}_hirl_agent.zip"
    agent.save(output_path)
    print(f"Human-in-the-Loop trained agent for {CITY_TO_TRAIN} saved to {output_path}")
    print(f"Training reward curve saved to {reward_log_path}")

    # --- Test the newly trained agent ---
    print(f"\n--- Testing Trained Agent for {CITY_TO_TRAIN} ---")
    
    num_test_cases = 10
    
    for i in range(num_test_cases):
        obs, _ = env.reset()
        action, _ = agent.predict(obs, deterministic=True)
        print(f"  - Test Case {i+1}: For state {np.round(obs, 2)}, Agent chose action: {action}")

    print("\n--- Test complete. ---")