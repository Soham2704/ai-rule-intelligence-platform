from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import json
from typing import List, Dict, Any

# Enhanced prompt for user-friendly, contextual explanations
EXPLAINER_PROMPT = """
You are an expert AI Rule Explainer for urban planning and building regulations.
Your task is to provide CLEAR, CONTEXTUAL, and USER-FRIENDLY explanations.

**Critical Requirements:**
1. Explain in simple, conversational language
2. Start with the big picture, then provide specifics
3. Include ALL key numbers and calculations
4. Reference specific clauses with their purpose
5. Use professional formatting with clear structure

**Input Data:**
User Parameters: {user_query}
Applicable Rules: {applicable_rules}

**Output Format Structure:**

📍 **PROJECT OVERVIEW**
Briefly describe the project type and scale in one sentence.

📋 **APPLICABLE REGULATIONS**
For each major rule:
- Clause reference and authority
- What it permits/requires
- Specific numerical values and calculations

✅ **KEY ENTITLEMENTS**
Summarize the main development rights:
- Total buildable area (with FSI calculation)
- Maximum height allowed
- Open space requirements
- Parking provisions
- Any special conditions

**Example Output:**

📍 **PROJECT OVERVIEW**
This proposal involves a 2,000 sqm urban residential plot located on a 20-meter-wide road, falling under standard DCPR 2034 regulations for medium-density development.

📋 **APPLICABLE REGULATIONS**

**Clause DCPR-12.3 (FSI Entitlement)**
Permits a base FSI of 2.4 for plots between 1,000-3,000 sqm on roads 18-24m wide.
Calculation: 2,000 sqm × 2.4 = 4,800 sqm total buildable area

**Clause DCPR-15.1 (Layout Open Space)**
Requires 15% of plot area as Layout Open Space (LOS) for plots exceeding 1,500 sqm.
Calculation: 2,000 sqm × 15% = 300 sqm mandatory open space

**Clause DCPR-18.2 (Setbacks)**
Front margin: 3.0m, Side margins: 1.5m each, Rear margin: 3.0m

✅ **KEY ENTITLEMENTS**
• Total Developable Area: 4,800 sqm (across multiple floors)
• Maximum Building Height: 24 meters (typically 7-8 floors)
• Open Space Provision: 300 sqm landscaped area required
• Parking: 1 space per 100 sqm built-up (48 spaces minimum)
• Ground Coverage: Maximum 40% (800 sqm footprint)

**Important:**
- Use emoji icons for section headers (📍 📋 ✅)
- Include calculations with actual numbers
- Explain the "why" behind each rule
- Make it actionable and easy to understand
- Format with line breaks and bullet points for clarity

Generate comprehensive, user-friendly explanation:
"""

CLAUSE_EXTRACTION_PROMPT = """
You are a precise rule parser. Extract structured clause information from the given rule data.

**Input:** {rule_data}

**Task:** For each rule, identify:
1. Clause number/reference
2. Main entitlement type (FSI, setback, height, etc.)
3. Specific value or range
4. Conditions that trigger this clause

**Output Format (JSON):**
{{
    "clause_id": "DCPR_12.3",
    "entitlement_type": "FSI",
    "value": 3.0,
    "conditions": ["plot_size > 1000", "road_width 15-20m"],
    "summary": "Maximum FSI of 3.0 for plots over 1000 sqm on 15-20m roads"
}}

Generate structured clause data:
"""

class ExplainerAgent:
    """
    Advanced AI Rule Explainer Agent that provides human-readable summaries
    of building compliance rules with detailed reasoning chains.
    """
    
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.explainer_prompt = PromptTemplate.from_template(EXPLAINER_PROMPT)
        self.clause_prompt = PromptTemplate.from_template(CLAUSE_EXTRACTION_PROMPT)
        self.explainer_chain = self.explainer_prompt | self.llm
        self.clause_chain = self.clause_prompt | self.llm
        print("✓ ExplainerAgent initialized with advanced reasoning capabilities.")

    def extract_clause_summaries(self, rules: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Extracts structured clause information from raw rule data.
        
        Args:
            rules: List of rule dictionaries from MCP
            
        Returns:
            List of structured clause summaries
        """
        clause_summaries = []
        
        for rule in rules:
            try:
                # Create a concise summary for each rule
                clause_summary = {
                    "clause_id": rule.get("id", "Unknown"),
                    "authority": rule.get("authority", ""),
                    "clause_no": rule.get("clause_no", ""),
                    "entitlements": rule.get("entitlements", {}),
                    "conditions": rule.get("conditions", {}),
                    "notes": rule.get("notes", "")
                }
                
                # Extract key entitlement values
                entitlements = rule.get("entitlements", {})
                summary_parts = []
                
                if "total_fsi" in entitlements:
                    summary_parts.append(f"FSI: {entitlements['total_fsi']}")
                if "max_height_m" in entitlements:
                    summary_parts.append(f"Height: {entitlements['max_height_m']}m")
                if "ground_coverage_percent" in entitlements:
                    summary_parts.append(f"Coverage: {entitlements['ground_coverage_percent']}%")
                
                clause_summary["quick_summary"] = ", ".join(summary_parts) if summary_parts else "See entitlements"
                clause_summaries.append(clause_summary)
                
            except Exception as e:
                print(f"⚠ Warning: Could not extract clause summary for rule: {e}")
                continue
        
        return clause_summaries

    def generate_detailed_explanation(
        self, 
        user_query: Dict[str, Any], 
        applicable_rules: List[Dict[str, Any]]
    ) -> str:
        """
        Generates a comprehensive, human-readable explanation of why specific rules apply.
        
        Args:
            user_query: Dictionary with plot_size, location, road_width, etc.
            applicable_rules: List of rules that matched from MCP
            
        Returns:
            Human-readable reasoning string with clause references and explanations
        """
        if not applicable_rules:
            return (
                f"No specific compliance rules found for {user_query.get('plot_size', 'N/A')} sqm "
                f"{user_query.get('location', 'N/A')} plot on {user_query.get('road_width', 'N/A')}m road. "
                f"Please verify parameters or consult local development control regulations."
            )

        try:
            # Use LLM to generate comprehensive explanation
            response = self.explainer_chain.invoke({
                "user_query": json.dumps(user_query, indent=2),
                "applicable_rules": json.dumps(applicable_rules, indent=2)
            })
            
            explanation = response.content.strip()
            
            # Add metadata footer
            explanation += f"\n\n[Total rules applied: {len(applicable_rules)}]"
            
            return explanation
            
        except Exception as e:
            print(f"❌ ERROR in ExplainerAgent.generate_detailed_explanation: {e}")
            # Fallback to basic explanation
            return self._generate_fallback_explanation(user_query, applicable_rules)

    def _generate_fallback_explanation(
        self, 
        user_query: Dict[str, Any], 
        applicable_rules: List[Dict[str, Any]]
    ) -> str:
        """
        Generates a concise explanation without LLM if the main method fails.
        """
        plot_size = user_query.get("plot_size", "N/A")
        road_width = user_query.get("road_width", "N/A")
        location = user_query.get("location", "N/A")
        
        if not applicable_rules:
            return f"No specific rules found for {plot_size} sqm {location} plot on {road_width}m road."
        
        # Generate concise summary
        summary_parts = []
        
        for rule in applicable_rules[:2]:  # Limit to first 2 rules
            rule_id = rule.get("id", "Unknown")
            entitlements = rule.get("entitlements", {})
            
            if "total_fsi" in entitlements:
                fsi = entitlements["total_fsi"]
                buildable = int(plot_size) * fsi if isinstance(plot_size, (int, float)) else "N/A"
                summary_parts.append(f"{rule_id} allows FSI {fsi} ({buildable} sqm buildable)")
            elif "ground_coverage_percent" in entitlements:
                coverage = entitlements["ground_coverage_percent"]
                summary_parts.append(f"{rule_id} permits {coverage}% ground coverage")
        
        if summary_parts:
            return f"For {plot_size} sqm {location} plot on {road_width}m road: {', '.join(summary_parts)}."
        else:
            return f"Rules {', '.join([r.get('id', 'Unknown') for r in applicable_rules[:2]])} apply to {plot_size} sqm {location} plot."

    def generate_reasoning_with_confidence_context(
        self,
        user_query: Dict[str, Any],
        applicable_rules: List[Dict[str, Any]],
        confidence_score: float
    ) -> Dict[str, Any]:
        """
        Generates reasoning with additional confidence context for better decision transparency.
        
        Args:
            user_query: User's project parameters
            applicable_rules: Matched rules from MCP
            confidence_score: RL agent confidence (0-1)
            
        Returns:
            Dictionary with reasoning, clause summaries, and confidence interpretation
        """
        # Generate main explanation
        reasoning = self.generate_detailed_explanation(user_query, applicable_rules)
        
        # Extract structured clause summaries
        clause_summaries = self.extract_clause_summaries(applicable_rules)
        
        # Interpret confidence score
        if confidence_score >= 0.85:
            confidence_level = "High"
            confidence_note = "The RL agent is highly confident in this recommendation."
        elif confidence_score >= 0.65:
            confidence_level = "Moderate"
            confidence_note = "The RL agent has moderate confidence. Review recommended."
        else:
            confidence_level = "Low"
            confidence_note = "The RL agent has low confidence. Manual verification strongly recommended."
        
        return {
            "reasoning": reasoning,
            "clause_summaries": clause_summaries,
            "confidence_score": round(confidence_score, 3),
            "confidence_level": confidence_level,
            "confidence_note": confidence_note,
            "rules_applied": [rule.get("id") for rule in applicable_rules]
        }


if __name__ == "__main__":
    # Test the explainer agent
    print("Testing ExplainerAgent...")
    
    from langchain_google_genai import ChatGoogleGenerativeAI
    from dotenv import load_dotenv
    import os
    
    load_dotenv()
    os.environ["GOOGLE_API_KEY"] = os.getenv("GEMINI_API_KEY")
    
    llm = ChatGoogleGenerativeAI(model="gemini-pro-latest")
    explainer = ExplainerAgent(llm)
    
    # Mock data
    test_query = {
        "plot_size": 1200,
        "road_width": 18,
        "location": "urban"
    }
    
    test_rules = [
        {
            "id": "DCPR_12.3",
            "authority": "DCPR 2034",
            "clause_no": "12.3",
            "entitlements": {"total_fsi": 3.0, "max_height_m": 24, "ground_coverage_percent": 40},
            "conditions": {"plot_area_sqm": {"min": 1000, "max": 2000}, "road_width_m": {"min": 15, "max": 20}},
            "notes": "Enhanced FSI for urban development zones"
        }
    ]
    
    result = explainer.generate_reasoning_with_confidence_context(test_query, test_rules, 0.88)
    print("\n" + "="*80)
    print("EXPLAINER OUTPUT:")
    print("="*80)
    print(json.dumps(result, indent=2))
    print("\n✓ ExplainerAgent test complete!")
