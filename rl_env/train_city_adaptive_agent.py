"""
Train City-Adaptive RL Agent
-----------------------------
Trains a PPO agent on the city-adaptive environment that learns
city-specific preferences from user feedback.
"""

from city_adaptive_env import CityAdaptiveEnv
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import BaseCallback
from stable_baselines3.common.logger import configure
import numpy as np
import json
import os
from datetime import datetime


class CityMetricsCallback(BaseCallback):
    """
    Callback to log city-specific metrics during training
    """
    def __init__(self, verbose=0):
        super().__init__(verbose)
        self.city_rewards = {}
    
    def _on_step(self) -> bool:
        # Log rewards per city
        if 'city' in self.locals.get('infos', [{}])[0]:
            city = self.locals['infos'][0]['city']
            reward = self.locals.get('rewards', [0])[0]
            
            if city not in self.city_rewards:
                self.city_rewards[city] = []
            
            self.city_rewards[city].append(reward)
        
        return True
    
    def _on_training_end(self) -> None:
        print("\n" + "="*80)
        print("CITY-SPECIFIC TRAINING METRICS")
        print("="*80)
        
        for city, rewards in self.city_rewards.items():
            avg_reward = np.mean(rewards)
            std_reward = np.std(rewards)
            print(f"{city:15s}: Avg Reward = {avg_reward:7.2f} ± {std_reward:6.2f} ({len(rewards)} episodes)")


def sync_feedback_from_mcp_to_env(env: CityAdaptiveEnv):
    """
    Sync user feedback from MCP database to the RL environment's reward weights.
    
    This allows the RL agent to learn from actual user preferences.
    """
    try:
        from database_setup import SessionLocal, Feedback, ReasoningOutput
        
        print("\n--- Syncing feedback from MCP to RL environment ---")
        
        db = SessionLocal()
        
        # Get all feedback records
        feedback_records = db.query(Feedback).all()
        
        if not feedback_records:
            print("⚠ No feedback records found in MCP")
            db.close()
            return
        
        # Group by city and action
        city_action_feedback = {}
        
        for fb in feedback_records:
            city = fb.city
            feedback_type = fb.feedback_type  # "up" or "down"
            
            # Try to extract action from the output report
            # In a real scenario, we'd store the action directly in the feedback table
            output_report = fb.full_output
            
            # For now, simulate action extraction based on rules applied
            # This would need to be adapted based on your actual data structure
            action = 1  # Default to medium FSI
            
            if output_report and isinstance(output_report, dict):
                rules_applied = output_report.get('rules_applied', [])
                # Simple heuristic: if many rules applied, likely high FSI recommendation
                if len(rules_applied) > 2:
                    action = 2
                elif len(rules_applied) == 0:
                    action = 0
            
            # Update environment weights
            env.update_city_weights_from_feedback(city, action, feedback_type)
        
        db.close()
        
        print(f"✓ Synced {len(feedback_records)} feedback records to RL environment")
        print(f"✓ Updated weights for {len(env.city_reward_weights)} cities")
        
    except Exception as e:
        print(f"⚠ Could not sync feedback from MCP: {e}")


def train_city_adaptive_agent(
    total_timesteps: int = 50000,
    sync_mcp_feedback: bool = True,
    model_save_path: str = "rl_env/ppo_city_adaptive_agent.zip"
):
    """
    Train a city-adaptive PPO agent.
    
    Args:
        total_timesteps: Number of training steps
        sync_mcp_feedback: Whether to sync feedback from MCP before training
        model_save_path: Path to save the trained model
    """
    print("="*80)
    print("TRAINING CITY-ADAPTIVE RL AGENT")
    print("="*80)
    
    # Create environment
    env = CityAdaptiveEnv()
    
    # Sync feedback from MCP if requested
    if sync_mcp_feedback:
        sync_feedback_from_mcp_to_env(env)
    
    # Create callback
    callback = CityMetricsCallback()
    
    # Configure logger
    log_dir = "rl_env/logs/city_adaptive"
    os.makedirs(log_dir, exist_ok=True)
    
    # Create PPO agent with enhanced config for multi-city learning
    print("\n--- Creating PPO Agent ---")
    agent = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        tensorboard_log=log_dir
    )
    
    # Train the agent
    print("\n--- Starting Training ---")
    print(f"Total timesteps: {total_timesteps}")
    
    agent.learn(
        total_timesteps=total_timesteps,
        callback=callback,
        progress_bar=True
    )
    
    print("\n--- Training Complete ---")
    
    # Save the model
    agent.save(model_save_path)
    print(f"✓ Model saved to: {model_save_path}")
    
    # Save training metadata
    metadata = {
        "training_date": datetime.utcnow().isoformat() + "Z",
        "total_timesteps": total_timesteps,
        "cities_trained": list(env.city_reward_weights.keys()),
        "city_weights": env.city_reward_weights
    }
    
    metadata_path = model_save_path.replace(".zip", "_metadata.json")
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"✓ Metadata saved to: {metadata_path}")
    
    # Test the trained agent
    print("\n" + "="*80)
    print("TESTING TRAINED AGENT")
    print("="*80)
    
    test_cities = ["Mumbai", "Pune", "Ahmedabad"]
    
    for city in test_cities:
        print(f"\n--- Testing {city} ---")
        
        # Reset environment for this city
        obs, _ = env.reset(options={"city": city})
        
        # Predict action
        action, _ = agent.predict(obs, deterministic=True)
        
        # Get action probabilities
        import torch
        obs_tensor = torch.as_tensor(obs, device=agent.device).reshape(1, -1)
        distribution = agent.policy.get_distribution(obs_tensor)
        action_probs = distribution.distribution.probs.detach().cpu().numpy()[0]
        
        print(f"State: Plot={obs[0]:.0f}sqm, Location={int(obs[1])}, Road={obs[2]:.1f}m")
        print(f"Chosen Action: {action} (Low=0, Med=1, High=2)")
        print(f"Action Probabilities: {action_probs}")
        print(f"Confidence: {action_probs[action]:.1%}")
        
        # Show city weights
        city_data = env.city_reward_weights.get(city, {})
        if city_data:
            print(f"City Weights: {city_data.get('action_weights', [])}")
            print(f"Approval Rate: {city_data.get('positive_feedback_count', 0) / max(1, city_data.get('total_cases', 1)):.1%}")
    
    print("\n" + "="*80)
    print("✓ TRAINING COMPLETE!")
    print("="*80)
    
    return agent, env


if __name__ == "__main__":
    # Train the agent
    trained_agent, trained_env = train_city_adaptive_agent(
        total_timesteps=20000,  # Reduced for quick training
        sync_mcp_feedback=True
    )
    
    print("\n✓ City-adaptive agent training complete!")
    print("✓ The agent is now ready to provide city-specific recommendations")
