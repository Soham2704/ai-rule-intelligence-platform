import gymnasium as gym
from gymnasium import spaces
import numpy as np
import random
import os
import sys
import json

# --- Make the script project-aware ---
# This adds the main project directory to Python's path,
# allowing it to find the `mcp_client` and other top-level modules.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from mcp_client import MCPClient

class ComplexEnv(gym.Env):
    """
    This is the final, professional version of the RL environment.
    It is "city-adaptive," learning from feedback specific to a given city.
    """
    def __init__(self, city: str):
        super().__init__()
        
        self.city = city
        self.mcp_client = MCPClient()
        
        # --- 1. LOAD KNOWLEDGE SOURCES (Now City-Specific) ---
        
        # Source A: Human-in-the-Loop "Real-World" Feedback for THIS city
        human_feedback_records = self.mcp_client.get_feedback_by_city(self.city)
        human_feedback_cases = []
        for feedback in human_feedback_records:
            try:
                # This logic is simplified for the demo; a production system would be more robust
                # It now correctly looks inside the 'full_input' and 'full_output' keys from the DB
                params = feedback.full_input['parameters']
                location_map = {"urban": 0, "suburban": 1, "rural": 2}
                state = [params['plot_size'], location_map.get(params['location'], 0), params['road_width']]
                action_taken = feedback.full_output['rl_decision']['optimal_action']
                
                human_feedback_cases.append({
                    "state": state, "action_taken": action_taken,
                    "feedback": feedback.feedback_type, "source": 'human'
                })
            except (KeyError, TypeError):
                # Skip any malformed feedback records
                continue

        self.training_cases = human_feedback_cases
        
        # A robust fallback in case there are no feedback cases for this city yet
        if not self.training_cases:
            print(f"WARNING: No human feedback found for {self.city}. Using a default case for training.")
            self.training_cases = [{"state": [1000, 0, 10], "action_taken": 0, "feedback": "up", "source": "human"}]

        # --- 2. DEFINE SPACES (Unchanged) ---
        self.action_space = spaces.Discrete(5)
        low_obs = np.array([0, 0, 0]); high_obs = np.array([10000, 2, 100])
        self.observation_space = spaces.Box(low=low_obs, high=high_obs, dtype=np.float32)
        
        self.current_case = None
        print(f"ComplexEnv (City-Adaptive: {self.city}) initialized with {len(self.training_cases)} human feedback cases.")
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_case = random.choice(self.training_cases)
        return np.array(self.current_case["state"]).astype(np.float32), {}

    def step(self, action):
        # --- 3. THE REWARD LOGIC IS NOW CITY-ADAPTIVE BY DEFAULT ---
        source = self.current_case.get('source', 'human')
        
        if source == 'human':
            action_the_human_saw = self.current_case['action_taken']
            human_vote = self.current_case['feedback']
            
            if action == action_the_human_saw and human_vote == 'up': reward = 2
            elif action == action_the_human_saw and human_vote == 'down': reward = -2
            elif action != action_the_human_saw and human_vote == 'down': reward = 1
            else: reward = 0
        else: # Fallback for synthetic cases if we ever add them back
            reward = 0

        terminated = True; truncated = False; info = {}
        return np.array(self.current_case["state"]).astype(np.float32), reward, terminated, truncated, info

    def __del__(self):
        if self.mcp_client:
            self.mcp_client.close()

