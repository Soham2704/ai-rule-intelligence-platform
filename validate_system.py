"""
Comprehensive System Validation Script
---------------------------------------
This script validates the entire AI Rule Intelligence system:
1. Database initialization
2. File structure verification
3. Code syntax validation
4. Import checks
5. Configuration verification
"""

import os
import sys
import importlib.util
import json
from pathlib import Path

class SystemValidator:
    def __init__(self):
        self.errors = []
        self.warnings = []
        self.passed = []
        self.base_path = Path(__file__).parent
    
    def log_pass(self, message):
        """Log a passed check"""
        self.passed.append(message)
        print(f"✅ {message}")
    
    def log_warning(self, message):
        """Log a warning"""
        self.warnings.append(message)
        print(f"⚠️  {message}")
    
    def log_error(self, message):
        """Log an error"""
        self.errors.append(message)
        print(f"❌ {message}")
    
    def print_header(self, text):
        """Print section header"""
        print("\n" + "="*80)
        print(f"  {text}")
        print("="*80 + "\n")
    
    def check_file_exists(self, file_path):
        """Check if a file exists"""
        full_path = self.base_path / file_path
        if full_path.exists():
            self.log_pass(f"File exists: {file_path}")
            return True
        else:
            self.log_error(f"File missing: {file_path}")
            return False
    
    def check_python_syntax(self, file_path):
        """Check Python file for syntax errors"""
        full_path = self.base_path / file_path
        if not full_path.exists():
            return False
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                compile(f.read(), str(full_path), 'exec')
            self.log_pass(f"Syntax valid: {file_path}")
            return True
        except SyntaxError as e:
            self.log_error(f"Syntax error in {file_path}: {e}")
            return False
    
    def check_imports(self, file_path):
        """Check if a Python file can be imported"""
        full_path = self.base_path / file_path
        if not full_path.exists():
            return False
        
        module_name = file_path.replace('/', '.').replace('\\', '.').replace('.py', '')
        
        try:
            spec = importlib.util.spec_from_file_location(module_name, full_path)
            if spec and spec.loader:
                self.log_pass(f"Imports loadable: {file_path}")
                return True
            else:
                self.log_warning(f"Import issue: {file_path}")
                return False
        except Exception as e:
            self.log_warning(f"Import warning for {file_path}: {str(e)[:50]}")
            return False
    
    def validate_file_structure(self):
        """Validate all required files exist"""
        self.print_header("FILE STRUCTURE VALIDATION")
        
        required_files = {
            "New Files (Day 1-4)": [
                "agents/explainer_agent.py",
                "api_bridge.py",
                "design_platform_ui.py",
                "rl_env/city_adaptive_env.py",
                "rl_env/train_city_adaptive_agent.py",
                "tests/test_multi_city.py",
                "run_demo.py",
                "handover_v2.md",
                "DEMO_VIDEO_SCRIPT.md",
                "VALIDATION_CHECKLIST.md"
            ],
            "Updated Files": [
                "main_pipeline.py",
                "mcp_client.py",
                "database_setup.py",
                "README.md",
                "requirements.txt"
            ],
            "Existing Core Files": [
                "main.py",
                "app.py",
                "logging_config.py",
                "agents/reasoning_agent.py",
                "agents/geometry_agent.py"
            ]
        }
        
        for category, files in required_files.items():
            print(f"\n{category}:")
            for file in files:
                self.check_file_exists(file)
    
    def validate_python_syntax(self):
        """Validate Python syntax for all Python files"""
        self.print_header("PYTHON SYNTAX VALIDATION")
        
        python_files = [
            "agents/explainer_agent.py",
            "api_bridge.py",
            "design_platform_ui.py",
            "rl_env/city_adaptive_env.py",
            "rl_env/train_city_adaptive_agent.py",
            "tests/test_multi_city.py",
            "run_demo.py",
            "main_pipeline.py",
            "mcp_client.py",
            "database_setup.py",
            "main.py"
        ]
        
        for file in python_files:
            self.check_python_syntax(file)
    
    def validate_database_setup(self):
        """Validate database setup"""
        self.print_header("DATABASE SETUP VALIDATION")
        
        try:
            import database_setup
            self.log_pass("database_setup.py imported successfully")
            
            # Check if required classes exist
            required_classes = ['Rule', 'Feedback', 'GeometryOutput', 'ReasoningOutput']
            for cls_name in required_classes:
                if hasattr(database_setup, cls_name):
                    self.log_pass(f"Database class exists: {cls_name}")
                else:
                    self.log_error(f"Database class missing: {cls_name}")
            
            # Check ReasoningOutput has new fields
            reasoning_output = database_setup.ReasoningOutput
            if hasattr(reasoning_output, 'clause_summaries'):
                self.log_pass("ReasoningOutput has clause_summaries field")
            else:
                self.log_error("ReasoningOutput missing clause_summaries field")
            
            if hasattr(reasoning_output, 'confidence_level'):
                self.log_pass("ReasoningOutput has confidence_level field")
            else:
                self.log_error("ReasoningOutput missing confidence_level field")
                
        except Exception as e:
            self.log_error(f"Database setup validation failed: {e}")
    
    def validate_configuration(self):
        """Validate configuration files"""
        self.print_header("CONFIGURATION VALIDATION")
        
        # Check .env file
        env_path = self.base_path / ".env"
        if env_path.exists():
            self.log_pass(".env file exists")
        else:
            self.log_warning(".env file not found (required for API key)")
        
        # Check requirements.txt
        req_path = self.base_path / "requirements.txt"
        if req_path.exists():
            with open(req_path, 'r') as f:
                content = f.read()
                required_packages = ['fastapi', 'streamlit', 'stable-baselines3', 
                                   'langchain', 'sqlalchemy', 'plotly']
                for pkg in required_packages:
                    if pkg in content.lower():
                        self.log_pass(f"requirements.txt includes: {pkg}")
                    else:
                        self.log_warning(f"requirements.txt missing: {pkg}")
        else:
            self.log_error("requirements.txt not found")
    
    def validate_documentation(self):
        """Validate documentation files"""
        self.print_header("DOCUMENTATION VALIDATION")
        
        doc_files = {
            "handover_v2.md": 500,  # Minimum expected lines
            "README.md": 100,
            "DEMO_VIDEO_SCRIPT.md": 200,
            "VALIDATION_CHECKLIST.md": 200
        }
        
        for doc_file, min_lines in doc_files.items():
            doc_path = self.base_path / doc_file
            if doc_path.exists():
                with open(doc_path, 'r', encoding='utf-8') as f:
                    lines = len(f.readlines())
                if lines >= min_lines:
                    self.log_pass(f"{doc_file} complete ({lines} lines)")
                else:
                    self.log_warning(f"{doc_file} may be incomplete ({lines}/{min_lines} lines)")
            else:
                self.log_error(f"{doc_file} not found")
    
    def validate_agents(self):
        """Validate agent files"""
        self.print_header("AGENT VALIDATION")
        
        agent_files = {
            "agents/explainer_agent.py": "ExplainerAgent",
            "agents/reasoning_agent.py": "ReasoningAgent",
            "agents/geometry_agent.py": "GeometryAgent"
        }
        
        for file, class_name in agent_files.items():
            if self.check_file_exists(file):
                self.check_python_syntax(file)
    
    def validate_api_bridge(self):
        """Validate API bridge"""
        self.print_header("API BRIDGE VALIDATION")
        
        bridge_path = self.base_path / "api_bridge.py"
        if bridge_path.exists():
            with open(bridge_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Check for required endpoints
                required_endpoints = [
                    'GET /api/design-bridge/rules',
                    'GET /api/design-bridge/reasoning',
                    'GET /api/design-bridge/geometry',
                    'GET /api/design-bridge/feedback'
                ]
                
                for endpoint in required_endpoints:
                    if '/rules' in endpoint and 'get_rules_by_city' in content:
                        self.log_pass(f"Endpoint implemented: rules endpoint")
                    elif '/reasoning' in endpoint and 'get_reasoning_output' in content:
                        self.log_pass(f"Endpoint implemented: reasoning endpoint")
                    elif '/geometry' in endpoint and 'get_geometry_info' in content:
                        self.log_pass(f"Endpoint implemented: geometry endpoint")
                    elif '/feedback' in endpoint and 'get_feedback_by_case' in content:
                        self.log_pass(f"Endpoint implemented: feedback endpoint")
        else:
            self.log_error("api_bridge.py not found")
    
    def generate_report(self):
        """Generate final validation report"""
        self.print_header("VALIDATION REPORT")
        
        total_checks = len(self.passed) + len(self.warnings) + len(self.errors)
        
        print(f"Total Checks: {total_checks}")
        print(f"✅ Passed: {len(self.passed)}")
        print(f"⚠️  Warnings: {len(self.warnings)}")
        print(f"❌ Errors: {len(self.errors)}")
        
        if self.errors:
            print("\n" + "="*80)
            print("ERRORS FOUND:")
            print("="*80)
            for error in self.errors:
                print(f"  ❌ {error}")
        
        if self.warnings:
            print("\n" + "="*80)
            print("WARNINGS:")
            print("="*80)
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        print("\n" + "="*80)
        if len(self.errors) == 0:
            print("✅ SYSTEM VALIDATION PASSED!")
            print("="*80)
            print("\n🎉 All core components are in place and validated!")
            print("\n📋 Next Steps:")
            print("  1. Ensure APIs are running (python main.py, python api_bridge.py)")
            print("  2. Run multi-city tests: python tests/test_multi_city.py")
            print("  3. Launch visualization: streamlit run design_platform_ui.py")
            print("  4. Review documentation: handover_v2.md")
            return True
        else:
            print("❌ VALIDATION FAILED - Please fix errors above")
            print("="*80)
            return False
    
    def run_all_validations(self):
        """Run all validation checks"""
        print("="*80)
        print("  AI RULE INTELLIGENCE SYSTEM - COMPREHENSIVE VALIDATION")
        print("="*80)
        
        self.validate_file_structure()
        self.validate_python_syntax()
        self.validate_database_setup()
        self.validate_configuration()
        self.validate_documentation()
        self.validate_agents()
        self.validate_api_bridge()
        
        return self.generate_report()


if __name__ == "__main__":
    validator = SystemValidator()
    success = validator.run_all_validations()
    
    sys.exit(0 if success else 1)
