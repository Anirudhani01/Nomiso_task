import json
from pathlib import Path
import subprocess
import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

# --- LLM Clients ---
try:
    from openai import OpenAI
except ImportError:
    OpenAI = None

try:
    import google.generativeai as genai
except ImportError:
    genai = None

# --- Conditional Initialization ---
openai_client = None
if os.getenv("OPENAI_API_KEY") and OpenAI:
    openai_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

gemini_enabled = False
if os.getenv("GOOGLE_API_KEY") and genai:
    genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
    gemini_enabled = True

def extract_json_from_text(text: str) -> list:
    """Extract JSON array from text that might contain extra content."""
    # Try to find JSON array pattern
    json_pattern = r'\[.*?\]'
    matches = re.findall(json_pattern, text, re.DOTALL)
    
    for match in matches:
        try:
            parsed = json.loads(match)
            if isinstance(parsed, list) and len(parsed) > 0:
                return parsed
        except json.JSONDecodeError:
            continue
    
    # If no JSON found, try to parse the entire text
    try:
        parsed = json.loads(text)
        if isinstance(parsed, list):
            return parsed
    except json.JSONDecodeError:
        pass
    
    return []

def clean_and_validate_test_cases(test_cases: list) -> list:
    """Clean and validate test case data."""
    cleaned_cases = []
    
    for case in test_cases:
        if isinstance(case, dict):
            cleaned_case = {
                "scenario": str(case.get("scenario", "")).strip(),
                "steps": str(case.get("steps", "")).strip(),
                "expected": str(case.get("expected", "")).strip(),
                "type": str(case.get("type", "")).strip(),
                "status": "Pending"
            }
            
            # Validate required fields
            if (cleaned_case["scenario"] and 
                cleaned_case["steps"] and 
                cleaned_case["expected"] and 
                cleaned_case["type"]):
                cleaned_cases.append(cleaned_case)
    
    return cleaned_cases

# --- Helper: Call LLM dynamically ---
def call_llm(prompt: str, model_name: str = "phi3:mini") -> list:
    """
    Sends the prompt to LLM and returns structured test cases.
    Follows priority: OpenAI -> Gemini -> Ollama
    """
    
    # Try OpenAI first
    if openai_client:
        try:
            print("⚡ Using OpenAI GPT...")
            response = openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a Test Case Generator. Generate exactly 6-8 test cases in valid JSON format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )
            output_text = response.choices[0].message.content
            print(f"📝 OpenAI response length: {len(output_text)} characters")
            
            # Extract and parse JSON
            test_cases = extract_json_from_text(output_text)
            if test_cases:
                cleaned_cases = clean_and_validate_test_cases(test_cases)
                if cleaned_cases:
                    print(f"✅ OpenAI generated {len(cleaned_cases)} valid test cases")
                    return cleaned_cases
            
        except Exception as e:
            print(f"❌ OpenAI call failed: {e}")
    
    # Try Gemini second
    if gemini_enabled:
        try:
            print("⚡ Using Google Gemini...")
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(prompt)
            output_text = response.text
            print(f"📝 Gemini response length: {len(output_text)} characters")
            
            # Extract and parse JSON
            test_cases = extract_json_from_text(output_text)
            if test_cases:
                cleaned_cases = clean_and_validate_test_cases(test_cases)
                if cleaned_cases:
                    print(f"✅ Gemini generated {len(cleaned_cases)} valid test cases")
                    return cleaned_cases
                    
        except Exception as e:
            print(f"❌ Gemini call failed: {e}")
    
    # Fallback to Ollama
    try:
        print("⚡ Using Ollama (local model)...")
        process = subprocess.run(
            ["ollama", "run", model_name],
            input=prompt.encode("utf-8"),
            capture_output=True,
            text=True,
            timeout=60
        )
        output_text = process.stdout.strip()
        print(f"📝 Ollama response length: {len(output_text)} characters")
        
        # Extract and parse JSON
        test_cases = extract_json_from_text(output_text)
        if test_cases:
            cleaned_cases = clean_and_validate_test_cases(test_cases)
            if cleaned_cases:
                print(f"✅ Ollama generated {len(cleaned_cases)} valid test cases")
                return cleaned_cases
        
        # If JSON parsing fails, try text parsing
        test_cases = parse_text_output(output_text)
        if test_cases:
            print(f"✅ Ollama generated {len(test_cases)} test cases from text")
            return test_cases
            
    except subprocess.TimeoutExpired:
        print("❌ Ollama call timed out.")
    except Exception as e:
        print(f"❌ Ollama call failed: {e}")
    
    print("❌ All LLM calls failed. No test cases generated.")
    return []

# --- Helper: Parse plain text LLM output into list of dicts ---
def parse_text_output(text: str) -> list:
    """
    Converts plain text from LLM into structured test case dicts.
    Expects each test case separated by '---' with 4 lines: scenario, steps, expected, type
    """
    test_cases = []
    for block in text.split("---"):
        lines = [line.strip() for line in block.strip().split("\n") if line.strip()]
        if len(lines) >= 4:
            test_cases.append({
                "scenario": lines[0],
                "steps": lines[1],
                "expected": lines[2],
                "type": lines[3],
                "status": "Pending"
            })
    return test_cases

# --- Main Function: Generate Test Cases ---
def generate_test_cases(user_story: str, analysis: str, template_path: str, knowledge_base_path: str) -> list:
    """
    Main function that follows the intended flow:
    1. Load knowledge base
    2. Load prompt template
    3. Combine user story + analysis + knowledge base + prompts
    4. Send to LLM for test case generation
    5. Return structured test cases
    """
    
    # --- Load knowledge base (domain context) ---
    kb_content = ""
    kb_file = Path(knowledge_base_path)
    if kb_file.exists():
        try:
            with open(kb_file, "r", encoding="utf-8") as f:
                kb_json = json.load(f)
            kb_content = json.dumps(kb_json, indent=2)
            print(f"✅ Knowledge base loaded: {kb_file}")
        except Exception as e:
            print(f"❌ Error loading knowledge base: {e}")
            kb_content = "Domain knowledge is not available."
    else:
        print(f"⚠️ Knowledge base not found: {kb_file}")
        kb_content = "Domain knowledge is not available."

    # --- Load prompt template ---
    prompt_template = ""
    template_folder = Path(template_path)
    if template_folder.exists():
        # SPECIFICALLY LOAD test_case_generation_prompt.txt
        target_template = template_folder / "test_case_generation_prompt.txt"
        if target_template.exists():
            try:
                with open(target_template, "r", encoding="utf-8") as f:
                    prompt_template = f.read()
                print(f"✅ Target template loaded: {target_template}")
            except Exception as e:
                print(f"❌ Error loading target template: {e}")
                prompt_template = ""
        
        # Fallback if target template not found
        if not prompt_template:
            print(f"⚠️ Target template not found: {target_template}")
            template_files = list(template_folder.glob("*.txt"))
            if template_files:
                try:
                    with open(template_files[0], "r", encoding="utf-8") as f:
                        prompt_template = f.read()
                    print(f"⚠️ Fallback template loaded: {template_files[0]}")
                except Exception as e:
                    print(f"❌ Error loading fallback template: {e}")
                    prompt_template = "Generate multiple test cases (happy, negative, edge) in structured format."
            else:
                print("⚠️ No prompt template files found")
                prompt_template = "Generate multiple test cases (happy, negative, edge) in structured format."
    else:
        print(f"⚠️ Prompt template folder not found: {template_folder}")
        prompt_template = "Generate multiple test cases (happy, negative, edge) in structured format."

    # --- Combine everything into comprehensive LLM prompt ---
    llm_prompt = f"""
You are a Test Case Generator for Software Applications.

DOMAIN KNOWLEDGE (extracted from project code):
{kb_content}

USER STORY:
{user_story}

USER STORY ANALYSIS:
{analysis}

INSTRUCTIONS:
{prompt_template}

CRITICAL REQUIREMENTS:
- Generate EXACTLY 6-8 test cases (not 1, not 2, but 6-8)
- Each test case must be COMPLETE with all fields filled
- Cover different scenarios: Happy Path, Negative Cases, Edge Cases
- Make test cases SPECIFIC and ACTIONABLE
- Return ONLY valid JSON array format

OUTPUT FORMAT - Return this exact JSON structure:
[
  {{
    "scenario": "Clear description of what is being tested",
    "steps": "Step-by-step test execution instructions",
    "expected": "Expected result or outcome",
    "type": "Happy/Negative/Edge"
  }},
  {{
    "scenario": "Another test scenario",
    "steps": "Test steps for this scenario",
    "expected": "Expected result for this scenario",
    "type": "Happy/Negative/Edge"
  }}
]

Generate exactly 6-8 test cases now:
"""

    print("\n🚀 Sending comprehensive prompt to LLM...")
    print(f"📝 Prompt length: {len(llm_prompt)} characters")
    
    # --- Call LLM dynamically ---
    test_cases = call_llm(llm_prompt)

    # --- Final validation ---
    if test_cases:
        print(f"✅ Final result: {len(test_cases)} test cases generated")
        for i, tc in enumerate(test_cases, 1):
            print(f"   TC{i}: {tc.get('scenario', 'N/A')[:60]}...")
    else:
        print("❌ No test cases generated")
    
    return test_cases
