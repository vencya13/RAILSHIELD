RAILSHIELD — Predictive Counterfactual Railway Control
Overview

RAILSHIELD is an intelligent railway traffic management and decision-support system designed to predict potential train conflicts, analyze delay propagation, identify root causes, and evaluate alternative interventions before they are applied.

The current prototype combines a Python-based railway simulation engine with a FastAPI backend and a web-based dashboard to model railway operations and support proactive decision-making.

Problem Statement

Railway networks operate with multiple trains sharing constrained infrastructure such as tracks, sections, junctions, and platforms. A delay or conflict involving one train can propagate through the network and affect other services.

Traditional monitoring approaches primarily identify existing conflicts. RAILSHIELD aims to go beyond detection by simulating possible interventions and evaluating their potential consequences before an operational decision is made.

Key Features
Railway network and train movement simulation
Train priority and headway management
Conflict detection
Delay propagation analysis
Root-cause analysis
Future-state prediction
Counterfactual intervention simulation
Comparison of possible interventions
Decision-support recommendations
Interactive web dashboard
REST APIs using FastAPI
How It Works
Current Railway State
        |
        v
Railway Simulation
        |
        v
Conflict Detection
        |
        v
Delay Propagation Analysis
        |
        v
Root-Cause Analysis
        |
        v
Generate Interventions
        |
        v
Counterfactual Simulation
        |
        v
Compare Outcomes
        |
        v
Recommend Suitable Intervention
Technology Stack
Backend
Python
FastAPI
Uvicorn
Pydantic
Simulation
Python-based railway simulation engine
Train movement modelling
Headway logic
Conflict detection
Delay propagation
Counterfactual simulation
Frontend
HTML
CSS
JavaScript
Project Structure
RAILSHIELD/
├── app/
├── assets/
├── backend/
│   ├── engine.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── index.html
├── gradle/
├── .env.example
├── .gitignore
├── build.gradle.kts
├── gradle.properties
├── metadata.json
├── README.md
└── settings.gradle.kts
API Endpoints

The current backend provides APIs for railway state, future prediction, conflicts, root-cause analysis, and intervention options.

GET /api/state
GET /api/future?horizon=15
GET /api/conflicts
GET /api/conflicts/{conflict_id}/rootcause
GET /api/conflicts/{conflict_id}/options
Running the Project

Clone the repository:

git clone https://github.com/YOUR_USERNAME/RAILSHIELD.git
cd RAILSHIELD

Create and activate a virtual environment:

python -m venv venv

Windows:

venv\Scripts\activate

Install dependencies:

cd backend
python -m pip install -r requirements.txt

Start the backend:

python -m uvicorn main:app --reload --port 8000

The application will be available at:

http://localhost:8000

API documentation:

http://localhost:8000/docs
Current Status

The current prototype implements railway simulation, conflict detection, delay propagation, root-cause analysis, future-state analysis, and counterfactual intervention evaluation.

Future Enhancements

A future version will integrate a machine learning layer trained on synthetic railway scenarios generated from the existing simulation environment.

Planned ML workflow:

Synthetic Railway Scenarios
        |
        v
Existing Railway Simulation
        |
        v
Ground-Truth Conflict Labels
        |
        v
Machine Learning Model
        |
        v
Conflict Risk Prediction
        |
        v
Counterfactual Simulation
        |
        v
Intervention Recommendation

Future development may also include integration with real railway operational data and edge/IoT devices for real-time railway state collection.

Limitations
The current prototype uses simulated railway scenarios.
It does not currently use live railway operational data.
The system has not been validated for real-world railway operations.
The current system is a decision-support prototype and does not directly control railway infrastructure.
Disclaimer

RAILSHIELD is a prototype developed for educational, research, and hackathon purposes. It is not intended to directly control real railway infrastructure or replace certified railway signalling, interlocking, or railway traffic management systems.
