from database_setup import SessionLocal, Rule
import os

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

# Comprehensive Pune rules based on PMRDA Development Control Regulations
COMPREHENSIVE_PUNE_RULES = [
    # FSI Rules for Pune
    {
        "id": "PUNE-FSI-URBAN-R20-UP", 
        "city": "Pune", 
        "rule_type": "FSI",
        "conditions": {
            "location": ["urban"], 
            "road_width_m": {"min": 20},
            "plot_area_sqm": {"min": 1000}
        },
        "entitlements": {
            "base_fsi": 1.5, 
            "premium_fsi": 0.5, 
            "total_fsi": 2.0,
            "ground_coverage_percent": 50,
            "max_height_m": 65
        },
        "notes": "FSI for urban plots over 1000 sqm on roads 20m+. Base FSI 1.5, Premium 0.5",
        "authority": "PMRDA",
        "clause_no": "PMRDA-DCR-25.1",
        "page": "45"
    },
    {
        "id": "PUNE-FSI-URBAN-R15-20",
        "city": "Pune",
        "rule_type": "FSI",
        "conditions": {
            "location": ["urban"],
            "road_width_m": {"min": 15, "max": 20},
            "plot_area_sqm": {"min": 500}
        },
        "entitlements": {
            "base_fsi": 1.2,
            "premium_fsi": 0.3,
            "total_fsi": 1.5,
            "ground_coverage_percent": 45,
            "max_height_m": 45
        },
        "notes": "FSI for urban plots 500+ sqm on 15-20m roads",
        "authority": "PMRDA",
        "clause_no": "PMRDA-DCR-25.2",
        "page": "45"
    },
    {
        "id": "PUNE-FSI-SUBURBAN-R18-UP",
        "city": "Pune",
        "rule_type": "FSI",
        "conditions": {
            "location": ["suburban"],
            "road_width_m": {"min": 18},
            "plot_area_sqm": {"min": 1000}
        },
        "entitlements": {
            "base_fsi": 1.0,
            "premium_fsi": 0.5,
            "total_fsi": 1.5,
            "ground_coverage_percent": 40,
            "max_height_m": 35
        },
        "notes": "FSI for suburban plots 1000+ sqm on roads 18m+",
        "authority": "PMRDA",
        "clause_no": "PMRDA-DCR-25.3",
        "page": "46"
    },
    {
        "id": "PUNE-FSI-CAT-A",
        "city": "Pune",
        "rule_type": "FSI",
        "conditions": {
            "location": ["urban"],
            "plot_area_sqm": {"min": 300, "max": 1000}
        },
        "entitlements": {
            "base_fsi": 1.0,
            "total_fsi": 1.0,
            "ground_coverage_percent": 50,
            "max_height_m": 27
        },
        "notes": "Category A plots (300-1000 sqm) in urban areas",
        "authority": "PMRDA",
        "clause_no": "PMRDA-DCR-26.1",
        "page": "47"
    },
    {
        "id": "PUNE-FSI-HIGH-DENSITY",
        "city": "Pune",
        "rule_type": "FSI",
        "conditions": {
            "location": ["urban"],
            "road_width_m": {"min": 30},
            "plot_area_sqm": {"min": 2000}
        },
        "entitlements": {
            "base_fsi": 2.0,
            "premium_fsi": 1.0,
            "total_fsi": 3.0,
            "ground_coverage_percent": 60,
            "max_height_m": 100
        },
        "notes": "High density development on wide roads (30m+) for large plots",
        "authority": "PMRDA",
        "clause_no": "PMRDA-DCR-27.1",
        "page": "48"
    },
    
    # Setback Rules for Pune
    {
        "id": "PUNE-SETBACK-R20-UP",
        "city": "Pune",
        "rule_type": "Setback",
        "conditions": {
            "road_width_m": {"min": 20},
            "plot_area_sqm": {"min": 1000}
        },
        "entitlements": {
            "front_margin_m": 6.0,
            "side_margin_m": 3.0,
            "rear_margin_m": 3.0
        },
        "notes": "Setbacks for plots 1000+ sqm on roads 20m+",
        "authority": "PMRDA",
        "clause_no": "PMRDA-DCR-30(A)",
        "page": "52"
    },
    {
        "id": "PUNE-SETBACK-R15-20",
        "city": "Pune",
        "rule_type": "Setback",
        "conditions": {
            "road_width_m": {"min": 15, "max": 20},
            "plot_area_sqm": {"min": 500}
        },
        "entitlements": {
            "front_margin_m": 4.5,
            "side_margin_m": 2.0,
            "rear_margin_m": 2.0
        },
        "notes": "Setbacks for plots 500+ sqm on 15-20m roads",
        "authority": "PMRDA",
        "clause_no": "PMRDA-DCR-30(B)",
        "page": "52"
    },
    {
        "id": "PUNE-SETBACK-CORNER",
        "city": "Pune",
        "rule_type": "Setback",
        "conditions": {
            "plot_corner": True,
            "road_width_m": {"min": 12}
        },
        "entitlements": {
            "front_margin_m": 4.0,
            "side_margin_m": 3.0,
            "rear_margin_m": 2.0
        },
        "notes": "Increased setbacks for corner plots",
        "authority": "PMRDA",
        "clause_no": "PMRDA-DCR-31.1",
        "page": "53"
    },
    
    # Height Rules for Pune
    {
        "id": "PUNE-HEIGHT-R25-UP",
        "city": "Pune",
        "rule_type": "BuildingHeight",
        "conditions": {
            "road_width_m": {"min": 25}
        },
        "entitlements": {
            "max_height_m": 65.0,
            "max_floors": 20
        },
        "notes": "Maximum height for plots on roads 25m+",
        "authority": "PMRDA",
        "clause_no": "PMRDA-DCR-35.1",
        "page": "58"
    },
    {
        "id": "PUNE-HEIGHT-R18-25",
        "city": "Pune",
        "rule_type": "BuildingHeight",
        "conditions": {
            "road_width_m": {"min": 18, "max": 25}
        },
        "entitlements": {
            "max_height_m": 45.0,
            "max_floors": 15
        },
        "notes": "Maximum height for plots on 18-25m roads",
        "authority": "PMRDA",
        "clause_no": "PMRDA-DCR-35.2",
        "page": "58"
    },
    {
        "id": "PUNE-HEIGHT-SPECIAL-ECO",
        "city": "Pune",
        "rule_type": "BuildingHeight",
        "conditions": {
            "special_zone": "eco_sensitive"
        },
        "entitlements": {
            "max_height_m": 15.0,
            "max_floors": 3
        },
        "notes": "Height restrictions in eco-sensitive zones",
        "authority": "PMRDA",
        "clause_no": "PMRDA-DCR-36.1",
        "page": "59"
    }
]

# Comprehensive Ahmedabad rules based on Ahmedabad Development Plan & Regulations
COMPREHENSIVE_AHMEDABAD_RULES = [
    # FSI Rules for Ahmedabad
    {
        "id": "AMD-FSI-URBAN-R20-UP", 
        "city": "Ahmedabad", 
        "rule_type": "FSI",
        "conditions": {
            "location": ["urban"], 
            "road_width_m": {"min": 20},
            "plot_area_sqm": {"min": 1000}
        },
        "entitlements": {
            "base_fsi": 1.8, 
            "premium_fsi": 0.7, 
            "total_fsi": 2.5,
            "ground_coverage_percent": 55,
            "max_height_m": 75
        },
        "notes": "FSI for urban plots over 1000 sqm on roads 20m+. Base FSI 1.8, Premium 0.7",
        "authority": "Ahmedabad Municipal Corporation",
        "clause_no": "ADP-22.1",
        "page": "38"
    },
    {
        "id": "AMD-FSI-URBAN-R15-20",
        "city": "Ahmedabad",
        "rule_type": "FSI",
        "conditions": {
            "location": ["urban"],
            "road_width_m": {"min": 15, "max": 20},
            "plot_area_sqm": {"min": 500}
        },
        "entitlements": {
            "base_fsi": 1.5,
            "premium_fsi": 0.5,
            "total_fsi": 2.0,
            "ground_coverage_percent": 50,
            "max_height_m": 50
        },
        "notes": "FSI for urban plots 500+ sqm on 15-20m roads",
        "authority": "Ahmedabad Municipal Corporation",
        "clause_no": "ADP-22.2",
        "page": "38"
    },
    {
        "id": "AMD-FSI-SUBURBAN-R18-UP",
        "city": "Ahmedabad",
        "rule_type": "FSI",
        "conditions": {
            "location": ["suburban"],
            "road_width_m": {"min": 18},
            "plot_area_sqm": {"min": 1000}
        },
        "entitlements": {
            "base_fsi": 1.2,
            "premium_fsi": 0.5,
            "total_fsi": 1.7,
            "ground_coverage_percent": 45,
            "max_height_m": 40
        },
        "notes": "FSI for suburban plots 1000+ sqm on roads 18m+",
        "authority": "Ahmedabad Municipal Corporation",
        "clause_no": "ADP-22.3",
        "page": "39"
    },
    {
        "id": "AMD-FSI-CAT-B",
        "city": "Ahmedabad",
        "rule_type": "FSI",
        "conditions": {
            "location": ["urban"],
            "plot_area_sqm": {"min": 200, "max": 1000}
        },
        "entitlements": {
            "base_fsi": 1.2,
            "total_fsi": 1.2,
            "ground_coverage_percent": 50,
            "max_height_m": 30
        },
        "notes": "Category B plots (200-1000 sqm) in urban areas",
        "authority": "Ahmedabad Municipal Corporation",
        "clause_no": "ADP-23.1",
        "page": "40"
    },
    {
        "id": "AMD-FSI-HERITAGE-ZONE",
        "city": "Ahmedabad",
        "rule_type": "FSI",
        "conditions": {
            "heritage_zone": True,
            "plot_area_sqm": {"min": 300}
        },
        "entitlements": {
            "base_fsi": 0.75,
            "total_fsi": 0.75,
            "ground_coverage_percent": 35,
            "max_height_m": 15
        },
        "notes": "Reduced FSI in heritage zones to preserve character",
        "authority": "Ahmedabad Municipal Corporation",
        "clause_no": "ADP-24.1",
        "page": "41"
    },
    
    # Setback Rules for Ahmedabad
    {
        "id": "AMD-SETBACK-R20-UP",
        "city": "Ahmedabad",
        "rule_type": "Setback",
        "conditions": {
            "road_width_m": {"min": 20},
            "plot_area_sqm": {"min": 1000}
        },
        "entitlements": {
            "front_margin_m": 7.0,
            "side_margin_m": 3.5,
            "rear_margin_m": 3.5
        },
        "notes": "Setbacks for plots 1000+ sqm on roads 20m+",
        "authority": "Ahmedabad Municipal Corporation",
        "clause_no": "ADP-28(A)",
        "page": "45"
    },
    {
        "id": "AMD-SETBACK-R15-20",
        "city": "Ahmedabad",
        "rule_type": "Setback",
        "conditions": {
            "road_width_m": {"min": 15, "max": 20},
            "plot_area_sqm": {"min": 500}
        },
        "entitlements": {
            "front_margin_m": 5.0,
            "side_margin_m": 2.5,
            "rear_margin_m": 2.5
        },
        "notes": "Setbacks for plots 500+ sqm on 15-20m roads",
        "authority": "Ahmedabad Municipal Corporation",
        "clause_no": "ADP-28(B)",
        "page": "45"
    },
    {
        "id": "AMD-SETBACK-HERITAGE",
        "city": "Ahmedabad",
        "rule_type": "Setback",
        "conditions": {
            "heritage_zone": True
        },
        "entitlements": {
            "front_margin_m": 6.0,
            "side_margin_m": 4.0,
            "rear_margin_m": 4.0
        },
        "notes": "Increased setbacks in heritage zones",
        "authority": "Ahmedabad Municipal Corporation",
        "clause_no": "ADP-29.1",
        "page": "46"
    },
    
    # Height Rules for Ahmedabad
    {
        "id": "AMD-HEIGHT-R30-UP",
        "city": "Ahmedabad",
        "rule_type": "BuildingHeight",
        "conditions": {
            "road_width_m": {"min": 30}
        },
        "entitlements": {
            "max_height_m": 75.0,
            "max_floors": 22
        },
        "notes": "Maximum height for plots on roads 30m+",
        "authority": "Ahmedabad Municipal Corporation",
        "clause_no": "ADP-32.1",
        "page": "50"
    },
    {
        "id": "AMD-HEIGHT-R20-30",
        "city": "Ahmedabad",
        "rule_type": "BuildingHeight",
        "conditions": {
            "road_width_m": {"min": 20, "max": 30}
        },
        "entitlements": {
            "max_height_m": 50.0,
            "max_floors": 15
        },
        "notes": "Maximum height for plots on 20-30m roads",
        "authority": "Ahmedabad Municipal Corporation",
        "clause_no": "ADP-32.2",
        "page": "50"
    },
    {
        "id": "AMD-HEIGHT-HERITAGE",
        "city": "Ahmedabad",
        "rule_type": "BuildingHeight",
        "conditions": {
            "heritage_zone": True
        },
        "entitlements": {
            "max_height_m": 12.0,
            "max_floors": 3
        },
        "notes": "Height restrictions in heritage zones",
        "authority": "Ahmedabad Municipal Corporation",
        "clause_no": "ADP-33.1",
        "page": "51"
    },
    
    # Parking Requirements for Ahmedabad
    {
        "id": "AMD-PARKING-COMMERCIAL",
        "city": "Ahmedabad",
        "rule_type": "Parking",
        "conditions": {
            "building_use": ["commercial"],
            "plot_area_sqm": {"min": 500}
        },
        "entitlements": {
            "ecs_per_100sqm": 2,
            "visitor_parking_percent": 25,
            "parking_area_per_ecs_sqm": 25
        },
        "notes": "2 ECS per 100 sqm built-up area + 25% visitor parking for commercial",
        "authority": "Ahmedabad Municipal Corporation",
        "clause_no": "ADP-37.1",
        "page": "55"
    }
]

def populate_comprehensive_rules():
    """
    Populate database with comprehensive rules for Mumbai, Pune, and Ahmedabad
    """
    print("=" * 60)
    print("POPULATING COMPREHENSIVE RULES FOR ALL CITIES")
    print("=" * 60)
    
    # Combine all rules
    ALL_RULES = COMPREHENSIVE_MUMBAI_RULES + COMPREHENSIVE_PUNE_RULES + COMPREHENSIVE_AHMEDABAD_RULES
    
    # Print current working directory and database path
    from database_setup import DB_PATH
    print(f"Current working directory: {os.getcwd()}")
    print(f"Database path: {DB_PATH}")
    print(f"Database file exists: {os.path.exists(DB_PATH)}")
    
    db = SessionLocal()
    try:
        rules_added = 0
        rules_updated = 0
        
        for rule_data in ALL_RULES:
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
        print(f"  Total rules processed: {len(ALL_RULES)}")
        print("=" * 60)
        
        # Verify total rules in database by city
        mumbai_count = db.query(Rule).filter(Rule.city == "Mumbai").count()
        pune_count = db.query(Rule).filter(Rule.city == "Pune").count()
        ahmedabad_count = db.query(Rule).filter(Rule.city == "Ahmedabad").count()
        
        print(f"\nRules by city:")
        print(f"  Mumbai: {mumbai_count}")
        print(f"  Pune: {pune_count}")
        print(f"  Ahmedabad: {ahmedabad_count}")
        print(f"  Total: {mumbai_count + pune_count + ahmedabad_count}")
        
        # Print some sample rules for verification
        for city in ["Mumbai", "Pune", "Ahmedabad"]:
            print(f"\nSample {city} rules in database:")
            sample_rules = db.query(Rule).filter(Rule.city == city).limit(2).all()
            for rule in sample_rules:
                print(f"  - {rule.id}: {rule.rule_type}")
                print(f"    Conditions: {rule.conditions}")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    populate_comprehensive_rules()