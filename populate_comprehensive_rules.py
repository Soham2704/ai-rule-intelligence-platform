from database_setup import SessionLocal, Rule

# Comprehensive Mumbai rules based on DCPR 2034
COMPREHENSIVE_MUMBAI_RULES = [
    # FSI Rules for different plot sizes and road widths
    {
        "id": "MUM-FSI-URBAN-R18-UP", 
        "city": "Mumbai", 
        "rule_type": "FSI",
        "conditions": {
            "location": ["urban"], 
            "road_width_m": {"min": 18},
            "plot_area_sqm": {"min": 1000}
        },
        "entitlements": {
            "base_fsi": 1.33, 
            "premium_fsi": 0.67, 
            "tdr_fsi": 1.0, 
            "total_fsi": 3.0,
            "ground_coverage_percent": 50,
            "max_height_m": 70
        },
        "notes": "FSI for urban plots over 1000 sqm on roads 18m+. Base FSI 1.33, Premium 0.67, TDR 1.0",
        "authority": "MCGM",
        "clause_no": "DCPR-30.1",
        "page": "84"
    },
    {
        "id": "MUM-FSI-URBAN-R12-18",
        "city": "Mumbai",
        "rule_type": "FSI",
        "conditions": {
            "location": ["urban"],
            "road_width_m": {"min": 12, "max": 18},
            "plot_area_sqm": {"min": 500}
        },
        "entitlements": {
            "base_fsi": 1.0,
            "premium_fsi": 0.5,
            "tdr_fsi": 0.9,
            "total_fsi": 2.4,
            "ground_coverage_percent": 45,
            "max_height_m": 50
        },
        "notes": "FSI for urban plots 500+ sqm on 12-18m roads",
        "authority": "MCGM",
        "clause_no": "DCPR-30.2",
        "page": "84"
    },
    {
        "id": "MUM-FSI-SUBURBAN-R18-UP",
        "city": "Mumbai",
        "rule_type": "FSI",
        "conditions": {
            "location": ["suburban"],
            "road_width_m": {"min": 18},
            "plot_area_sqm": {"min": 1000}
        },
        "entitlements": {
            "base_fsi": 1.0,
            "premium_fsi": 0.5,
            "tdr_fsi": 0.9,
            "total_fsi": 2.4,
            "ground_coverage_percent": 40,
            "max_height_m": 60
        },
        "notes": "FSI for suburban plots 1000+ sqm on roads 18m+",
        "authority": "MCGM",
        "clause_no": "DCPR-30.3",
        "page": "85"
    },
    
    # Layout Open Space (LOS) Rules
    {
        "id": "MUM-LOS-2001-PLUS",
        "city": "Mumbai",
        "rule_type": "LayoutOpenSpace",
        "conditions": {
            "plot_area_sqm": {"min": 2001}
        },
        "entitlements": {
            "los_percentage": 20,
            "min_area_sqm": 150,
            "min_dimension_m": 9.0
        },
        "notes": "20% LOS required for plots over 2000 sqm, minimum 150 sqm with 9m dimension",
        "authority": "MCGM",
        "clause_no": "DCPR-15(c)",
        "page": "77"
    },
    {
        "id": "MUM-LOS-1501-2000",
        "city": "Mumbai",
        "rule_type": "LayoutOpenSpace",
        "conditions": {
            "plot_area_sqm": {"min": 1501, "max": 2000}
        },
        "entitlements": {
            "los_percentage": 18,
            "min_area_sqm": 135,
            "min_dimension_m": 8.0
        },
        "notes": "18% LOS for plots 1501-2000 sqm",
        "authority": "MCGM",
        "clause_no": "DCPR-15(b2)",
        "page": "77"
    },
    
    # Setback Rules
    {
        "id": "MUM-SETBACK-R18-UP",
        "city": "Mumbai",
        "rule_type": "Setback",
        "conditions": {
            "road_width_m": {"min": 18},
            "plot_area_sqm": {"min": 1000}
        },
        "entitlements": {
            "front_margin_m": 6.0,
            "side_margin_m": 3.0,
            "rear_margin_m": 3.0
        },
        "notes": "Setbacks for plots 1000+ sqm on roads 18m+",
        "authority": "MCGM",
        "clause_no": "DCPR-35(A)",
        "page": "92"
    },
    {
        "id": "MUM-SETBACK-R12-18",
        "city": "Mumbai",
        "rule_type": "Setback",
        "conditions": {
            "road_width_m": {"min": 12, "max": 18},
            "plot_area_sqm": {"min": 500}
        },
        "entitlements": {
            "front_margin_m": 4.5,
            "side_margin_m": 2.0,
            "rear_margin_m": 2.0
        },
        "notes": "Setbacks for plots 500+ sqm on 12-18m roads",
        "authority": "MCGM",
        "clause_no": "DCPR-35(B)",
        "page": "92"
    },
    
    # Height Rules
    {
        "id": "MUM-HEIGHT-R20-UP",
        "city": "Mumbai",
        "rule_type": "BuildingHeight",
        "conditions": {
            "road_width_m": {"min": 20}
        },
        "entitlements": {
            "max_height_m": 70.0,
            "max_floors": 20
        },
        "notes": "Maximum height for plots on roads 20m+",
        "authority": "MCGM",
        "clause_no": "DCPR-40.1",
        "page": "98"
    },
    {
        "id": "MUM-HEIGHT-R15-20",
        "city": "Mumbai",
        "rule_type": "BuildingHeight",
        "conditions": {
            "road_width_m": {"min": 15, "max": 20}
        },
        "entitlements": {
            "max_height_m": 50.0,
            "max_floors": 15
        },
        "notes": "Maximum height for plots on 15-20m roads",
        "authority": "MCGM",
        "clause_no": "DCPR-40.2",
        "page": "98"
    },
    
    # Parking Requirements
    {
        "id": "MUM-PARKING-RESIDENTIAL",
        "city": "Mumbai",
        "rule_type": "Parking",
        "conditions": {
            "building_use": ["residential"],
            "plot_area_sqm": {"min": 1000}
        },
        "entitlements": {
            "ecs_per_dwelling": 1,
            "visitor_parking_percent": 10,
            "parking_area_per_ecs_sqm": 23
        },
        "notes": "1 ECS per dwelling unit + 10% visitor parking",
        "authority": "MCGM",
        "clause_no": "DCPR-45.1",
        "page": "105"
    }
]

def populate_comprehensive_rules():
    """
    Populate database with comprehensive Mumbai rules
    """
    print("=" * 60)
    print("POPULATING COMPREHENSIVE MUMBAI RULES")
    print("=" * 60)
    
    db = SessionLocal()
    try:
        rules_added = 0
        rules_updated = 0
        
        for rule_data in COMPREHENSIVE_MUMBAI_RULES:
            existing_rule = db.query(Rule).filter(Rule.id == rule_data["id"]).first()
            
            if existing_rule:
                # Update existing rule
                for key, value in rule_data.items():
                    setattr(existing_rule, key, value)
                rules_updated += 1
                print(f"  ✓ Updated rule: {rule_data['id']}")
            else:
                # Add new rule
                new_rule = Rule(**rule_data)
                db.add(new_rule)
                rules_added += 1
                print(f"  + Added new rule: {rule_data['id']}")
        
        db.commit()
        
        print("=" * 60)
        print(f"SUMMARY:")
        print(f"  New rules added: {rules_added}")
        print(f"  Existing rules updated: {rules_updated}")
        print(f"  Total rules processed: {len(COMPREHENSIVE_MUMBAI_RULES)}")
        print("=" * 60)
        
        # Verify total rules in database
        total_rules = db.query(Rule).filter(Rule.city == "Mumbai").count()
        print(f"\nTotal Mumbai rules in database: {total_rules}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_comprehensive_rules()
