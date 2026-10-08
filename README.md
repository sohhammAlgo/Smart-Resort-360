# Smart Resort 360 🏨🤖

## AI-Powered Resort Management & Autonomous Operations Platform

Smart Resort 360 is an AI-driven resort management system designed to help resorts **predict operational problems, optimize scarce resources, and automate staff coordination**.

Instead of acting only as a guest chatbot, Smart Resort 360 works as an **operational intelligence layer** connecting prediction, scheduling, recommendations, and execution.

---

## 🚨 Problems We Solve

### 1. Preventive Maintenance

Guests may experience problems such as a malfunctioning AC but never report them.

Smart Resort 360 analyzes existing resort data such as:

- Asset age
- Previous maintenance history
- Service intervals
- Occupancy and usage patterns
- Previous complaints

It calculates a **maintenance risk score** and can create a preventive inspection task before the problem affects another guest.

> **Important:** The system identifies maintenance risk; it does not claim that a physical failure has been confirmed.

---

### 2. Smart Amenity Scheduling

Popular amenities such as spas can have multiple guests waiting for the same resource.

Instead of relying on manual allocation, Smart Resort 360 uses a **deterministic and auditable priority scheduler**.

Priority can consider:

- Waiting time
- Guest readiness
- Amenity compatibility
- Guest loyalty

This creates a fair and explainable queue while reducing unnecessary waiting.

---

### 3. Intelligent Alternative Recommendations

If a guest's preferred amenity is unavailable, Smart Resort 360 searches for **actually available alternatives**.

The recommendation process combines:

- Guest intent
- Semantic similarity
- Current availability
- Guest preferences
- Time compatibility
- Convenience

Only amenities verified as available by the database are recommended.

---

# 🧠 Core Intelligence

Smart Resort 360 combines predictive ML, LLM-based reasoning, retrieval, and deterministic operational logic.

### Predictive Intelligence

Used for:

- Maintenance risk prediction
- Occupancy forecasting
- Demand forecasting
- Operational planning

### Resource Optimization

Used for:

- Amenity scheduling
- Waitlist management
- Alternative recommendations
- Staff coordination
- Operational prioritization

### Generative AI

Used for:

- Understanding guest requests
- Natural-language interaction
- Generating contextual responses
- AI-assisted operational workflows
- RAG-based resort knowledge retrieval

---

# 🤖 AI & Automation

## LangGraph

LangGraph coordinates multi-step AI workflows and operational agents.

It is used where a task requires multiple decisions or actions instead of a single LLM response.

---

## LLM

An open-weight LLM is used for:

- Natural-language understanding
- Guest request interpretation
- Response generation
- Operational reasoning
- AI-assisted workflows

The LLM does **not directly control critical database state**. Operational actions are validated by the backend and database rules.

---

## ChromaDB + RAG

ChromaDB provides vector storage for resort knowledge.

RAG is used to retrieve relevant information before generating responses, such as:

- Resort policies
- Amenity information
- Guest-service information
- Operational documentation
- Internal knowledge

---

## XGBoost / LightGBM

XGBoost or LightGBM can be used for structured predictive tasks such as:

- Maintenance risk prediction
- Occupancy prediction
- Operational risk scoring
- Demand-related prediction

The model used depends on the specific prediction problem and available historical data.

---

## Forecasting

Forecasting models such as **Chronos-Bolt / MOIRAI** can support:

- Occupancy forecasting
- Demand forecasting
- Resource planning
- Operational preparation

---

# 🏗️ System Architecture

```text
                         ┌─────────────────────────┐
                         │      React + TypeScript  │
                         │         Frontend        │
                         └────────────┬────────────┘
                                      │
                                      ▼
                         ┌─────────────────────────┐
                         │         FastAPI         │
                         │         Backend         │
                         │                         │
                         │ Auth / RBAC / APIs      │
                         │ Business Logic          │
                         │ Operational Workflows   │
                         └────────────┬────────────┘
                                      │
                    ┌─────────────────┼─────────────────┐
                    │                 │                 │
                    ▼                 ▼                 ▼
             ┌─────────────┐  ┌─────────────┐  ┌─────────────┐
             │ PostgreSQL  │  │    Redis    │  │    Kafka    │
             │             │  │             │  │             │
             │ Source of   │  │ Cache /     │  │ Event Bus   │
             │ Truth       │  │ Temp State  │  │             │
             └──────┬──────┘  └─────────────┘  └──────┬──────┘
                    │                                  │
                    └────────────────┬─────────────────┘
                                     ▼
                          ┌─────────────────────────┐
                          │       AI Engine         │
                          │                         │
                          │ XGBoost / LightGBM      │
                          │ Forecasting             │
                          │ LLM                     │
                          └────────────┬────────────┘
                                       │
                                       ▼
                          ┌─────────────────────────┐
                          │       LangGraph         │
                          │    Agent Workflows      │
                          └────────────┬────────────┘
                                       │
                                       ▼
                          ┌─────────────────────────┐
                          │       ChromaDB           │
                          │        + RAG             │
                          └─────────────────────────┘
```

### Data Responsibility

- **PostgreSQL** — authoritative source of truth
- **Redis** — caching and temporary state
- **Kafka** — asynchronous event communication
- **AI models** — prediction and intelligence
- **LangGraph** — multi-step agent/workflow orchestration
- **ChromaDB** — semantic retrieval

---

# 🔄 Example End-to-End Operational Flow

A typical maintenance scenario works like this:

```text
Asset / Maintenance Data
          ↓
Maintenance Risk Analysis
          ↓
High Risk Detected
          ↓
Preventive Inspection Task
          ↓
Manager Authorization
          ↓
Amenity → UNAVAILABLE
          ↓
Stop New Offers
          ↓
Preserve Existing Waitlist
          ↓
Find Available Alternatives
          ↓
Recommend Alternative to Guest
          ↓
Guest Reserves Alternative
          ↓
Maintenance Completed
          ↓
Amenity → AVAILABLE
          ↓
Scheduling Resumes
```

This connects predictive maintenance, resource optimization, recommendation, and operational execution into one workflow.

---

# 👨‍💼 Autonomous Department Head

The **Autonomous Department Head** acts as the execution and coordination layer of Smart Resort 360.

It can coordinate approved operational actions such as:

- Creating maintenance tasks
- Dispatching staff tasks
- Coordinating amenity allocation
- Sending guest notifications
- Triggering asynchronous voice escalation
- Coordinating approved operational workflows

The goal is to reduce manual coordination between departments and allow operational decisions to move from **detection → decision → execution**.

### Controlled Execution

The Autonomous Department Head does not bypass authorization or business rules.

Sensitive operational actions can require **manager authorization** before execution.

---

# 🧩 Intelligence Flow

```text
                    Resort Data
                        │
        ┌───────────────┼────────────────┐
        │               │                │
        ▼               ▼                ▼
   Historical       Guest Data       Operational
      Data                              Data
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                 AI Intelligence
                        │
        ┌───────────────┼────────────────┐
        ▼               ▼                ▼
   Prediction      Recommendation    Understanding
        │               │                │
        └───────────────┼────────────────┘
                        ▼
                 Decision Layer
                        │
                        ▼
              Autonomous Department
                     Head
                        │
                        ▼
                 Approved Action
                        │
                        ▼
                  Resort Staff
```

---

# 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL / Neon PostgreSQL |
| Cache / Temporary State | Redis |
| Event Bus | Apache Kafka |
| AI Workflow | LangGraph |
| LLM | Open-weight LLM |
| RAG / Vector Database | ChromaDB |
| Machine Learning | XGBoost / LightGBM |
| Forecasting | Chronos-Bolt / MOIRAI |
| Authentication | JWT + bcrypt + Email OTP |
| MLOps | MLflow |
| Containerization | Docker |
| Deployment | Kubernetes |
| CI/CD | Git-based CI/CD |

---

# 🔐 Security

The platform uses:

- JWT authentication
- bcrypt password hashing
- Email OTP authentication
- Role-based access control
- Environment variables for secrets
- PostgreSQL as the authoritative data source
- Manager authorization for sensitive operational actions

### Environment Variables

Frontend environment-specific configuration uses:

```env
VITE_API_BASE_URL=https://your-backend-url
```

Backend secrets such as:

- Database credentials
- JWT secrets
- SMTP credentials
- API keys

must be stored as environment variables.

> **Never commit secrets to the repository.**

---

# 📁 Project Structure

```text
smart-resort-360/
│
├── frontend/
│   └── client/
│       ├── src/
│       ├── public/
│       ├── .env.example
│       └── package.json
│
├── backend/
│   ├── app/
│   ├── tests/
│   ├── scripts/
│   └── requirements.txt
│
├── k8s/
│
├── docker-compose.yml
│
└── README.md
```

---

# 🚀 Running Locally

## Frontend

```bash
cd frontend/client
pnpm install
pnpm dev
```

Create:

```text
frontend/client/.env
```

Configure:

```env
VITE_API_BASE_URL=http://localhost:8000
```

---

## Backend

```bash
cd backend
uvicorn app.main:app --reload
```

The FastAPI API will normally be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

---

# 🗄️ Database

Smart Resort 360 uses PostgreSQL as the authoritative source of operational data.

A managed PostgreSQL service such as **Neon PostgreSQL** can be used for deployment.

The database stores information required for:

- Guests
- Staff
- Managers
- Bookings
- Amenities
- Waitlists
- Maintenance tasks
- Notifications
- Operational state
- Authentication-related data

Redis is used for caching and temporary state where appropriate.

---

# 🌐 Deployment

## Frontend

The React frontend can be deployed using Vercel.

Configure:

```env
VITE_API_BASE_URL=https://YOUR-BACKEND-URL
```

---

## Backend

The FastAPI backend can be deployed using the project's supported container/cloud infrastructure.

Docker can be used to package the backend, while Kubernetes can be used for container orchestration where required.

---

# 🔄 CI/CD

The project can use Git-based CI/CD to:

```text
Git Push
   ↓
Build
   ↓
Test
   ↓
Build Docker Image
   ↓
Deploy
   ↓
Run Health Checks
```

Environment secrets must be provided through the deployment environment rather than committed to Git.

---

# 🎯 Key Differentiator

Traditional resort management systems mainly record what happened.

Smart Resort 360 aims to predict what may happen and coordinate what should happen next.

```text
Traditional PMS
       ↓
Record → Manage → Respond

Smart Resort 360
       ↓
Predict → Decide → Coordinate → Execute
```

The central idea is:

> **From reactive resort management to proactive AI-driven operations.**

---

# 🏆 Hackathon Value Proposition

Smart Resort 360 brings together:

**Predictive Intelligence + Resource Optimization + RAG + AI Agents + Automated Operations**

into a single resort-management platform.

The system is designed to help resorts:

- Reduce operational delays
- Identify maintenance risks earlier
- Allocate amenities fairly
- Reduce guest waiting
- Recommend verified available alternatives
- Coordinate staff more efficiently
- Improve the overall guest experience

---

# 🧠 What Makes Smart Resort 360 Different?

Smart Resort 360 is not simply:

- A chatbot
- A booking system
- A recommendation engine
- A predictive model

It combines these capabilities with an operational execution layer.

```text
              ┌──────────────────────┐
              │   Predict Problems    │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │   Understand Context │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │   Decide Next Action │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │ Coordinate Resources │
              └──────────┬───────────┘
                         ↓
              ┌──────────────────────┐
              │   Execute Approved   │
              │       Actions        │
              └──────────────────────┘
```

**Smart Resort 360 — Predict → Decide → Coordinate → Execute.**
