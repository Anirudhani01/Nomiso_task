# 🤖 AI Test Case Generator

An intelligent AI-powered system that automatically generates comprehensive test cases from user stories by analyzing project codebases and extracting domain knowledge.

## 🎯 Overview

The AI Test Case Generator is a sophisticated tool that combines multiple AI models (OpenAI GPT, Google Gemini, Ollama) to analyze user stories and generate detailed, actionable test cases. It automatically extracts knowledge from your project's source code to create contextually relevant test scenarios.

## ✨ Key Features

- **🧠 Multi-Model AI Support**: Fallback system using OpenAI GPT-4, Google Gemini, and Ollama
- **📊 Intelligent Analysis**: Extracts business logic, dependencies, and validation rules from code
- **🎯 Context-Aware Generation**: Creates domain-specific test cases based on actual project functionality
- **📋 Comprehensive Coverage**: Generates Happy Path, Negative, and Edge case scenarios
- **📁 Organized Output**: Timestamped results with detailed Markdown reports
- **🔄 Knowledge Base Integration**: Automatically builds knowledge base from backend and source code

## 🏗️ Architecture

```
AI_Agent/
├── main.py                          # Main orchestrator
├── user_story_analyser/             # User story analysis module
│   └── user_story_analyser.py
├── test_case_generator/             # Test case generation module
│   └── test_case.py
├── knowledge_base/                  # Domain knowledge extraction
│   ├── generate_knowledge_base.py
│   └── knowledge_base.json
├── prompts/                         # AI prompt templates
│   ├── test_case_generation_prompt.txt
│   └── unit_test_prompt.txt
└── test_results/                    # Generated test case outputs
    └── results_YYYYMMDD_HHMMSS/
```

## 🚀 Quick Start

### Prerequisites

```bash
pip install openai google-generativeai python-dotenv
```

### Environment Setup

Create a `.env` file in the AI_Agent directory with your API keys:

```env
# Optional: Use any combination of these
OPENAI_API_KEY=your_openai_api_key_here
GOOGLE_API_KEY=your_google_api_key_here
```

### Running the Generator

```bash
cd AI_Agent
python main.py
```

**Input**: Enter your user story when prompted  
**Output**: Generated test cases saved in `test_results/results_YYYYMMDD_HHMMSS/test_cases.md`

## 🔄 How It Works

### 1. **User Story Analysis**
- Analyzes user intent and requirements
- Extracts key functional needs
- Summarizes main goals in 2-3 sentences

### 2. **Knowledge Base Generation**
- Automatically scans `backend/` and `src/` directories
- Extracts business logic, models, and API endpoints
- Builds comprehensive domain knowledge base
- Identifies security features, validation rules, and dependencies

### 3. **Test Case Generation**
- Uses extracted knowledge to create contextually relevant test cases
- Generates exactly 6-8 comprehensive test scenarios
- Covers Happy Path, Negative, and Edge cases
- Adapts to specific technology stack and business domain

### 4. **Output Generation**
- Creates detailed Markdown reports
- Includes test case tables and detailed scenarios
- Timestamps all results for tracking

## 📊 Example Output

```markdown
# Test Cases Generated

**Total Test Cases:** 7

| Test Case ID | Test Scenario | Type | Status |
|--------------|---------------|------|--------|
| TC001 | Admin successfully updates the get history feature | Happy | Pending |
| TC002 | Admin attempts update without authentication | Negative | Pending |
| TC003 | Admin tries update with invalid data | Negative | Pending |
| TC004 | Admin verifies data integrity after update | Happy | Pending |
| TC005 | Admin attempts update with missing fields | Negative | Pending |
| TC006 | Admin checks response time performance | Edge | Pending |
| TC007 | Admin verifies system stability after update | Edge | Pending |
```

### Sample Detailed Test Case

```markdown
## TC001: Admin successfully updates the get history feature

**Test Type:** Happy Path  
**Priority:** High  
**Estimated Time:** 10 minutes

### Pre-conditions
- Admin user is authenticated and logged in
- System is in stable state
- Required permissions are granted

### Test Steps
1. Navigate to admin dashboard
2. Access the get history feature settings
3. Modify the feature configuration
4. Submit the changes
5. Verify the update was successful

### Expected Results
- Feature updates are saved successfully
- System maintains stability
- Changes are reflected in the application
- No errors or warnings are displayed

### Post-conditions
- Get history feature operates with new configuration
- System remains in stable state
- Audit logs capture the change
```

## 🎛️ Configuration

### AI Model Priority
The system uses a fallback mechanism:
1. **OpenAI GPT-4o-mini** (if API key provided)
2. **Google Gemini 1.5 Flash** (if API key provided)  
3. **Ollama Phi3:mini** (local fallback)

### Knowledge Base Sources
- `backend/` - Main application code
- `src/` - Source code examples and templates
- Automatically extracts:
  - API endpoints and routes
  - Data models and schemas
  - Authentication mechanisms
  - Validation rules
  - Business logic functions

## 📁 Output Structure

```
test_results/
└── results_20250830_161754/
    └── test_cases.md
        ├── User Story Analysis
        ├── Test Cases Summary Table
        └── Detailed Test Case Descriptions
```

## 🔍 Supported Domains

The system automatically adapts to various domains by analyzing your codebase:

- **E-commerce**: User registration, product management, authentication
- **Employee Management**: HR systems, employee data, admin functions
- **API Services**: REST endpoints, authentication, data validation
- **Web Applications**: User interfaces, form validation, business logic

## 🛠️ Customization

### Adding New Prompts
Edit `prompts/test_case_generation_prompt.txt` to customize:
- Test case structure
- Coverage requirements
- Domain-specific instructions

### Extending Knowledge Base
Modify `knowledge_base/generate_knowledge_base.py` to:
- Add new file types to analyze
- Extract additional metadata
- Include custom business rules

## 📈 Benefits

- **⚡ Speed**: Generate comprehensive test cases in seconds
- **🎯 Accuracy**: Context-aware based on actual project code
- **📋 Completeness**: Covers all test case types automatically
- **🔄 Consistency**: Standardized format and structure
- **🧠 Knowledge**: Builds reusable domain knowledge base
- **🤖 AI-Powered**: Leverages multiple AI models for best results

## 🔧 Troubleshooting

### Common Issues

**No API Keys**: System falls back to Ollama (requires local installation)
```bash
# Install Ollama locally
curl -fsSL https://ollama.ai/install.sh | sh
ollama pull phi3:mini
```

**Empty Results**: Check that `backend/` or `src/` directories contain analyzable code

**Generation Errors**: Verify prompt templates and knowledge base format

### Debug Mode
Add debug prints in individual modules to trace execution flow:

```python
# In main.py
print(f"Knowledge base generated: {len(knowledge_base)} entries")
print(f"Using AI model: {selected_model}")
```

## 📋 Requirements

- Python 3.8+
- OpenAI API key (optional)
- Google AI API key (optional)
- Ollama (optional, for local fallback)

## 🚀 Getting Started

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd AI_Agent
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

4. **Run the generator**
   ```bash
   python main.py
   ```

5. **View results**
   - Check `test_results/` directory for generated test cases
   - Open the latest `test_cases.md` file for detailed results

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙋‍♂️ Support

For questions or issues:
- Create an issue in the GitHub repository
- Check the troubleshooting section above
- Review the generated knowledge base for context

---

