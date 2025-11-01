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
        all_matching_rules = []
        
        # Query for rules matching road width
        if "road_width" in parameters:
            width = parameters["road_width"]
            width_rules = self.db.query(Rule).filter(
                Rule.city.ilike(city),
                Rule.conditions['road_width_m']['min'].as_float() <= width,
                Rule.conditions['road_width_m']['max'].as_float() > width
            ).all()
            all_matching_rules.extend(width_rules)

        # Query for rules matching plot size
        if "plot_size" in parameters:
            area = parameters["plot_size"]
            area_rules = self.db.query(Rule).filter(
                Rule.city.ilike(city),
                Rule.conditions['plot_area_sqm']['min'].as_float() <= area,
                Rule.conditions['plot_area_sqm']['max'].as_float() >= area
            ).all()
            all_matching_rules.extend(area_rules)
            
        # Query for rules matching location
        if "location" in parameters:
            loc = parameters["location"]
            loc_rules = self.db.query(Rule).filter(
                Rule.city.ilike(city),
                Rule.conditions['location'].as_string().contains(f'"{loc}"')
            ).all()
            all_matching_rules.extend(loc_rules)

        # De-duplicate the final list to ensure each rule is returned only once
        return list({rule.id: rule for rule in all_matching_rules}.values())

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
            existing.stl_path = geometry_data.get("stl_path")
            existing.timestamp = datetime.utcnow().isoformat() + "Z"
        else:
            new_geometry = GeometryOutput(id=str(uuid.uuid4()), **geometry_data)
            self.db.add(new_geometry)
        self.db.commit()

    def add_reasoning_output(self, report_data: Dict[str, Any]):
        """Saves or updates the final AI reasoning report in the DB with enhanced fields."""
        existing = self.db.query(ReasoningOutput).filter(ReasoningOutput.case_id == report_data.get("case_id")).first()
        if existing:
            existing.rules_applied = report_data.get("rules_applied")
            existing.reasoning_summary = report_data.get("reasoning")
            existing.clause_summaries = report_data.get("clause_summaries", [])
            existing.confidence_score = report_data.get("confidence_score")
            existing.confidence_level = report_data.get("confidence_level", "Unknown")
            existing.confidence_note = report_data.get("confidence_note", "")
            existing.timestamp = datetime.utcnow().isoformat() + "Z"
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

