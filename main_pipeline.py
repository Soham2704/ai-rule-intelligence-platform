import json
import os
import numpy as np
import re
from datetime import datetime
import torch

from logging_config import logger

# Import all our stateless agents
from agents.geometry_agent import GeometryAgent
from agents.reasoning_agent import ReasoningAgent
from agents.explainer_agent import ExplainerAgent  # NEW: Enhanced explainer
from agents.interior_agent import InteriorDesignAgent
from agents.calculator_agent import EntitlementsAgent, AllowableEnvelopeAgent
from adaptive_feedback_system import AdaptiveFeedbackSystem  # NEW: Adaptive feedback integration


def process_case_logic(case_data, system_state):
    """
    This is the final, definitive version of the core pipeline logic.
    It is fully refactored to use the MCPClient and all final agent designs.
    """
    # --- A. Unpack Inputs ---
    project_id = case_data.get("project_id", "default_project")
    case_id = case_data.get("case_id")
    city = case_data.get("city")
    parameters = case_data.get("parameters", {})
    logger.info(f"Processing case {case_id} for project {project_id}.")
    
    # --- B. Query MCP for Hard Facts ---
    logger.info(f"Querying MCP for rules for case {case_id}...")
    matching_rules = system_state.mcp_client.query_rules(city, parameters)
    deterministic_entitlements = [{"id": rule.id, "notes": rule.notes, **rule.entitlements} for rule in matching_rules] if matching_rules else []
    logger.info(f"MCP returned {len(matching_rules)} rules for {case_id}.")

    # --- C. AI Reasoning Layer (Enhanced with Explainer) ---
    # Use the new ExplainerAgent for detailed, clause-level reasoning
    explainer_agent = ExplainerAgent(llm=system_state.llm)
    
    # Keep backward compatibility with basic reasoning agent
    reasoning_agent = ReasoningAgent(llm=system_state.llm)
    basic_reasoning = reasoning_agent.generate_reasoning(
        user_query=parameters,
        applicable_rules=deterministic_entitlements
    )
    logger.info(f"Reasoning summary generated for {case_id}.")
    
    # --- D. Run RL Agent for Confidence Score ---
    location_map = {"urban": 0, "suburban": 1, "rural": 2}
    rl_state_np = np.array([parameters.get("plot_size",0), location_map.get(parameters.get("location", "urban"),0), parameters.get("road_width",0)]).astype(np.float32)
    
    action, _ = system_state.rl_agent.predict(rl_state_np, deterministic=True)
    rl_optimal_action = int(action)

    # Convert the numpy state to a torch Tensor to get the probability distribution
    rl_state_tensor = torch.as_tensor(rl_state_np, device=system_state.rl_agent.device).reshape(1, -1)
    distribution = system_state.rl_agent.policy.get_distribution(rl_state_tensor)
    action_probabilities = distribution.distribution.probs.detach().cpu().numpy()[0]
    base_confidence_score = float(action_probabilities[rl_optimal_action])
    logger.info(f"Base RL confidence for {case_id}: {base_confidence_score:.3f}")
    
    # --- D2. Apply City-Specific Confidence Adjustment (NEW: Adaptive Feedback Integration) ---
    try:
        adaptive_system = AdaptiveFeedbackSystem()
        adjusted_confidence, confidence_explanation = adaptive_system.adjust_confidence_score(
            base_confidence=base_confidence_score,
            city=city,
            rules_applied=[rule.id for rule in matching_rules]
        )
        adaptive_system.close()
        
        logger.info(f"Adjusted confidence for {case_id}: {adjusted_confidence:.3f} (was {base_confidence_score:.3f})")
        logger.info(f"Confidence adjustment: {confidence_explanation}")
        
        confidence_score = adjusted_confidence
    except Exception as e:
        logger.warning(f"Could not apply adaptive confidence adjustment: {e}")
        confidence_score = base_confidence_score
        confidence_explanation = "Base RL confidence (no city-specific adjustment available)"
    
    # --- E. Generate Enhanced Reasoning with Confidence Context ---
    enhanced_reasoning = explainer_agent.generate_reasoning_with_confidence_context(
        user_query=parameters,
        applicable_rules=deterministic_entitlements,
        confidence_score=confidence_score
    )
    
    # --- F. Compile the NEW, Standardized Final Report with Enhanced Reasoning ---
    final_report = { 
        "project_id": project_id,
        "case_id": case_id,
        "city": city,  # Include city for UI filtering
        "parameters": parameters,  # Include parameters for UI display
        "rules_applied": enhanced_reasoning["rules_applied"],
        "reasoning": enhanced_reasoning["reasoning"],  # Detailed explanation
        "clause_summaries": enhanced_reasoning["clause_summaries"],  # Structured clause data
        "confidence_score": enhanced_reasoning["confidence_score"],
        "confidence_level": enhanced_reasoning["confidence_level"],  # High/Moderate/Low
        "confidence_note": enhanced_reasoning["confidence_note"],  # Human-readable confidence interpretation
        "basic_reasoning": basic_reasoning  # Keep for backward compatibility
    }
    
    # --- G. Run Final Agents & Save All Outputs (for handover) ---
    output_dir = f"outputs/projects/{project_id}"
    os.makedirs(output_dir, exist_ok=True)
    json_output_path = os.path.join(output_dir, f"{case_id}_report.json")
    stl_output_path = os.path.join(output_dir, f"{case_id}_geometry.stl")

    with open(json_output_path, "w") as f:
        json.dump(final_report, f, indent=4)
    
    # Generate geometry based on FSI if available
    geometry_agent = GeometryAgent()
    total_fsi = 1.0 # Default
    if deterministic_entitlements:
        for ent in deterministic_entitlements:
            if 'total_fsi' in ent:
                fsi_value = ent['total_fsi']
                if isinstance(fsi_value, (int, float)): 
                    total_fsi = fsi_value
                    break
    height = total_fsi * 10 
    geometry_agent.create_block(output_path=stl_output_path, width=np.sqrt(max(0, parameters.get("plot_size", 100))), depth=np.sqrt(max(0, parameters.get("plot_size", 100))), height=height)
    
    # Save reasoning and geometry reference to the MCP
    system_state.mcp_client.add_reasoning_output(final_report)
    system_state.mcp_client.add_geometry_output({
        "case_id": case_id,
        "project_id": project_id,
        "stl_path": stl_output_path
    })
    
    logger.info(f"PIPELINE_COMPLETE for case: {case_id}", extra={'extra_data': {'final_report': final_report}})
    
    return final_report

    

