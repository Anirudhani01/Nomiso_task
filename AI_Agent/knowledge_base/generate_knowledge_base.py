import os
import ast
import json
import re
from typing import Dict, List, Any

def analyze_business_logic(name: str, docstring: str, node: ast.AST, source_lines: List[str]) -> Dict[str, Any]:
    """Analyze business logic, dependencies, and test-relevant details."""
    
    # Enhanced business case analysis
    business_case = docstring.strip().split("\n")[0] if docstring else ""
    
    if not business_case:
        if "register" in name.lower():
            business_case = "User registration endpoint - creates new user accounts with validation"
        elif "login" in name.lower():
            business_case = "User authentication endpoint - validates credentials and issues JWT tokens"
        elif "add_product" in name.lower() or "create_product" in name.lower():
            business_case = "Product creation endpoint - adds new products with seller authentication"
        elif "get_product" in name.lower():
            business_case = "Product retrieval endpoint - fetches product information by ID"
        elif "get_products" in name.lower():
            business_case = "Product listing endpoint - retrieves all available products"
        elif "verify_password" in name.lower():
            business_case = "Password verification utility - compares plain text with hashed passwords"
        elif "get_password_hash" in name.lower():
            business_case = "Password hashing utility - creates secure password hashes using bcrypt"
        elif "create_access_token" in name.lower():
            business_case = "JWT token generation - creates time-limited access tokens for authentication"
        elif "verify_token" in name.lower():
            business_case = "JWT token validation - verifies and decodes authentication tokens"
        elif "User" in name:
            business_case = "User data model - represents user account information"
        elif "Product" in name:
            business_case = "Product data model - represents product catalog items"
        elif "Token" in name:
            business_case = "Authentication token model - represents JWT access tokens"
        else:
            business_case = "Core business logic component"
    
    # Extract dependencies and imports
    dependencies = []
    if hasattr(node, 'body'):
        for item in node.body:
            if isinstance(item, ast.Import):
                for alias in item.names:
                    dependencies.append(alias.name)
            elif isinstance(item, ast.ImportFrom):
                module = item.module if item.module else ""
                for alias in item.names:
                    dependencies.append(f"{module}.{alias.name}")
    
    # Extract validation rules and business constraints
    validation_rules = []
    if "password" in name.lower():
        validation_rules.append("Password validation and hashing")
    if "email" in name.lower():
        validation_rules.append("Email format validation")
    if "username" in name.lower():
        validation_rules.append("Username uniqueness validation")
    if "price" in name.lower():
        validation_rules.append("Price validation (must be positive number)")
    if "token" in name.lower():
        validation_rules.append("JWT token validation and expiration")
    
    # Extract error handling patterns
    error_handling = []
    if hasattr(node, 'body'):
        for item in node.body:
            if isinstance(item, ast.Raise):
                if hasattr(item.exc, 'value') and hasattr(item.exc.value, 'id'):
                    error_handling.append(f"Raises {item.exc.value.id}")
                elif hasattr(item.exc, 'func') and hasattr(item.exc.func, 'id'):
                    error_handling.append(f"Raises {item.exc.func.id}")
    
    # Extract test-relevant details
    test_details = {
        "input_validation": [],
        "authentication_required": False,
        "database_operations": [],
        "external_dependencies": [],
        "error_scenarios": []
    }
    
    if "verify_token" in name.lower() or "Depends" in str(node):
        test_details["authentication_required"] = True
        test_details["error_scenarios"].extend([
            "Invalid token format",
            "Expired token",
            "Missing authorization header"
        ])
    
    if "register" in name.lower():
        test_details["input_validation"].extend([
            "Username uniqueness check",
            "Email format validation",
            "Password strength requirements"
        ])
        test_details["error_scenarios"].extend([
            "Duplicate username",
            "Duplicate email",
            "Invalid input format"
        ])
    
    if "login" in name.lower():
        test_details["input_validation"].extend([
            "Username existence check",
            "Password verification"
        ])
        test_details["error_scenarios"].extend([
            "Invalid credentials",
            "User not found"
        ])
    
    if "product" in name.lower():
        test_details["input_validation"].extend([
            "Product name validation",
            "Price validation",
            "Category validation"
        ])
        test_details["error_scenarios"].extend([
            "Invalid product data",
            "Unauthorized access"
        ])
    
    return {
        "business_case": business_case,
        "dependencies": dependencies,
        "validation_rules": validation_rules,
        "error_handling": error_handling,
        "test_details": test_details
    }

def extract_field_info(class_node: ast.ClassDef) -> List[Dict[str, Any]]:
    """Extract detailed field information from Pydantic models."""
    fields = []
    
    for item in class_node.body:
        if isinstance(item, ast.AnnAssign) and hasattr(item, 'target') and hasattr(item, 'annotation'):
            field_name = item.target.id if hasattr(item.target, 'id') else str(item.target)
            field_type = ast.unparse(item.annotation) if hasattr(ast, 'unparse') else str(item.annotation)
            
            # Analyze field constraints and validation
            field_info = {
                "name": field_name,
                "type": field_type,
                "validation_rules": [],
                "business_constraints": []
            }
            
            if "password" in field_name.lower():
                field_info["validation_rules"].append("Secure password storage")
                field_info["business_constraints"].append("Password should be hashed before storage")
            
            if "email" in field_name.lower():
                field_info["validation_rules"].append("Email format validation")
                field_info["business_constraints"].append("Email must be unique across users")
            
            if "username" in field_name.lower():
                field_info["validation_rules"].append("Username uniqueness")
                field_info["business_constraints"].append("Username must be unique across users")
            
            if "price" in field_name.lower():
                field_info["validation_rules"].append("Positive number validation")
                field_info["business_constraints"].append("Price must be greater than zero")
            
            if "id" in field_name.lower():
                field_info["validation_rules"].append("UUID format validation")
                field_info["business_constraints"].append("Auto-generated unique identifier")
            
            fields.append(field_info)
    
    return fields

def parse_python_file(file_path: str) -> Dict[str, Any]:
    """Parse Python file and extract comprehensive information."""
    with open(file_path, "r", encoding="utf-8") as f:
        source = f.read()
    
    source_lines = source.split('\n')
    tree = ast.parse(source)
    
    file_info = {
        "filename": os.path.basename(file_path),
        "file_path": file_path,
        "business_overview": "E-commerce backend API with user authentication and product management",
        "architecture": "FastAPI-based REST API with JWT authentication",
        "security_features": [
            "JWT token-based authentication",
            "Password hashing with bcrypt",
            "Protected endpoints requiring authentication"
        ],
        "classes": [],
        "functions": [],
        "endpoints": [],
        "data_models": [],
        "business_logic": []
    }
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            # Enhanced class analysis
            class_analysis = analyze_business_logic(node.name, ast.get_docstring(node), node, source_lines)
            fields = extract_field_info(node)
            
            class_info = {
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "business_case": class_analysis["business_case"],
                "fields": fields,
                "dependencies": class_analysis["dependencies"],
                "validation_rules": class_analysis["validation_rules"],
                "test_details": class_analysis["test_details"]
            }
            
            file_info["classes"].append(class_info)
            
            # Categorize as data model
            if any(keyword in node.name for keyword in ["User", "Product", "Token"]):
                file_info["data_models"].append(class_info)
        
        elif isinstance(node, ast.FunctionDef):
            # Enhanced function analysis
            func_analysis = analyze_business_logic(node.name, ast.get_docstring(node), node, source_lines)
            
            # Check if it's an endpoint
            is_endpoint = False
            endpoint_info = {}
            
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Call) and hasattr(decorator.func, 'value') and hasattr(decorator.func.value, 'id'):
                    if decorator.func.value.id == 'app':
                        is_endpoint = True
                        endpoint_info = {
                            "method": decorator.func.attr,
                            "path": "",
                            "response_model": "",
                            "status_code": ""
                        }
                        
                        # Extract path from decorator arguments
                        for arg in decorator.args:
                            if isinstance(arg, ast.Constant):
                                endpoint_info["path"] = arg.value
                        
                        # Extract response model and status code from decorator keywords
                        for keyword in decorator.keywords:
                            if keyword.arg == "response_model":
                                endpoint_info["response_model"] = keyword.value.id if hasattr(keyword.value, 'id') else str(keyword.value)
                            elif keyword.arg == "status_code":
                                endpoint_info["status_code"] = keyword.value.value if hasattr(keyword.value, 'value') else str(keyword.value)
            
            func_info = {
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "business_case": func_analysis["business_case"],
                "parameters": [a.arg for a in node.args.args],
                "return": "Unknown",
                "dependencies": func_analysis["dependencies"],
                "validation_rules": func_analysis["validation_rules"],
                "error_handling": func_analysis["error_handling"],
                "test_details": func_analysis["test_details"],
                "is_endpoint": is_endpoint
            }
            
            if is_endpoint:
                func_info.update(endpoint_info)
                file_info["endpoints"].append(func_info)
            else:
                file_info["functions"].append(func_info)
                file_info["business_logic"].append(func_info)
    
    return file_info

def generate_knowledge_base(source_folder: str, output_file: str = "knowledge_base.json"):
    """Generate comprehensive knowledge base from source code."""
    knowledge_base = []
    
    for root, _, files in os.walk(source_folder):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                try:
                    parsed = parse_python_file(file_path)
                    knowledge_base.append(parsed)
                    print(f"✅ Parsed: {file}")
                except Exception as e:
                    print(f"❌ Error parsing {file}: {e}")
    
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(knowledge_base, f, indent=2)
    
    print(f"\n🎯 Knowledge base generated: {output_file}")
    print(f"📊 Total files processed: {len(knowledge_base)}")
    
    # Print summary
    for file_info in knowledge_base:
        print(f"\n📁 {file_info['filename']}:")
        print(f"   - Classes: {len(file_info['classes'])}")
        print(f"   - Functions: {len(file_info['functions'])}")
        print(f"   - Endpoints: {len(file_info['endpoints'])}")
        print(f"   - Data Models: {len(file_info['data_models'])}")

if __name__ == "__main__":
    # Use relative path from AI_Agent directory to src directory
    generate_knowledge_base("../src", "knowledge_base.json")
