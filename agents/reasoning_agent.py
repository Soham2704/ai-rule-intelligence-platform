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
    def __init__(self, llm: ChatGoogleGenerativeAI):
        self.llm = llm
        self.prompt = PromptTemplate.from_template(REASONING_PROMPT)
        self.chain = self.prompt | self.llm
        print("ReasoningAgent initialized.")

    def generate_reasoning(self, user_query: dict, applicable_rules: list) -> str:
        """
        Generates a human-readable reasoning chain from structured rule data.
        """
        if not applicable_rules:
            return "No specific rules were found in the database for the given parameters."

        try:
            # We pass the clean, factual data to the LLM
            response = self.chain.invoke({
                "user_query": json.dumps(user_query),
                "applicable_rules": json.dumps(applicable_rules)
            })
            return response.content.strip()
        except Exception as e:
            print(f"!!! ERROR in ReasoningAgent: {e}")
            return f"An error occurred while generating the reasoning summary: {e}"

