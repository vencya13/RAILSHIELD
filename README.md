RAILSHIELD — Predictive Counterfactual Railway Control
Overview

RAILSHIELD is an intelligent railway traffic management and decision-support system designed to help identify potential train conflicts, analyze delay propagation, determine conflict root causes, and evaluate alternative operational interventions before they are applied.

The system combines a Python-based railway simulation engine, FastAPI backend, and interactive web dashboard to create a simulated railway environment where different operational decisions can be analyzed safely.

RAILSHIELD follows a counterfactual decision-support approach: instead of only identifying what is happening, it evaluates what could happen under different intervention strategies.

Problem

Modern railway networks manage multiple trains operating through shared tracks, sections, junctions, and platforms. A delay or conflict involving one train can propagate through the network and affect other trains.

Conventional monitoring systems can identify existing operational conflicts, but evaluating the consequences of different possible interventions can be difficult.

RAILSHIELD addresses this challenge by providing a simulation-based environment that can:

Monitor the current railway state
Detect potential conflicts
Analyze delay propagation
Identify possible root causes
Simulate alternative interventions
Compare the resulting outcomes
Support selection of an appropriate intervention
Solution

RAILSHIELD creates a digital representation of a railway network and continuously evaluates train movements and operational constraints.

When a potential conflict is identified, the system performs counterfactual simulations using alternative operational decisions. The resulting scenarios can then be compared with the current situation to understand the potential effect of each intervention.

Core Workflow
Railway Network State
        |
        v
Train Movement Simulation
        |
        v
Headway & Constraint Analysis
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
Generate Intervention Options
        |
        v
Counterfactual Simulation
        |
        v
Compare Outcomes
        |
        v
Decision Support
Key Features
1. Railway Simulation

Models train movements across railway sections and represents the current state of the simulated railway network.

2. Conflict Detection

Identifies potential operational conflicts based on railway constraints such as train separation and headway conditions.

3. Headway Analysis

Monitors the spacing between trains and identifies situations where required separation may be violated.

4. Delay Propagation

Analyzes how delays affecting one train can influence other trains and propagate through the simulated network.

5. Root-Cause Analysis

Provides analysis of the factors contributing to detected conflicts and delays.

6. Counterfactual Simulation

Simulates alternative operational decisions without changing the original scenario.

For example:

Current Scenario
      |
      +---- Intervention A → Simulate → Outcome A
      |
      +---- Intervention B → Simulate → Outcome B
      |
      +---- Intervention C → Simulate → Outcome C

The outcomes can then be compared to support a better operational decision.

7. Future-State Analysis

The system can simulate future railway states over a configurable time horizon to identify potential upcoming conflicts and delays.

8. Interactive Dashboard

The web interface provides visibility into:

Current railway state
Trains in operation
Network delays
Detected conflicts
Root causes
Intervention options
Simulation results
Technology Stack
Backend
Python
FastAPI
Uvicorn
Pydantic
Simulation Engine
Python
Custom railway simulation logic
Train movement modelling
Headway analysis
Conflict detection
Delay propagation
Counterfactual simulation
Frontend
HTML
CSS
JavaScript
Development Environment
Python Virtual Environment
Git and GitHub
Gradle components for the associated project structure
System Architecture
                    RAILSHIELD
                         |
             +-----------+-----------+
             |                       |
             v                       v
      Railway Engine          Web Dashboard
             |
             v
      Network State
             |
      +------+------+
      |             |
      v             v
   Trains       Sections
      |             |
      +------+------+
             |
             v
      Constraint Analysis
             |
             v
      Conflict Detection
             |
             v
      Root-Cause Analysis
             |
             v
   Counterfactual Engine
             |
             v
    Intervention Evaluation
             |
             v
       Decision Support
Project Structure
RAILSHIELD/
│
├── app/
│   └── Application components
│
├── assets/
│   └── Project assets
│
├── backend/
│   ├── engine.py
│   ├── main.py
│   └── requirements.txt
│
├── frontend/
│   └── index.html
│
├── gradle/
│
├── .env.example
├── .gitignore
├── build.gradle.kts
├── gradle.properties
├── metadata.json
├── README.md
└── settings.gradle.kts
API

RAILSHIELD uses FastAPI to expose the railway simulation and analysis functionality.

Railway State
GET /api/state

Returns the current simulated railway state.

Future State
GET /api/future?horizon=15

Generates a future railway state for the specified simulation horizon.

Conflicts
GET /api/conflicts

Returns detected railway conflicts.

Root-Cause Analysis
GET /api/conflicts/{conflict_id}/rootcause

Returns root-cause information for a selected conflict.

Intervention Options
GET /api/conflicts/{conflict_id}/options

Returns available counterfactual intervention options for a conflict.

API Documentation

After starting the backend, interactive API documentation is available at:

http://localhost:8000/docs
Installation
Prerequisites
Python 3.10 or later
Git
Web browser
Clone the Repository
git clone https://github.com/YOUR_USERNAME/RAILSHIELD.git
cd RAILSHIELD
Create Virtual Environment

Windows:

python -m venv venv
Activate Virtual Environment

PowerShell:

venv\Scripts\Activate.ps1

If PowerShell execution policy prevents activation, the project can be run directly using the Python executable inside the virtual environment.

Install Dependencies
cd backend
python -m pip install -r requirements.txt
Running the Application

From the backend directory:

python -m uvicorn main:app --reload --port 8000

If the virtual environment is not activated:

..\venv\Scripts\python.exe -m uvicorn main:app --reload --port 8000

The application will be available at:

http://localhost:8000

API documentation:

http://localhost:8000/docs
Example Workflow

A typical RAILSHIELD analysis follows these steps:

The railway simulation initializes the current network state.
Train movements and section occupancy are evaluated.
Headway and other operational constraints are checked.
Potential conflicts are detected.
The system analyzes the cause of the conflict.
Possible interventions are generated.
Each intervention is simulated independently.
The resulting scenarios are compared.
The system provides decision-support information for selecting an intervention.
Current Implementation

The current RAILSHIELD prototype includes:

Railway network simulation
Train movement simulation
Train priority handling
Section and headway logic
Conflict detection
Delay propagation
Future-state analysis
Root-cause analysis
Counterfactual intervention simulation
Intervention comparison
FastAPI backend
Interactive web dashboard
Future Enhancements
Machine Learning

A future version of RAILSHIELD will introduce a machine learning layer for predictive conflict-risk estimation.

The planned approach is to generate synthetic railway scenarios using the existing simulation engine and use the resulting simulation outcomes as ground-truth labels for model training.

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

The initial planned model is a Random Forest classifier using railway state features such as:

Train speed
Train type
Train priority
Current delay
Headway
Distance to conflict
Section occupancy
Platform occupancy
Traffic density
Time to conflict
Number of trains
Freight/express interaction

The ML component will be an additional intelligence layer and will not replace the existing railway simulation engine.

Real-World Data Integration

Future versions may integrate real railway operational data to improve predictive capabilities and enable validation against real-world railway scenarios.

Edge and IoT Integration

Future development may also explore integration with railway sensors and edge computing devices for real-time data collection and processing.

Current Limitations
The current system operates using simulated railway scenarios.
It does not currently use live railway operational data.
The current prototype has not been validated for real-world railway operations.
The system does not directly control railway signalling or railway infrastructure.
Future machine learning predictions will require appropriate real-world validation before operational deployment.
Future Vision

RAILSHIELD aims to evolve from a simulation-based decision-support prototype into a predictive railway intelligence platform.

The long-term vision is:

Real-Time Railway Data
          |
          v
Data Processing
          |
          v
Predictive Intelligence
          |
          v
Conflict Risk Estimation
          |
          v
Counterfactual Simulation
          |
          v
Intervention Evaluation
          |
          v
Operator Decision Support

The goal is to help railway operators move from reactive conflict management toward predictive, simulation-driven decision-making.

Disclaimer

RAILSHIELD is a prototype developed for educational, research, and hackathon purposes. It is not intended for direct control of railway infrastructure and does not replace certified railway signalling, interlocking, traffic management, or safety-critical railway systems.
