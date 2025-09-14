# 🤖 AI-Agent Mentorship Platform

This repository contains the backend service for the **AI-Agent Mentorship Platform**, an advanced skill-exchange network powered by intelligent multi-agent systems.

It leverages **Microsoft AutoGen** agents to autonomously match mentees with suitable mentors based on skills to learn and skills to offer. The entire system is served via a robust, asynchronous API built with **FastAPI**, ensuring responsiveness and scalability.

---

## ✨ Key Features

- **Intelligent Mentor Matching** – Multi-agent orchestration automatically pairs mentees with the most suitable mentors.  
- **Asynchronous API** – Non-blocking FastAPI endpoints return responses instantly while AI reasoning happens in the background.  
- **Agentic Core Design** – Encapsulated, single-purpose agents (orchestration, trust, matchmaking) for reliability and easier debugging.  
- **Local LLM Integration** – Runs on **Ollama** with **LiteLLM** proxy for OpenAI-compatible APIs.  
- **Database Persistence** – Uses **SQLite (SQLAlchemy Async)** to store requests and matches.  
- **Validation First** – Input and response validation with **Pydantic**.  

---

## 🛠️ Technology Stack

- **Framework:** Python 3.10+, FastAPI  
- **Agents:** Microsoft AutoGen  
- **Database:** SQLite (Async SQLAlchemy)  
- **LLM Runtime:** Ollama (local)  
- **LLM Proxy:** LiteLLM  
- **Validation:** Pydantic  

---

## 🏗️ System Architecture

![System Architecture](https://github.com/user-attachments/assets/80af101b-bef0-4569-b8ad-4d0f7b933409)

---

## ⚙️ System Workflow

The lifecycle of a mentorship request follows a controlled, sequential process:  

![System Workflow](https://github.com/user-attachments/assets/d4e03a97-d8d0-4a68-97a0-5cd73fc7243e)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+  
- Git  
- Ollama installed and running  

### Installation & Setup

#### 1. Clone the repository
bash
git clone <your-repository-url>
cd <your-project-directory>
2. Create and activate a virtual environment
bash
Copy code
python -m venv venv
source venv/bin/activate   # On Windows: venv\Scripts\activate
3. Install dependencies
bash
Copy code
pip install -r requirements.txt
4. Configure Local LLM
Terminal 1 – Start LLM Service:

bash
Copy code
ollama pull llama3:8b
litellm --model ollama/llama3:8b
5. Run Application Server
Terminal 2 – Start API:

bash
Copy code
uvicorn app.main:app --reload --port 8000
API base: http://127.0.0.1:8000

API docs: http://127.0.0.1:8000/docs

📋 API Endpoints
Core Mentorship Operations
Endpoint	Method	Description	Body Example
/mentorship-requests	POST	Create a new mentorship request	{"user_id": 123, "skill_to_learn": "Python Programming", "skill_to_offer": "Graphic Design"}
/mentorship-requests/{id}	GET	Get the status of a mentorship request	N/A

🧪 Testing
bash
Copy code
# Run all tests
pytest  

# Run with verbose output
pytest -v  

# Run with coverage report
pytest --cov=app  
pytest --cov=app --cov-report=html

🤝 Contributing
We welcome contributions from the community!

Fork the repository

Create a feature branch:

bash
Copy code
git checkout -b feature/amazing-feature
Commit your changes:

bash
Copy code
git commit -m 'Add amazing feature'
Push to your branch:

bash
Copy code
git push origin feature/amazing-feature
Open a Pull Request 🚀

🐛 Troubleshooting
Ollama Errors: Ensure Ollama is running and the llama3:8b model is pulled.

LiteLLM Connection Issues: Verify that the proxy server is running on the correct port.

Module Import Errors: Ensure dependencies are installed and your virtual environment is active.

📜 License
This project is licensed under the MIT License – see the LICENSE file for details.

🆓 Free & Open Source
This is a free and open-source project. Community contributions, feedback, and improvements are always welcome!

