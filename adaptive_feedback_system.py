"""
Adaptive Feedback Integration System
-------------------------------------
Connects user feedback to RL training and confidence scoring in a visible, transparent way.

Key Features:
1. Real-time feedback processing
2. City-specific reward weight updates
3. Confidence score adjustments based on approval rates
4. Transparent audit trail of adaptations
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Tuple
from database_setup import SessionLocal, Feedback, ReasoningOutput
import numpy as np


class AdaptiveFeedbackSystem:
    """
    Manages the complete feedback loop:
    User Feedback → Reward Weights → RL Training → Confidence Scoring
    """
    
    def __init__(self, reward_table_path: str = "rl_env/city_reward_table.json"):
        self.reward_table_path = reward_table_path
        self.reward_weights = self._load_reward_weights()
        self.db = SessionLocal()
        self.feedback_history = []
        
    def _load_reward_weights(self) -> Dict[str, Any]:
        """Load current city-specific reward weights"""
        if os.path.exists(self.reward_table_path):
            with open(self.reward_table_path, 'r') as f:
                return json.load(f)
        return {}
    
    def _save_reward_weights(self):
        """Save updated reward weights"""
        with open(self.reward_table_path, 'w') as f:
            json.dump(self.reward_weights, f, indent=2)
    
    def process_feedback(
        self, 
        case_id: str, 
        project_id: str,
        city: str, 
        feedback_type: str,
        input_params: Dict[str, Any],
        output_report: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Process a single feedback event and update the system adaptively.
        
        Returns:
            Dictionary with:
            - feedback_recorded: bool
            - weights_updated: bool
            - new_city_weights: Dict
            - confidence_adjustment: float
            - audit_trail: List[str]
        """
        audit_trail = []
        audit_trail.append(f"[{datetime.utcnow().isoformat()}] Processing feedback for {case_id}")
        
        # 1. Record feedback in database
        feedback_record = Feedback(
            id=f"fb_{datetime.utcnow().timestamp()}",
            case_id=case_id,
            project_id=project_id,
            city=city,
            feedback_type=feedback_type,
            timestamp=datetime.utcnow().isoformat() + "Z",
            full_input=input_params,
            full_output=output_report
        )
        self.db.add(feedback_record)
        self.db.commit()
        audit_trail.append(f"✓ Feedback recorded in MCP database")
        
        # 2. Update city-specific reward weights
        if city not in self.reward_weights:
            self.reward_weights[city] = {
                "base_reward": 1.0,
                "action_weights": [1.0, 1.0, 1.0],  # Low, Med, High FSI
                "positive_feedback_count": 0,
                "negative_feedback_count": 0,
                "total_cases": 0
            }
        
        city_data = self.reward_weights[city]
        city_data["total_cases"] += 1
        
        if feedback_type == "up":
            city_data["positive_feedback_count"] += 1
            weight_delta = 0.05  # Increase weight for chosen action
            audit_trail.append(f"📈 Positive feedback: Increasing reward weight")
        else:
            city_data["negative_feedback_count"] += 1
            weight_delta = -0.03  # Decrease weight for chosen action
            audit_trail.append(f"📉 Negative feedback: Decreasing reward weight")
        
        # 3. Extract the action from the output report (FSI level)
        action = self._infer_action_from_output(output_report)
        audit_trail.append(f"🎯 Inferred action: {['Low FSI', 'Medium FSI', 'High FSI'][action]}")
        
        # 4. Adjust action weights
        old_weight = city_data["action_weights"][action]
        city_data["action_weights"][action] = max(0.1, min(2.0, old_weight + weight_delta))
        new_weight = city_data["action_weights"][action]
        audit_trail.append(f"⚖️  Weight change: {old_weight:.3f} → {new_weight:.3f}")
        
        # 5. Calculate approval rate and confidence adjustment
        approval_rate = city_data["positive_feedback_count"] / max(1, city_data["total_cases"])
        confidence_adjustment = self._calculate_confidence_adjustment(approval_rate)
        audit_trail.append(f"📊 City approval rate: {approval_rate:.1%}")
        audit_trail.append(f"🎚️  Confidence adjustment factor: {confidence_adjustment:.3f}")
        
        # 6. Save updated weights
        self._save_reward_weights()
        audit_trail.append(f"💾 Reward weights saved to {self.reward_table_path}")
        
        # 7. Log the feedback event
        self.feedback_history.append({
            "timestamp": datetime.utcnow().isoformat(),
            "case_id": case_id,
            "city": city,
            "feedback_type": feedback_type,
            "action": action,
            "weight_change": new_weight - old_weight,
            "approval_rate": approval_rate
        })
        
        return {
            "feedback_recorded": True,
            "weights_updated": True,
            "city": city,
            "new_city_weights": city_data["action_weights"],
            "approval_rate": approval_rate,
            "confidence_adjustment": confidence_adjustment,
            "audit_trail": audit_trail
        }
    
    def _infer_action_from_output(self, output_report: Dict[str, Any]) -> int:
        """
        Infer the RL action (FSI level) from the output report.
        
        Action mapping:
        0: Low FSI (< 1.5)
        1: Medium FSI (1.5 - 2.5)
        2: High FSI (> 2.5)
        """
        rules_applied = output_report.get("rules_applied", [])
        
        # Extract FSI from first rule if available
        if rules_applied:
            # This is a simplified heuristic; in production, you'd parse the actual FSI
            if len(rules_applied) > 2:
                return 2  # High FSI (many rules = complex development)
            elif len(rules_applied) > 0:
                return 1  # Medium FSI
        
        return 0  # Default to low FSI
    
    def _calculate_confidence_adjustment(self, approval_rate: float) -> float:
        """
        Calculate confidence adjustment factor based on approval rate.
        
        High approval rate → Higher confidence multiplier
        Low approval rate → Lower confidence multiplier
        """
        if approval_rate >= 0.85:
            return 1.1  # Boost confidence by 10%
        elif approval_rate >= 0.70:
            return 1.0  # No adjustment
        elif approval_rate >= 0.50:
            return 0.9  # Reduce confidence by 10%
        else:
            return 0.8  # Reduce confidence by 20%
    
    def get_city_statistics(self, city: str) -> Dict[str, Any]:
        """Get comprehensive statistics for a specific city"""
        if city not in self.reward_weights:
            return {
                "city": city,
                "total_cases": 0,
                "approval_rate": 0.0,
                "action_weights": [1.0, 1.0, 1.0],
                "status": "No data yet"
            }
        
        city_data = self.reward_weights[city]
        approval_rate = city_data["positive_feedback_count"] / max(1, city_data["total_cases"])
        
        return {
            "city": city,
            "total_cases": city_data["total_cases"],
            "positive_feedback": city_data["positive_feedback_count"],
            "negative_feedback": city_data["negative_feedback_count"],
            "approval_rate": approval_rate,
            "action_weights": city_data["action_weights"],
            "confidence_multiplier": self._calculate_confidence_adjustment(approval_rate),
            "status": "Active" if city_data["total_cases"] > 5 else "Learning"
        }
    
    def get_all_city_statistics(self) -> List[Dict[str, Any]]:
        """Get statistics for all cities"""
        return [self.get_city_statistics(city) for city in self.reward_weights.keys()]
    
    def adjust_confidence_score(
        self, 
        base_confidence: float, 
        city: str,
        rules_applied: List[str]
    ) -> Tuple[float, str]:
        """
        Adjust the RL agent's base confidence score using city-specific feedback.
        
        Args:
            base_confidence: Raw confidence from RL agent (0-1)
            city: City context
            rules_applied: List of rule IDs used
            
        Returns:
            (adjusted_confidence, explanation)
        """
        if city not in self.reward_weights:
            return base_confidence, "No feedback data for this city yet"
        
        city_stats = self.get_city_statistics(city)
        approval_rate = city_stats["approval_rate"]
        multiplier = city_stats["confidence_multiplier"]
        
        # Apply adjustment
        adjusted_confidence = min(1.0, base_confidence * multiplier)
        
        # Generate explanation
        if multiplier > 1.0:
            explanation = (
                f"Confidence boosted by {(multiplier-1)*100:.0f}% based on "
                f"{approval_rate:.0%} approval rate in {city} "
                f"({city_stats['total_cases']} cases analyzed)"
            )
        elif multiplier < 1.0:
            explanation = (
                f"Confidence reduced by {(1-multiplier)*100:.0f}% due to "
                f"{approval_rate:.0%} approval rate in {city} "
                f"({city_stats['total_cases']} cases analyzed)"
            )
        else:
            explanation = f"Standard confidence based on {approval_rate:.0%} approval rate"
        
        return adjusted_confidence, explanation
    
    def generate_feedback_report(self) -> Dict[str, Any]:
        """Generate comprehensive feedback system report"""
        all_cities = self.get_all_city_statistics()
        
        total_feedback = sum(city["total_cases"] for city in all_cities)
        total_positive = sum(city["positive_feedback"] for city in all_cities)
        
        return {
            "report_timestamp": datetime.utcnow().isoformat() + "Z",
            "total_feedback_count": total_feedback,
            "total_positive": total_positive,
            "overall_approval_rate": total_positive / max(1, total_feedback),
            "cities_tracked": len(all_cities),
            "city_breakdown": all_cities,
            "recent_feedback": self.feedback_history[-10:],  # Last 10 events
            "system_status": "Active" if total_feedback > 10 else "Warming Up"
        }
    
    def close(self):
        """Close database connection"""
        self.db.close()


def demonstrate_adaptive_feedback():
    """Demonstration of the adaptive feedback system"""
    print("="*80)
    print("ADAPTIVE FEEDBACK SYSTEM DEMONSTRATION")
    print("="*80)
    
    system = AdaptiveFeedbackSystem()
    
    # Simulate some feedback
    print("\n--- Simulating Positive Feedback (Mumbai) ---")
    result1 = system.process_feedback(
        case_id="mumbai_test_001",
        project_id="proj_demo_01",
        city="Mumbai",
        feedback_type="up",
        input_params={"plot_size": 2000, "location": "urban"},
        output_report={"rules_applied": ["MUM-FSI-001", "MUM-LOS-002"]}
    )
    
    for line in result1["audit_trail"]:
        print(f"  {line}")
    
    print("\n--- Simulating Negative Feedback (Pune) ---")
    result2 = system.process_feedback(
        case_id="pune_test_001",
        project_id="proj_demo_02",
        city="Pune",
        feedback_type="down",
        input_params={"plot_size": 1500, "location": "suburban"},
        output_report={"rules_applied": ["PUNE-SETBACK-001"]}
    )
    
    for line in result2["audit_trail"]:
        print(f"  {line}")
    
    print("\n--- City Statistics ---")
    for city_stat in system.get_all_city_statistics():
        print(f"\n{city_stat['city']}:")
        print(f"  Cases: {city_stat['total_cases']}")
        print(f"  Approval Rate: {city_stat['approval_rate']:.1%}")
        print(f"  Action Weights: {city_stat['action_weights']}")
        print(f"  Confidence Multiplier: {city_stat['confidence_multiplier']:.2f}")
    
    print("\n--- Confidence Adjustment Demo ---")
    base_conf = 0.85
    adjusted_conf, explanation = system.adjust_confidence_score(
        base_confidence=base_conf,
        city="Mumbai",
        rules_applied=["MUM-FSI-001"]
    )
    print(f"Base Confidence: {base_conf:.2f}")
    print(f"Adjusted Confidence: {adjusted_conf:.2f}")
    print(f"Explanation: {explanation}")
    
    print("\n--- Full Feedback Report ---")
    report = system.generate_feedback_report()
    print(json.dumps(report, indent=2))
    
    system.close()
    print("\n✓ Demonstration complete!")


if __name__ == "__main__":
    demonstrate_adaptive_feedback()
