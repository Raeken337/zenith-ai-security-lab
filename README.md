\# Zenith



\*\*Adaptive AI-Driven Cyber Defence Research Prototype\*\*



Zenith is a cybersecurity and machine-learning research project exploring how AI can detect suspicious behaviour, distinguish malicious activity from human error, and support proportionate defensive decisions.



The project simulates a small corporate environment with \*\*50 users\*\*, \*\*64 endpoints\*\*, role-based access control, centralised telemetry, behavioural feature engineering, and ML-based classification.



\## Research Question



> How effectively can an adaptive AI-driven defence system prevent lateral movement following system compromise while distinguishing malicious behaviour from human error and minimising operational disruption caused by false or disproportionate responses?



\## Current Architecture



```text

Office Endpoints

&nbsp;     |

&nbsp;     v

Identity Server ---- File Server

&nbsp;     |                  |

&nbsp;     +--------+---------+

&nbsp;              |

&nbsp;              v

&nbsp;         Zenith Core

&nbsp;              |

&nbsp;              v

&nbsp;     Central Telemetry

```



The simulated organisation contains:



| Department | Users |

|---|---:|

| Finance | 8 |

| HR | 12 |

| Sales | 15 |

| IT | 12 |

| Office Admin | 3 |

| \*\*Total\*\* | \*\*50\*\* |



\## Implemented Features



\- 50-user simulated corporate environment

\- 64 registered endpoints

\- Department, role and group-based user modelling

\- Role-Based Access Control (RBAC)

\- Identity Server with:

&nbsp; - authentication

&nbsp; - failed-login tracking

&nbsp; - account lockout

&nbsp; - password reset

&nbsp; - session tokens

&nbsp; - server-side endpoint validation

&nbsp; - device-bound sessions

\- File Server with role-aware resource permissions

\- Local JSONL security logging

\- Centralised telemetry through Zenith Core

\- Live terminal telemetry viewer

\- Synthetic behavioural dataset generation

\- Behavioural feature engineering

\- Random Forest classification

\- Logistic Regression comparison

\- Confusion-matrix analysis

\- Zenith-specific security metrics

\- Feature importance, ablation and trusted feature selection



\## Behaviour Classes



Zenith currently classifies behaviour into four categories:



```text

normal

human\_error

suspicious

malicious

```



The synthetic dataset currently contains \*\*10,000 samples\*\*:



| Class | Samples |

|---|---:|

| Normal | 4,000 |

| Human Error | 2,000 |

| Suspicious | 2,000 |

| Malicious | 2,000 |



Synthetic data is used for controlled experimentation and does not represent real-world prevalence.



\## Behavioural Features



Current trusted features include:



\- department

\- role

\- event type

\- hour / off-hours activity

\- failed logins

\- denied resource access

\- unique resources accessed

\- role mismatch

\- device mismatch

\- recent password reset

\- successful recovery after failures

\- department-resource mismatch

\- resource sensitivity

\- recently used endpoints

\- time since previous event

\- repeated resource access

\- resource traversal count



Zenith uses structured security events rather than NLP. These features allow the models to learn behavioural patterns and context.



\## Current ML Results



The current selected-feature baseline removes several highly predictive synthetic proxy features to produce a more defensible test.



\### Random Forest — Selected Features



```text

Accuracy:                 94.85%

Macro F1:                 93.71%

Human Error Escalation:    0.75%

Malicious -> Normal:       0.00%

Malicious -> Suspicious:  18.75%

Suspicious -> Normal:      0.25%

Security Detection:       98.50%

```



\### Logistic Regression — Selected Features



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



\## Zenith-Specific Evaluation



Standard metrics include:



\- accuracy

\- precision

\- recall

\- F1-score

\- confusion matrix



Zenith also measures:



\- \*\*Human Error Escalation Rate\*\* — human error incorrectly classified as suspicious or malicious

\- \*\*Malicious -> Normal Miss Rate\*\* — malicious behaviour incorrectly treated as normal

\- \*\*Malicious -> Suspicious Rate\*\* — malicious behaviour downgraded but still security-relevant

\- \*\*Suspicious -> Normal Miss Rate\*\*

\- \*\*Security Detection Rate\*\* — suspicious or malicious behaviour retained within a security-relevant class



This allows the project to evaluate the operational impact of misclassification rather than relying on accuracy alone.



\## Project Structure



```text

zenith/

├── cloud/

├── data/

│   ├── datasets/

│   └── logs/

├── hq/

│   ├── identity\_server.py

│   ├── file\_server.py

│   ├── telemetry\_viewer.py

│   └── zenith\_core.py

├── models/

│   └── training/

│       └── train\_baseline.py

├── office/

│   ├── finance\_team.py

│   ├── hr\_team.py

│   ├── sales\_team.py

│   ├── it\_team.py

│   ├── office\_admin\_team.py

│   └── office\_endpoint.py

├── simulation/

│   └── behaviour\_generator.py

├── shared/

├── reports/

├── tests/

├── main.py

├── requirements.txt

└── README.md

```



\## Running the Current Prototype



Start the core services:



```powershell

python -m hq.zenith\_core

python -m hq.identity\_server

python -m hq.file\_server

```



Start an Office endpoint:



```powershell

python -m office.office\_endpoint

```



Optional live telemetry:



```powershell

python -m hq.telemetry\_viewer

```



Generate the behavioural dataset:



```powershell

python -m simulation.behaviour\_generator

```



Train and evaluate the baseline models:



```powershell

python -m models.training.train\_baseline

```



\## Current Development Stage



Completed:



\- enterprise simulation

\- authentication and endpoint validation

\- RBAC

\- central telemetry

\- behavioural dataset generation

\- overlapping behaviour scenarios

\- Random Forest and Logistic Regression baselines

\- security-specific metrics

\- feature importance and feature selection



Next:



\- grouped feature-selection experiments

\- true event-sequence modelling

\- dynamically calculated user baselines

\- collective model decision logic

\- adaptive risk scoring

\- response levels and containment

\- simulated attack scenarios

\- lateral movement experiments

\- adversarial testing

\- final research report



\## Technology



\- Python

\- pandas

\- scikit-learn

\- JSON / JSONL

\- TCP sockets

\- Git / GitHub

\- VS Code



\## Status



\*\*Active Development — Research Prototype\*\*



Zenith is not intended for production deployment. Current ML results are based on synthetic behavioural data and are used to evaluate the project methodology, feature design and model behaviour.



---



\*\*Independent Project, 2026–Present\*\*



