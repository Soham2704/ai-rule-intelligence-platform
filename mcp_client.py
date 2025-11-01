from database_setup import SessionLocal, Rule, Feedback, GeometryOutput, ReasoningOutput
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
import uuid

class MCPClient:
    """
    This is the final, feature-complete client for the Managed Compliance Platform.
    It is architected as a professional, stateful class that manages its own DB session.
    """
    def __init__(self):
        self.db: Session = SessionLocal()
        print("MCPClient (Final Handover Version) initialized.")

    def query_rules(self, city: str, parameters: dict) -> List[Rule]:
        """
        Finds all rules that match the given case parameters by aggregating results
        from multiple, independent queries.
        """
        print(f"Querying rules for city: {city} with parameters: {parameters}")
        
        # Get all rules for the city first
        city_rules = self.db.query(Rule).filter(Rule.city.ilike(city)).all()
        print(f"Found {len(city_rules)} total rules for city: {city}")
        
        all_matching_rules = []
        
        # Filter rules based on parameters
        for rule in city_rules:
            conditions = rule.conditions
            matches = True
            
            print(f"Checking rule {rule.id} with conditions: {conditions}")
            
            # Check road width
            if "road_width" in parameters and "road_width_m" in conditions:
                road_cond = conditions["road_width_m"]
                road_width = parameters["road_width"]
                
                # Handle different condition formats
                if isinstance(road_cond, dict):
                    min_width = road_cond.get("min", 0)
                    max_width = road_cond.get("max", float('inf'))
                    
                    if not (min_width <= road_width <= max_width):
                        matches = False
                        print(f"  Road width {road_width} not in range [{min_width}, {max_width}]")
                elif isinstance(road_cond, (int, float)):
                    # Simple equality check
                    if road_cond != road_width:
                        matches = False
                        print(f"  Road width {road_width} != {road_cond}")
            
            # Check plot size
            if "plot_size" in parameters and "plot_area_sqm" in conditions:
                plot_cond = conditions["plot_area_sqm"]
                plot_size = parameters["plot_size"]
                
                # Handle different condition formats
                if isinstance(plot_cond, dict):
                    min_area = plot_cond.get("min", 0)
                    max_area = plot_cond.get("max", float('inf'))
                    
                    if not (min_area <= plot_size <= max_area):
                        matches = False
                        print(f"  Plot size {plot_size} not in range [{min_area}, {max_area}]")
                elif isinstance(plot_cond, (int, float)):
                    # Simple equality check
                    if plot_cond != plot_size:
                        matches = False
                        print(f"  Plot size {plot_size} != {plot_cond}")
            
            # Check location
            if "location" in parameters and "location" in conditions:
                location_cond = conditions["location"]
                location = parameters["location"]
                
                # Handle different condition formats
                if isinstance(location_cond, list):
                    if location not in location_cond:
                        matches = False
                        print(f"  Location {location} not in {location_cond}")
                elif isinstance(location_cond, str):
                    if location != location_cond:
                        matches = False
                        print(f"  Location {location} != {location_cond}")
            
            # If all conditions match, add the rule
            if matches:
                print(f"  Rule {rule.id} matches!")
                all_matching_rules.append(rule)
            else:
                print(f"  Rule {rule.id} does not match")

        # De-duplicate the final list to ensure each rule is returned only once
        deduplicated = list({rule.id: rule for rule in all_matching_rules}.values())
        print(f"Returning {len(deduplicated)} matching rules: {[r.id for r in deduplicated]}")
        return deduplicated

    def add_feedback(self, feedback_data: Dict[str, Any]):
        """Saves a user feedback record directly to the 'feedback' table in the MCP."""
        new_feedback = Feedback(
            id=str(uuid.uuid4()),
            case_id=feedback_data.get("case_id"),
            project_id=feedback_data.get("project_id"),
            city=feedback_data.get("input_case", {}).get("city"),
            feedback_type=feedback_data.get("user_feedback"),
            timestamp=datetime.utcnow().isoformat() + "Z",
            full_input=feedback_data.get("input_case"),
            full_output=feedback_data.get("output_report")
        )
        self.db.add(new_feedback)
        self.db.commit()
        self.db.refresh(new_feedback)
        return new_feedback

    def add_geometry_output(self, geometry_data: Dict[str, Any]):
        """Saves or updates a reference to a generated geometry file in the DB."""
        existing = self.db.query(GeometryOutput).filter(GeometryOutput.case_id == geometry_data.get("case_id")).first()
        if existing:
            setattr(existing, 'stl_path', geometry_data.get("stl_path", existing.stl_path))
            setattr(existing, 'timestamp', datetime.utcnow().isoformat() + "Z")
        else:
            new_geometry = GeometryOutput(
                id=str(uuid.uuid4()),
                case_id=geometry_data.get("case_id"),
                project_id=geometry_data.get("project_id"),
                stl_path=geometry_data.get("stl_path"),
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            self.db.add(new_geometry)
        self.db.commit()

    def add_reasoning_output(self, report_data: Dict[str, Any]):
        """Saves or updates the final AI reasoning report in the DB with enhanced fields."""
        existing = self.db.query(ReasoningOutput).filter(ReasoningOutput.case_id == report_data.get("case_id")).first()
        if existing:
            setattr(existing, 'rules_applied', report_data.get("rules_applied", existing.rules_applied))
            setattr(existing, 'reasoning_summary', report_data.get("reasoning", existing.reasoning_summary))
            setattr(existing, 'clause_summaries', report_data.get("clause_summaries", existing.clause_summaries))
            setattr(existing, 'confidence_score', report_data.get("confidence_score", existing.confidence_score))
            setattr(existing, 'confidence_level', report_data.get("confidence_level", existing.confidence_level))
            setattr(existing, 'confidence_note', report_data.get("confidence_note", existing.confidence_note))
            setattr(existing, 'timestamp', datetime.utcnow().isoformat() + "Z")
        else:
            new_reasoning = ReasoningOutput(
                id=str(uuid.uuid4()),
                case_id=report_data.get("case_id"),
                project_id=report_data.get("project_id"),
                rules_applied=report_data.get("rules_applied"),
                reasoning_summary=report_data.get("reasoning"),
                clause_summaries=report_data.get("clause_summaries", []),
                confidence_score=report_data.get("confidence_score"),
                confidence_level=report_data.get("confidence_level", "Unknown"),
                confidence_note=report_data.get("confidence_note", ""),
                timestamp=datetime.utcnow().isoformat() + "Z"
            )
            self.db.add(new_reasoning)
        self.db.commit()

    def get_feedback_by_city(self, city: str) -> List[Feedback]:
        """Queries the MCP and returns all feedback records for a specific city."""
        return self.db.query(Feedback).filter(Feedback.city.ilike(city)).all()
        
    def close(self):
        """Closes the database session."""
        if self.db:
            self.db.close()
            print("MCPClient session closed.")