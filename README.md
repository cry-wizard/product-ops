# AI Product Ops: Automated App Toolification Strategic Matrix

An automated research pipeline and data orchestration engine built to analyze, categorize, and verify integration readiness across 100 enterprise applications. This project replaces manual market research with an AI-driven agent workflow, delivering a production-ready data matrix and interactive HTML dashboard.

---

## 📊 Strategic High-Level Insights
* **Self-Serve Access:** **23%** of audited applications feature an open, instant sign-up path allowing engineering teams to generate developer tokens immediately without legal or sales bottlenecks.
* **P0 Quick-Wins:** **23%** of the ecosystem is perfectly primed for immediate agent deployment, combining self-serve setup, standard API formats (REST/GraphQL), and robust auth protocols (e.g., Salesforce, HubSpot, Zendesk).
* **Auth Standardization:** **18%** of the market relies strictly on standard **OAuth2**, facilitating secure token injection.

---

## 🛠️ Repository Structure

```text
composio-product-ops/
├── data/
│   ├── apps.json            # Final verified application dataset
│   └── raw_results.json     # Initial raw data extracted from Pass 1
├── output/
│   └── index.html           # Interactive HTML strategic dashboard
├── .gitignore               # Standard git exclusions (ignores .venv, .env)
├── generate_dashboard.py    # Generates the final UI analytics interface
├── requirements.txt         # Project dependencies
├── run_pipeline.py          # Primary data extraction engine (Pass 1)
└── verify_results.py        # Multi-pass LLM validation critic (Pass 2)

```

### Environment Setup
```text
pip install -r requirements.txt
```

## 🛠️ Environment Setup
GROQ_API_KEY=your_groq_key_here
GEMINI_API_KEY=your_gemini_key_here
COMPOSIO_API_KEY=your_composio_key_here

## Execution Flow
python run_pipeline.py      # Extract raw data
python verify_results.py    # Clean, validate, and verify records
python generate_dashboard.py # Re-render output/index.html dashboard