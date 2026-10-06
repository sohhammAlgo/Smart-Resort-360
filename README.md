# Smart Resort 360 🏨🤖

AI-Powered Resort Management & Autonomous Operations Platform

Smart Resort 360 is an AI-driven resort management system designed to help resorts predict operational problems, optimize scarce resources, and automate staff coordination.

Instead of simply acting as a guest chatbot, Smart Resort 360 works as an operational intelligence layer connecting prediction, scheduling, recommendations, and execution.

## 🚨 Problems We Solve

### 1\. Preventive Maintenance

Guests may experience problems such as a malfunctioning AC but never report them.

Smart Resort 360 analyzes existing resort data such as:

*   Asset age
    
*   Previous maintenance history
    
*   Service intervals
    
*   Occupancy/usage patterns
    
*   Previous complaints
    

It calculates a maintenance risk score and can create a preventive inspection task before the problem affects another guest.

> The system identifies maintenance risk, not confirmed physical failure.

### 2\. Smart Amenity Scheduling

Popular amenities such as spas can have multiple guests waiting for the same resource.

Instead of relying on manual allocation or making guests wait for a long voice-call interaction, Smart Resort 360 uses a deterministic priority scheduler.

Priority considers factors such as:

*   Waiting time
    
*   Guest readiness
    
*   Amenity compatibility
    
*   Guest loyalty
    

This creates a fair and auditable queue.

### 3\. Intelligent Alternative Recommendations

If a guest's preferred amenity is unavailable, the system searches for actually available alternatives.

It combines:

*   Guest intent
    
*   Semantic similarity
    
*   Availability
    
*   Preferences
    
*   Time compatibility
    
*   Convenience
    

Only amenities verified as available by the database are recommended.

## 🧠 Core Intelligence

## 🤖 AI & Automation

### LangGraph

Used to coordinate multi-step AI workflows and operational agents.

### LLM

Used for:

*   Understanding guest requests
    
*   Natural-language interaction
    
*   Generating responses
    
*   AI-assisted operational workflows
    

### ChromaDB

Used for semantic retrieval and RAG-based resort knowledge.

### XGBoost / LightGBM

Used where appropriate for predictive intelligence such as maintenance and operational prediction.

### Forecasting

Occupancy and demand forecasting helps the resort prepare for future operational requirements.

## 🏗️ System Architecture

Plain textANTLR4BashCC#CSSCoffeeScriptCMakeDartDjangoDockerEJSErlangGitGoGraphQLGroovyHTMLJavaJavaScriptJSONJSXKotlinLaTeXLessLuaMakefileMarkdownMATLABMarkupObjective-CPerlPHPPowerShell.propertiesProtocol BuffersPythonRRubySass (Sass)Sass (Scss)SchemeSQLShellSwiftSVGTSXTypeScriptWebAssemblyYAMLXML                    `┌─────────────────┐                      │   React + TS    │                      │    Frontend     │                      └────────┬────────┘                               │                               ▼                      ┌─────────────────┐                      │    FastAPI      │                      │    Backend      │                      └────────┬────────┘                               │            ┌──────────────────┼──────────────────┐            │                  │                  │            ▼                  ▼                  ▼     ┌─────────────┐    ┌─────────────┐    ┌─────────────┐     │ PostgreSQL  │    │    Redis    │    │    Kafka    │     │ Source of   │    │ Fast/Temp   │    │ Event Bus   │     │ Truth       │    │ State       │    │             │     └─────────────┘    └─────────────┘    └─────────────┘            │            ├───────────────────────┐            ▼                       ▼     ┌─────────────┐         ┌─────────────┐     │  AI Engine  │         │  LangGraph  │     │ XGBoost etc │         │   Agents    │     └─────────────┘         └──────┬──────┘                                    │                                    ▼                             ┌─────────────┐                             │  ChromaDB   │                             │    + RAG    │                             └─────────────┘`

## 🔄 Example End-to-End Flow

A typical maintenance scenario works like this:

```text
Asset Data      ↓  Maintenance Risk Analysis      ↓  High Risk Detected      ↓  Preventive Inspection Task      ↓  Manager Authorization      ↓  Amenity → UNAVAILABLE      ↓  Stop New Offers      ↓  Preserve Existing Waitlist      ↓  Recommend Available Alternatives      ↓  Guest Reserves Alternative      ↓  Maintenance Completed      ↓  Amenity → AVAILABLE      ↓  Scheduling Resumes
```

This connects our three major intelligence capabilities into one operational workflow.

## 👨‍💼 Autonomous Department Head

The Autonomous Department Head acts as the execution and coordination layer.

It can coordinate actions such as:

*   Creating maintenance tasks
    
*   Dispatching staff tasks
    
*   Coordinating amenity allocation
    
*   Sending guest notifications
    
*   Triggering asynchronous voice escalation
    
*   Coordinating approved operational actions
    

The goal is to reduce manual coordination between departments.

## 🛠️ Technology Stack

| Layer | Technology |
|---|---|
| Frontend | React, TypeScript, Tailwind CSS |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Cache / Temporary State | Redis |
| Event Bus | Apache Kafka |
| AI Workflow | LangGraph |
| LLM | Open-weight LLM |
| RAG / Vector DB | ChromaDB |
| ML | XGBoost / LightGBM |
| Forecasting | Chronos-Bolt / MOIRAI |
| Authentication | JWT + bcrypt + Email OTP |
| MLOps | MLflow |
| Containerization | Docker |
| Deployment | Kubernetes |
| CI/CD | Git-based CI/CD |

## 🔐 Security

The platform uses:

*   JWT authentication
    
*   bcrypt password hashing
    
*   Email OTP authentication
    
*   Role-based access control
    
*   Environment variables for secrets
    
*   PostgreSQL as the authoritative data source
    
*   Manager authorization for sensitive operational actions
    

Frontend environment-specific configuration is stored through environment variables such as:

```text
VITE_API_BASE_URL=https://your-backend-url
```

Secrets should never be committed to the repository.

## 📁 Project Structure

```text
smart-resort-360/  │  ├── frontend/  │   └── client/  │       ├── src/  │       ├── public/  │       ├── .env.example  │       └── package.json  │  ├── backend/  │   ├── app/  │   ├── tests/  │   ├── scripts/  │   └── requirements.txt  │  ├── k8s/  │  ├── docker-compose.yml  │  └── README.md
```

## 🚀 Running Locally

Frontend
--------

```text
cd frontend/client  pnpm install  pnpm dev
```

Create:

```text
frontend/client/.env
```

and configure:

```text
VITE_API_BASE_URL=http://localhost:8000
```

Backend
-------

```text
cd backend  uvicorn app.main:app --reload
```

The FastAPI API will normally be available at:

```text
http://localhost:8000
```

Swagger documentation:

```text
http://localhost:8000/docs
```

## 🌐 Deployment

The frontend can be deployed using Vercel.

Configure the Vercel environment variable:

```text
VITE_API_BASE_URL=https://YOUR-BACKEND-URL
```

The backend can be deployed separately using the project's supported container/cloud infrastructure.

## 🎯 Key Differentiator

Traditional resort systems mainly record what happened.

Smart Resort 360 aims to predict what may happen and coordinate what should happen next.

```text
Traditional PMS       ↓  Record → Manage → Respond  Smart Resort 360       ↓  Predict → Decide → Coordinate → Execute
```

The central idea is:

> From reactive resort management to proactive AI-driven operations.

## 🏆 Hackathon Value Proposition

Smart Resort 360 brings together:

Predictive Intelligence + Resource Optimization + RAG + AI Agents + Automated Operations

into a single resort-management platform.

The result is a system designed to help resorts:

*   Reduce operational delays
    
*   Prevent avoidable maintenance issues
    
*   Allocate amenities fairly
    
*   Reduce guest waiting
    
*   Provide intelligent alternatives
    
*   Coordinate staff more efficiently
    
*   Improve the overall guest experience
