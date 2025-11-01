"""
City-Adaptive Reinforcement Learning Environment
-------------------------------------------------
An enhanced RL environment that adapts rewards based on city-specific
feedback patterns and learns city-specific rule preferences.
"""

import gymnasium as gym
import numpy as np
from typing import Dict, List, Optional
import json
import os


class CityAdaptiveEnv(gym.Env):
    """
    RL Environment with city-specific reward weighting based on user feedback.
    
    The environment maintains a reward table per city that gets updated
    based on thumbs up/down feedback from users. Cities with more positive
    feedback on certain rule combinations get higher reward weights.
    """
    
    metadata = {"render_modes": ["human"], "render_fps": 30}
    
    def __init__(self, reward_config_path: str = "rl_env/city_reward_table.json"):
        super().__init__()
        
        # State space: [plot_size, location_encoded, road_width, city_encoded]
        # Expanded to include city as part of the state
        self.observation_space = gym.spaces.Box(
            low=np.array([0, 0, 0, 0], dtype=np.float32),
            high=np.array([10000, 2, 100, 10], dtype=np.float32),
            dtype=np.float32
        )
        
        # Action space: Different FSI recommendation levels
        # 0: Low FSI (1.0-1.5), 1: Medium FSI (1.5-2.5), 2: High FSI (2.5-3.5)
        self.action_space = gym.spaces.Discrete(3)
        
        # City encoding
        self.city_map = {
            "Mumbai": 0,
            "Pune": 1,
            "Ahmedabad": 2,
            "Nashik": 3,
            "Delhi": 4,
            "Bangalore": 5,
            # Add more cities as needed
        }
        
        # Location encoding
        self.location_map = {"urban": 0, "suburban": 1, "rural": 2}
        
        # City-specific reward weights (loaded from file or initialized)
        self.reward_config_path = reward_config_path
        self.city_reward_weights = self._load_reward_weights()
        
        # Current state
        self.current_city = "Mumbai"
        self.state = None
        
        print(f"✓ CityAdaptiveEnv initialized with {len(self.city_reward_weights)} cities")
    
    def _load_reward_weights(self) -> Dict[str, Dict]:
        """Load city-specific reward weights from file"""
        if os.path.exists(self.reward_config_path):
            try:
                with open(self.reward_config_path, 'r') as f:
                    weights = json.load(f)
                print(f"✓ Loaded reward weights from {self.reward_config_path}")
                return weights
            except Exception as e:
                print(f"⚠ Could not load reward weights: {e}")
        
        # Initialize default weights for all cities
        default_weights = {
            city: {
                "base_reward": 1.0,
                "action_weights": [1.0, 1.0, 1.0],  # Weights for each action
                "positive_feedback_count": 0,
                "negative_feedback_count": 0,
                "total_cases": 0
            }
            for city in self.city_map.keys()
        }
        
        # Save default weights
        self._save_reward_weights(default_weights)
        return default_weights
    
    def _save_reward_weights(self, weights: Dict[str, Dict]):
        """Save city-specific reward weights to file"""
        os.makedirs(os.path.dirname(self.reward_config_path), exist_ok=True)
        with open(self.reward_config_path, 'w') as f:
            json.dump(weights, indent=2, fp=f)
    
    def update_city_weights_from_feedback(
        self, 
        city: str, 
        action: int, 
        feedback_type: str
    ):
        """
        Update city-specific reward weights based on user feedback.
        
        Args:
            city: City name (e.g., "Mumbai")
            action: Action taken by the agent (0, 1, or 2)
            feedback_type: "up" or "down"
        """
        if city not in self.city_reward_weights:
            print(f"⚠ City {city} not in reward table, adding...")
            self.city_reward_weights[city] = {
                "base_reward": 1.0,
                "action_weights": [1.0, 1.0, 1.0],
                "positive_feedback_count": 0,
                "negative_feedback_count": 0,
                "total_cases": 0
            }
        
        city_data = self.city_reward_weights[city]
        city_data["total_cases"] += 1
        
        # Update feedback counts
        if feedback_type == "up":
            city_data["positive_feedback_count"] += 1
            # Increase weight for this action
            city_data["action_weights"][action] *= 1.1  # 10% increase
        elif feedback_type == "down":
            city_data["negative_feedback_count"] += 1
            # Decrease weight for this action
            city_data["action_weights"][action] *= 0.9  # 10% decrease
        
        # Normalize weights to keep them reasonable
        max_weight = max(city_data["action_weights"])
        if max_weight > 2.0:
            city_data["action_weights"] = [w / max_weight * 2.0 for w in city_data["action_weights"]]
        
        # Calculate approval rate
        total_feedback = city_data["positive_feedback_count"] + city_data["negative_feedback_count"]
        if total_feedback > 0:
            approval_rate = city_data["positive_feedback_count"] / total_feedback
            # Adjust base reward based on overall approval
            city_data["base_reward"] = 0.5 + approval_rate  # Range: 0.5 to 1.5
        
        # Save updated weights
        self._save_reward_weights(self.city_reward_weights)
        
        print(f"✓ Updated weights for {city}: action {action} -> {city_data['action_weights'][action]:.3f}")
    
    def reset(self, seed: Optional[int] = None, options: Optional[dict] = None):
        """Reset the environment to initial state"""
        super().reset(seed=seed)
        
        # Extract city from options if provided
        if options and "city" in options:
            self.current_city = options["city"]
        else:
            # Randomly select a city for training diversity
            self.current_city = np.random.choice(list(self.city_map.keys()))
        
        # Generate random parameters for the case
        plot_size = np.random.uniform(500, 5000)
        location = np.random.choice([0, 1, 2])  # urban, suburban, rural
        road_width = np.random.uniform(6, 30)
        city_encoded = self.city_map.get(self.current_city, 0)
        
        self.state = np.array([plot_size, location, road_width, city_encoded], dtype=np.float32)
        
        return self.state, {}
    
    def step(self, action: int):
        """
        Execute one step in the environment.
        
        Args:
            action: Chosen action (FSI level: 0=Low, 1=Medium, 2=High)
            
        Returns:
            observation, reward, terminated, truncated, info
        """
        plot_size, location, road_width, city_encoded = self.state
        
        # Get city-specific weights
        city_data = self.city_reward_weights.get(self.current_city, {
            "base_reward": 1.0,
            "action_weights": [1.0, 1.0, 1.0]
        })
        
        base_reward = city_data["base_reward"]
        action_weight = city_data["action_weights"][action]
        
        # Calculate reward based on the "oracle" logic with city weighting
        reward = self._calculate_reward(plot_size, location, road_width, action)
        
        # Apply city-specific weighting
        weighted_reward = reward * base_reward * action_weight
        
        # Episode is done after one step (episodic task)
        terminated = True
        truncated = False
        
        info = {
            "city": self.current_city,
            "base_reward": reward,
            "city_weight": base_reward,
            "action_weight": action_weight,
            "final_reward": weighted_reward
        }
        
        return self.state, weighted_reward, terminated, truncated, info
    
    def _calculate_reward(self, plot_size: float, location: int, road_width: float, action: int) -> float:
        """
        Calculate base reward using rule-based oracle logic.
        
        This represents the "correct" FSI choice based on parameters.
        """
        # Determine optimal action based on parameters
        optimal_action = None
        
        # High FSI conditions (Action 2)
        if plot_size > 2000 and road_width > 18 and location == 0:  # Urban, large plot, wide road
            optimal_action = 2
        # Medium FSI conditions (Action 1)
        elif plot_size > 1000 and road_width > 12:
            optimal_action = 1
        # Low FSI conditions (Action 0)
        else:
            optimal_action = 0
        
        # Reward structure
        if action == optimal_action:
            return 10.0  # Correct action
        elif abs(action - optimal_action) == 1:
            return 2.0   # Close, but not optimal
        else:
            return -5.0  # Wrong action
    
    def render(self):
        """Render the environment (optional)"""
        if self.state is not None:
            print(f"City: {self.current_city}")
            print(f"State: Plot={self.state[0]:.0f}sqm, Location={self.state[1]}, Road={self.state[2]:.1f}m")


def test_city_adaptive_env():
    """Test the city-adaptive environment"""
    print("="*80)
    print("Testing CityAdaptiveEnv")
    print("="*80)
    
    env = CityAdaptiveEnv()
    
    # Test 1: Reset with different cities
    print("\n--- Test 1: Reset with different cities ---")
    for city in ["Mumbai", "Pune", "Ahmedabad"]:
        obs, info = env.reset(options={"city": city})
        print(f"{city}: State = {obs}")
    
    # Test 2: Simulate feedback updates
    print("\n--- Test 2: Simulate feedback updates ---")
    
    # Mumbai users like high FSI (action 2)
    for _ in range(5):
        env.update_city_weights_from_feedback("Mumbai", action=2, feedback_type="up")
    
    # Pune users dislike high FSI
    for _ in range(3):
        env.update_city_weights_from_feedback("Pune", action=2, feedback_type="down")
    
    # Pune users like medium FSI (action 1)
    for _ in range(4):
        env.update_city_weights_from_feedback("Pune", action=1, feedback_type="up")
    
    print("\n--- Updated City Weights ---")
    print(json.dumps(env.city_reward_weights, indent=2))
    
    # Test 3: Check reward differences
    print("\n--- Test 3: Reward differences for action 2 ---")
    
    obs_mumbai, _ = env.reset(options={"city": "Mumbai"})
    _, reward_mumbai, _, _, info_mumbai = env.step(action=2)
    print(f"Mumbai action 2 reward: {reward_mumbai:.2f} (weight: {info_mumbai['action_weight']:.3f})")
    
    obs_pune, _ = env.reset(options={"city": "Pune"})
    _, reward_pune, _, _, info_pune = env.step(action=2)
    print(f"Pune action 2 reward: {reward_pune:.2f} (weight: {info_pune['action_weight']:.3f})")
    
    print("\n✓ CityAdaptiveEnv test complete!")


if __name__ == "__main__":
    test_city_adaptive_env()
