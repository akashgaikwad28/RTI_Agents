
#  RTI Agent – AI-Powered RTI Automation for India

> **Stage 1 MVP**: Backend agent workflow for automating RTI applications, classification, public info checks, and tracking.

---

## 🚀 Project Overview

**RTI Agent** is an intelligent automation system designed to simplify the Right to Information (RTI) process in India. It uses LLMs and modular agents to format user queries, classify them to the correct department, check if the information is already public, and track RTI requests.

- **Tech Stack**: Python · LangChain · LangGraph · Groq · Gemini · Google Translate · MongoDB
- **Stage**: MVP (Backend only)
- **Goal**: Automate RTI creation, classification, info retrieval, and tracking

---

## 🧠 Architecture Overview

```
User Input → Formatter Agent → Translator → Classifier Agent → MongoDB → Info Fetcher → Email Client → Tracker Agent
```

Each module is designed as a LangGraph node, enabling scalable orchestration and modular debugging.

---

## 📁 Project Structure

```
│   .dockerignore
│   .env
│   .gitignore
│   app.py
│   docker-compose.yml
│   Dockerfile
│   LICENSE
│   pyproject.toml
│   README.md
│   requirements.txt
│   uv.lock
│
├───.github
│   └───workflows
│           ci-cd.yml
│
├───agents
│   │   classifier_agent.py
│   │   formatter_agent.py
│   │   info_fetcher_agent.py
│   │   tracker_agent.py
│   │   __init__.py
│   │
│   ├───base
│   │   │   base_agent.py
│   │   │   graph_manager.py
│   │   
│   │   
│   │           
│   │           
│   │
│   └───nodes
│       │   classifier_node.py
│       │   formatter_node.py
│       │   info_fetcher_node.py
│       │   tracker_node.py
│      
│
├───chains
│       classifier_chain.py
│       formatter_chain.py
│       info_fetcher_chain.py
│       tracker_chain.py
│       utils_chain.py
│
├───config
│       settings.py
│
├───database
│       schema.py
│
├───logs
│       rti_system.log
│
├───mcp_clients
│       email_client.py
│       gemini_client.py
│       groq_client.py
│       mongo_client.py
│       translator_client.py
│
├───memory
│       memory_chain.py
│       memory_manager.py
│       memory_node.py
│       memory_store.json
│       __init__.py
│
├───prompts
│       classifier_prompt.txt
│       formatter_prompt.txt
│       info_fetcher_prompt.txt
│       tracker_prompt.txt
│
├───schemas
│       agent_response_schema.py
│       rti_query_schema.py
│
└───utils
        exception_handler.py
        helpers.py
        logger.py
        logging_config.py
        templates.py
        __init__.py

```

---

## 🧩 Modules & Responsibilities

| Module               | Role                                                  |
|----------------------|-------------------------------------------------------|
| `formatter_agent`    | Formats raw user query into RTI template              |
| `translator_client`  | Translates query to English or regional language      |
| `classifier_agent`   | Classifies RTI to correct department                  |
| `info_fetcher_agent` | Checks if info is already public                      |
| `tracker_agent`      | Generates tracking ID and updates status              |
| `mongo_client`       | Stores RTI data and tracking info                     |
| `email_client`       | Sends RTI to department (mocked for MVP)              |

---

## 🛠️ Setup Instructions

```bash
# 1. Activate virtual environment
source .rti/Scripts/activate

# 2. Install dependencies
uv pip install -r requirements.txt

# 3. Run the orchestrator
python app.py
```

---

## 🧪 Sample Workflow (MVP)

1. User submits RTI form (name, contact, query, address)
2. Query is formatted via Groq LLM
3. Translated to appropriate language
4. Classified to correct department
5. Stored in MongoDB with tracking ID
6. Info fetcher checks RTI portal:
   - If info is public → return to user
   - If not → email simulated to department
7. Tracker updates status

---

## 📅 Milestones

| Milestone               | Status     |
|-------------------------|------------|
| Project Setup           | ✅ Complete |
| MCP Clients             | 🔜 In Progress |
| Agent Implementation    | 🔜 Next |
| LangGraph Orchestration | ⏳ Pending |
| Testing & MVP           | ⏳ Pending |
| Documentation           | 📝 This file |

---

## 📚 Tech Stack

- **Python 3.11+**
- **LangChain + LangGraph**
- **Groq + Gemini + Google Translate**
- **MongoDB + Pydantic**
- **Email Validator (mocked)**
- **Optional Web API**: FastAPI + Uvicorn

---

## 📈 Future Extensions

- Web frontend for RTI form input
- Integration with official RTI APIs
- Analytics dashboard for RTI trends
- Regional language support via NLLB or IndicTrans2

---

## 👨‍💻 Author

**Akash Gaikwad**  

🔗 [LinkedIn](https://www.linkedin.com/in/akashgaikwad28) · 📁 [GitHub](https://github.com/akashgaikwad28)

---

> Built with ❤️ to empower transparency and citizen access to public information.
```
