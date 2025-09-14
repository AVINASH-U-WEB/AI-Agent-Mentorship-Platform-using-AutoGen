AI-Agent Mentorship Platform


This project is an advanced, AI-driven backend for a skill-exchange network. It leverages a sophisticated multi-agent system built with Microsoft AutoGen to intelligently and autonomously match mentees with suitable mentors. The entire system is served via a robust and asynchronous API built with FastAPI.

🏗️ Architectural Overview
The system is designed to be highly responsive, scalable, and robust, centered around two key principles: asynchronous processing and decoupled agent logic.

Asynchronous by Design: The primary API endpoints are non-blocking. They accept a request, create an initial record in the database, and immediately return a response. The heavy lifting of AI reasoning and matching is delegated to a background task.

Decoupled Agentic Core: The AI logic is encapsulated within specialized, single-purpose agents, each with a clear and rigid set of instructions. This makes the system more reliable and easier to debug.

🚀 System Architecture
Diagram
Code




<img width="2868" height="3186" alt="deepseek_mermaid_20250914_838e8c" src="https://github.com/user-attachments/assets/80af101b-bef0-4569-b8ad-4d0f7b933409" />


⚙️ System Workflow
<br>
The entire lifecycle of a mentorship request follows a controlled, sequential process:
<img width="5235" height="2931" alt="deepseek_mermaid_20250914_f419c3" src="https://github.com/user-attachments/assets/d4e03a97-d8d0-4a68-97a0-5cd73fc7243e" />

Diagram
Code
🛠️ Core Technologies
Backend Framework: FastAPI

AI Agent Framework: Microsoft AutoGen

Database: SQLite (via SQLAlchemy Async)

LLM Integration: Ollama (for local models)

LLM Proxy: LiteLLM (for an OpenAI-compatible API)

Validation: Pydantic

📦 Installation & Setup
Prerequisites
Python 3.10+

Git

Ollama installed and running

1. Clone & Set Up Environment
bash
# Clone the repository
git clone <your-repository-url>
cd <your-project-directory>

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
2. Configure Local LLM
Terminal 1 - Start LLM Service:

bash
# Pull a capable model (llama3:8b recommended)
ollama pull llama3:8b

# Start LiteLLM proxy server
litellm --model ollama/llama3:8b
3. Run Application Server
Terminal 2 - Start Application:

bash
uvicorn app.main:app --reload --port 8000
Your API is now available at http://127.0.0.1:8000 with documentation at http://127.0.0.1:8000/docs.

4. Run Tests
bash
# Run test suite with coverage
pytest --cov=app tests/
📋 API Usage
Create Mentorship Request
bash
curl -X 'POST' \
  'http://localhost:8000/mentorship-requests' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": 123,
  "skill_to_learn": "Python Programming",
  "skill_to_offer": "Graphic Design"
}'
Check Request Status
bash
curl -X 'GET' \
  'http://localhost:8000/mentorship-requests/1'
🧪 Testing
The project includes comprehensive tests:

bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=app --cov-report=html

Fork the repository

Create a feature branch (git checkout -b feature/amazing-feature)

Commit changes (git commit -m 'Add amazing feature')

Push to branch (git push origin feature/amazing-feature)

Open a Pull Request

📄 License
This project is licensed under the MIT License - see the LICENSE file for details.

🆓 Free and Open Source
This is a free and open source project. We welcome contributions from the community!

