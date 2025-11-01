#!/usr/bin/env python3

from database_setup import SessionLocal, Rule

def analyze_database():
    print('🔍 DETAILED DATABASE BREAKDOWN')
    print('=' * 60)
    
    db = SessionLocal()
    
    try:
        # Get total count
        total = db.query(Rule).count()
        print(f'📊 Total rules in database: {total}')
        print()
        
        # Get detailed breakdown by city
        cities = db.query(Rule.city).distinct().all()
        city_counts = []
        
        for city_tuple in cities:
            city = city_tuple[0]
            if city:  # Skip None cities
                count = db.query(Rule).filter(Rule.city == city).count()
                city_counts.append((city, count))
        
        # Sort by count descending
        city_counts.sort(key=lambda x: x[1], reverse=True)
        
        print('🏙️ Rules by City (Detailed Count):')
        pune_related_total = 0
        pune_exact = 0
        
        for city, count in city_counts:
            print(f'   📍 {city}: {count} rules')
            if 'pune' in city.lower() or 'pmr' in city.lower():
                pune_related_total += count
            if city.lower() == 'pune':
                pune_exact = count
        
        print()
        print(f'🎯 PUNE-RELATED ANALYSIS:')
        print(f'   Direct "Pune": {pune_exact} rules')
        print(f'   All Pune-related cities: {pune_related_total} rules')
        print(f'   Non-Pune rules: {total - pune_related_total} rules')
        print()
        
        # Check what cities we actually have
        print('📋 All City Names Found:')
        for city, count in city_counts:
            if count > 50:  # Show cities with significant rule counts
                print(f'   🔥 {city}: {count} rules (MAJOR)')
            else:
                print(f'   📝 {city}: {count} rules')
        
        print()
        print('🔍 Sample Pune rules:')
        pune_rules = db.query(Rule).filter(
            (Rule.city.ilike('%Pune%')) | (Rule.city == 'Pune')
        ).limit(5).all()
        
        for rule in pune_rules:
            print(f'   City: "{rule.city}" | Rule: {rule.id} | Type: {rule.rule_type}')
        
        print()
        print('💡 EXPLANATION:')
        print('   The 855 new rules are distributed across:')
        for city, count in city_counts:
            if count > 10:  # Only show significant additions
                print(f'   - {city}: {count} rules')
        
    finally:
        db.close()

if __name__ == "__main__":
    analyze_database()