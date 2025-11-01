from database_setup import SessionLocal, Rule

# --- 1. Define the "Golden Record" Rules ---
# This is the high-quality, manually curated knowledge base.
# It now includes the new metadata fields as per the final schema.
RULES_DATA = [
    # --- Mumbai Rules ---
    {
        "id": "MUM-FSI-SUBURBS-R18-27", "city": "Mumbai", "rule_type": "FSI",
        "conditions": {"location": ["urban", "suburban"], "road_width_m": {"min": 18, "max": 27}},
        "entitlements": {"base_fsi": 1.0, "premium_fsi": 0.5, "tdr_fsi": 0.9, "total_fsi": 2.4},
        "notes": "FSI for urban/suburban areas on 18m-27m roads.", "authority": "MCGM", "clause_no": "DCPR-30", "page": "84"
    },
    {
        "id": "MUM-LOS-1001-2500", "city": "Mumbai", "rule_type": "LayoutOpenSpace",
        "conditions": {"plot_area_sqm": {"min": 1001, "max": 2500}},
        "entitlements": {"los_percentage": 15, "min_area_sqm": 125, "min_dimension_m": 7.5},
        "notes": "LOS for plots between 1001 and 2500 sq.m.", "authority": "MCGM", "clause_no": "DCPR-15(b)", "page": "77"
    },
    # --- Pune Rules ---
    {
        "id": "PUNE-SETBACK-001", "city": "Pune", "rule_type": "Setback",
        "conditions": {"plot_area_sqm": {"min": 501, "max": 1000}, "road_width_m": {"min": 9, "max": 15}},
        "entitlements": {"front_margin_m": 3.0, "side_margin_m": 1.5, "rear_margin_m": 1.5},
        "notes": "Setbacks for plots 501-1000sqm on 9m-15m roads.", "authority": "PMRDA", "clause_no": "PMRDA-DCR-Table-6A", "page": "81"
    },
    # --- Ahmedabad Rules ---
    {
        "id": "AHM-HEIGHT-001", "city": "Ahmedabad", "rule_type": "BuildingHeight",
        "conditions": {"road_width_m": {"min": 12, "max": 18}},
        "entitlements": {"max_height_m": 25.0},
        "notes": "Max height for plots on 12m-18m roads.", "authority": "AUDA", "clause_no": "GDCR-2021-R1", "page": "N/A"
    }
]

# --- 2. Database Population Logic ---
def populate_database():
    """
    This function connects to the database and inserts the structured "golden record" rules.
    It's designed to be run once to set up the initial, high-quality knowledge base.
    """
    print("--- Connecting to DB to populate golden records... ---")
    db = SessionLocal()
    try:
        rules_added = 0
        for rule_data in RULES_DATA:
            # Check if the rule already exists to prevent duplicates
            existing_rule = db.query(Rule).filter(Rule.id == rule_data["id"]).first()
            if existing_rule:
                print(f"  - Rule '{rule_data['id']}' already exists. Skipping.")
                continue

            # Create a new Rule object from our dictionary
            new_rule = Rule(**rule_data)
            db.add(new_rule)
            rules_added += 1
            print(f"  - Staging new rule '{rule_data['id']}' for {rule_data['city']}.")
        
        if rules_added > 0:
            # Commit all the new rules to the database in a single transaction
            db.commit()
            print(f"--- Successfully committed {rules_added} new golden records. ---")
        else:
            print("--- All golden records already exist. ---")
    
    except Exception as e:
        print(f"!!! An error occurred: {e}")
        db.rollback() # If anything goes wrong, undo all changes for this session
    
    finally:
        db.close() # Always ensure the database connection is closed


if __name__ == "__main__":
    populate_database()

