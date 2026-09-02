# Zenith

**Adaptive AI-Driven Cyber Defence Research Prototype**

Zenith is a cybersecurity and machine-learning research project exploring how AI can detect suspicious behaviour, distinguish malicious activity from human error, and support proportionate defensive decisions.

The project simulates a small corporate environment with **50 users**, **64 endpoints**, role-based access control, centralised telemetry, behavioural feature engineering, and ML-based classification.

## Research Question

> How effectively can an adaptive AI-driven defence system prevent lateral movement following system compromise while distinguishing malicious behaviour from human error and minimising operational disruption caused by false or disproportionate responses?

## Current Architecture

```text
Office Endpoints
      |
      v
Identity Server ---- File Server
      |                  |
      +--------+---------+
               |
               v
          Zenith Core
               |
               v
      Central Telemetry
```

The simulated organisation contains:

| Department   | Users |
|--------------|------:|
| Finance      |     8 |
| HR           |    12 |
| Sales        |    15 |
| IT           |    12 |
| Office Admin |     3 |
| **Total**    | **50** |

## Implemented Features

- 50-user simulated corporate environment
- 64 registered endpoints
- Department, role and group-based user modelling
- Role-Based Access Control (RBAC)
- Identity Server with:
  - authentication
  - failed-login tracking
  - account lockout
  - password reset
  - session tokens
  - server-side endpoint validation
  - device-bound sessions
- File Server with role-aware resource permissions
- Local JSONL security logging
- Centralised telemetry through Zenith Core
- Live terminal telemetry viewer
- Synthetic behavioural dataset generation
- Behavioural feature engineering
- Random Forest classification
- Logistic Regression comparison
- Confusion-matrix analysis
- Zenith-specific security metrics
- Feature importance, ablation and trusted feature selection

## Behaviour Classes

Zenith currently classifies behaviour into four categories:

```text
normal
human_error
suspicious
malicious
```

The synthetic dataset currently contains **10,000 samples**:

| Class       | Samples |
|-------------|--------:|
| Normal      |   4,000 |
| Human Error |   2,000 |
| Suspicious  |   2,000 |
| Malicious   |   2,000 |

Synthetic data is used for controlled experimentation and does not represent real-world prevalence.

## Behavioural Features

Current trusted features include:

- department
- role
- event type
- hour / off-hours activity
- failed logins
- denied resource access
- unique resources accessed
- role mismatch
- device mismatch
- recent password reset
- successful recovery after failures
- department-resource mismatch
- resource sensitivity
- recently used endpoints
- time since previous event
- repeated resource access
- resource traversal count

Zenith uses structured security events rather than NLP. These features allow the models to learn behavioural patterns and context.

## Current ML Results

The current selected-feature baseline removes several highly predictive synthetic proxy features to produce a more defensible test.

### Random Forest — Selected Features

```text
Accuracy:                 94.85%
Macro F1:                 93.71%
Human Error Escalation:    0.75%
Malicious -> Normal:       0.00%
Malicious -> Suspicious:  18.75%
Suspicious -> Normal:      0.25%
Security Detection:       98.50%
```

### Logistic Regression — Selected Features

```text
Accuracy:                 88.10%
Macro F1:                 85.32%
Human Error Escalation:    3.50%
Malicious -> Normal:       0.00%
Malicious -> Suspicious:  23.75%
Suspicious -> Normal:      0.00%
Security Detection:       97.62%
```

Random Forest currently performs better under overlapping behavioural conditions, particularly in reducing false escalation of legitimate human error.

## Zenith-Specific Evaluation

Standard metrics include:

- accuracy
- precision
- recall
- F1-score
- confusion matrix

Zenith also measures:

- **Human Error Escalation Rate** — human error incorrectly classified as suspicious or malicious
- **Malicious -> Normal Miss Rate** — malicious behaviour incorrectly treated as normal
- **Malicious -> Suspicious Rate** — malicious behaviour downgraded but still security-relevant
- **Suspicious -> Normal Miss Rate**
- **Security Detection Rate** — suspicious or malicious behaviour retained within a security-relevant class

This allows the project to evaluate the operational impact of misclassification rather than relying on accuracy alone.

## Project Structure

```text
zenith/
├── cloud/
├── data/
│   ├── datasets/
│   └── logs/
├── hq/
│   ├── identity_server.py
│   ├── file_server.py
│   ├── telemetry_viewer.py
│   └── zenith_core.py
├── models/
│   └── training/
│       └── train_baseline.py
├── office/
│   ├── finance_team.py
│   ├── hr_team.py
│   ├── sales_team.py
│   ├── it_team.py
│   ├── office_admin_team.py
│   └── office_endpoint.py
├── simulation/
│   └── behaviour_generator.py
├── shared/
├── reports/
├── tests/
├── main.py
├── requirements.txt
└── README.md
```

## Running the Current Prototype

Start the core services:

```powershell
python -m hq.zenith_core
python -m hq.identity_server
python -m hq.file_server
```

Start an Office endpoint:

```powershell
python -m office.office_endpoint
```

Optional live telemetry:

```powershell
python -m hq.telemetry_viewer
```

Generate the behavioural dataset:

```powershell
python -m simulation.behaviour_generator
```

Train and evaluate the baseline models:

```powershell
python -m models.training.train_baseline
```

## Current Development Stage

Completed:

- enterprise simulation
- authentication and endpoint validation
- RBAC
- central telemetry
- behavioural dataset generation
- overlapping behaviour scenarios
- Random Forest and Logistic Regression baselines
- security-specific metrics
- feature importance and feature selection

Next:

- grouped feature-selection experiments
- true event-sequence modelling
- dynamically calculated user baselines
- collective model decision logic
- adaptive risk scoring
- response levels and containment
- simulated attack scenarios
- lateral movement experiments
- adversarial testing
- final research report

## Technology

- Python
- pandas
- scikit-learn
- JSON / JSONL
- TCP sockets
- Git / GitHub
- VS Code

## Status

**Active Development — Research Prototype**

Zenith is not intended for production deployment. Current ML results are based on synthetic behavioural data and are used to evaluate the project methodology, feature design and model behaviour.

---

**Independent Project, 2026–Present**