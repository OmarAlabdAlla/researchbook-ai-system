# ResearchBook

AI-powered academic research intelligence platform for researcher discovery and collaboration matching.

Developed for Chalmers University to enable intelligent exploration of academic data, expert discovery, and collaboration analysis across large-scale graph databases.

Built as an AI-powered system with LLM-based reasoning and structured workflows, approaching agent-like behaviour for complex query handling.

---

## Features

* **Person Lookup** – Search researcher profiles with fuzzy name matching (handles Swedish names, accents, variations)
* **Expert Finder** – Find experts on any topic with AI-powered ranking
* **Strategic Meeting Recommendations** – Identify collaboration opportunities using "hard" (direct) and "soft" (indirect) relationship types
* **Field Intelligence Brief** – Generate structured analysis of research areas and trends

---

## Architecture

```
┌─────────────────────────────────────────────┐
│         Streamlit Web Interface             │
└─────────────────┬───────────────────────────┘
                  │
┌─────────────────▼───────────────────────────┐
│         ResearchBookFinal                   │
│  ├── EnhancedNameMatcher (fuzzy matching)   │
│  ├── AIKeywordExtractor (LLM keywords)      │
│  └── Smart Query Handler (intent parsing)   │
└───────┬─────────────────────┬───────────────┘
        │                     │
┌───────▼───────┐     ┌───────▼───────┐
│   Neo4j DB1   │     │   Neo4j DB2   │
│  (Research)   │     │   (Thesis)    │
│  150K+ people │     │  58K+ roles   │
└───────────────┘     └───────────────┘
        │                     │
        └──────────┬──────────┘
                   │
           ┌───────▼───────┐
           │  LightLLM API │
           │ (Claude Model)│
           └───────────────┘
```

---

## Tech Stack

| Component     | Technology                |
| ------------- | ------------------------- |
| Backend       | Python 3.11               |
| Database      | Neo4j (Graph DB)          |
| AI/LLM        | Claude (via LightLLM API) |
| Frontend      | Streamlit                 |
| Visualization | Plotly                    |

---

## Why This Project Matters

This project demonstrates how LLMs can be combined with structured graph data to build intelligent systems that go beyond simple retrieval.

It highlights:

* Integration of LLM reasoning with real-world data systems (Neo4j)
* Handling of complex queries through structured workflows
* Practical challenges in building AI systems (data quality, entity matching, query routing)

The system reflects real-world AI engineering work, combining backend systems, data pipelines, and LLM-based reasoning.

---

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/yourusername/researchbook.git
cd researchbook
pip install -r requirements.txt
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Edit `.env`:

```
NEO4J_URI_DB1=neo4j+s://your-server:7688
NEO4J_URI_DB2=neo4j+s://your-server:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your-password
LIGHTLLM_URL=https://your-llm-server:4000
LIGHTLLM_API_KEY=sk-your-api-key
```

### 3. Run the application

```bash
streamlit run streamlit_app.py
```

Open: http://localhost:8501

---

## Project Structure

```
researchbook/
├── streamlit_app.py
├── researchbook.py
├── researchbook_final.py
├── enhanced_name_matching.py
├── ai_keyword_extractor.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## Core Components

### ResearchBook (Base Class)

* Connects to Neo4j databases
* Integrates with LLM API
* Core methods: `lookup_person()`, `find_expert()`, `ai_query()`

### ResearchBookFinal (Enhanced)

* Fuzzy name matching (Swedish + international names)
* LLM-based intent parsing
* Structured query workflows
* Strategic meeting recommendations
* Field intelligence generation

---

## Relation Types

| Hard Relations (Direct)         | Soft Relations (Indirect)       |
| ------------------------------- | ------------------------------- |
| Co-author (shared publications) | Keyword similarity              |
| Supervision network             | Research topic overlap          |
| Same organization               | Alumni networks                 |
| Shared alma mater               | Cross-database topic similarity |

---

## Example Usage

```python
from researchbook_final import ResearchBookFinal

rb = ResearchBookFinal()

person = rb.lookup_person("Anders Andersson")

experts = rb.find_expert("machine learning", limit=10)

result = rb.smart_query_handler("Find AI experts at Chalmers")

meetings = rb.strategic_meeting_recommendations("Erik Bohlin", "Chalmers")
```

---

## License

MIT
