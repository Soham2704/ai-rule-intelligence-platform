from typing import Optional

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
import json

# This is the "brain" of our new agent. It's a master-level prompt
# designed for concise, factual explanation.
REASONING_PROMPT = """
You are a precise AI Rule Explainer. Your task is to analyze a list of structured, applicable rules and a user's query, and then generate a concise, single-string reasoning chain.

**Think step-by-step:**
1.  Review the `APPLICABLE_RULES` provided from the database.
2.  Review the `USER_QUERY` to understand the context.
3.  Synthesize a one or two-sentence summary that directly connects the user's parameters to the key entitlements found in the rules. For example: "For a {{plot_size}} sqm plot on a {{road_width}}m road, Clause {{clause_id}} allows a maximum FSI of {{fsi}}."
4.  Combine these individual summaries into a single, cohesive "reasoning" string.

**Rules:**
* Be concise, factual, and direct.
* The final output MUST be a single string, not a multi-part report.

**User Query:**
{user_query}

**Applicable Rules Found in Database:**
{applicable_rules}
"""

class ReasoningAgent:
    def __init__(self, llm: Optional[ChatGoogleGenerativeAI] = None):
        self.llm = llm
        if self.llm is not None:
            self.prompt = PromptTemplate.from_template(REASONING_PROMPT)
            self.chain = self.prompt | self.llm
        else:
            self.chain = None
        print("ReasoningAgent initialized.")

    def generate_reasoning(self, user_query: dict, applicable_rules: list) -> str:
        """
        Generates a human-readable reasoning chain from structured rule data.
        """
        if not applicable_rules:
            return "No specific rules were found in the database for the given parameters."

        # If LLM is not available, return a basic explanation
        if self.llm is None or self.chain is None:
            return self._generate_basic_reasoning(user_query, applicable_rules)

        try:
            # We pass the clean, factual data to the LLM
            response = self.chain.invoke({
                "user_query": json.dumps(user_query),
                "applicable_rules": json.dumps(applicable_rules)
            })
            
            # Handle different response types
            if hasattr(response, 'content'):
                return str(response.content).strip()
            elif isinstance(response, str):
                return response.strip()
            else:
                return str(response).strip()
        except Exception as e:
            print(f"!!! ERROR in ReasoningAgent: {e}")
            return f"An error occurred while generating the reasoning summary: {e}"

    def _generate_basic_reasoning(self, user_query: dict, applicable_rules: list) -> str:
        """
        Generates a basic reasoning explanation without LLM.
        """
        plot_size = user_query.get("plot_size", "N/A")
        road_width = user_query.get("road_width", "N/A")
        location = user_query.get("location", "N/A")
        
        if not applicable_rules:
            return "No specific rules were found in the database for the given parameters."
        
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
