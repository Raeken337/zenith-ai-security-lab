# Zenith Roadmap

**Project:** Zenith — Adaptive AI-Driven Cyber Defence Research Prototype  
**Status:** Active Development  
**Focus:** Behavioural ML, adaptive risk scoring, lateral-movement prevention, false-positive reduction, proportional automated response

---

## 1. Main Infrastructure / Topology Foundation ✅

- HQ environment established
- Office environment established
- Cloud directory reserved
- Shared reusable classes/utilities created
- TCP-based local service communication working

---

## 2. Corporate Workforce Simulation ✅

- 50 simulated employees created
- Finance: 8
- HR: 12
- Sales: 15
- IT: 12
- Office Admin: 3
- 64 endpoints assigned across desktops, laptops and mobiles
- Work hours, roles, departments and groups defined

---

## 3. Role-Based Access Control Model ✅

- Finance role access
- HR role access
- Sales role access
- IT role access
- Office Admin role access
- Department-level access separated from role-level access
- Fail-closed handling for unknown roles/resources

---

## 4. Identity Server Integration ✅

- All 50 users loaded dynamically
- Authentication working
- Session-token generation
- Failed-login tracking
- Account lockout
- Password reset / unlock
- Role and department context included in sessions
- Working-hour information included

---

## 5. Endpoint Trust / Validation ✅

- HQ endpoint registry
- Server-side device validation
- User/device ownership checks
- Registered Office endpoint checks
- Device-bound sessions
- File Server validates session/device relationship

---

## 6. File Server Repurpose + RBAC Enforcement ✅

- Resources expanded across Finance / HR / Sales / Admin / IT
- Role permissions enforced dynamically
- Human-friendly resource input
- Case-insensitive resource entry
- Resource normalisation
- Clean employee-facing output
- Access grants/denials centrally logged

---

## 7. Reusable Office Endpoint Abstraction ✅

- One client represents any Office employee/device
- User selection
- Assigned-device selection
- Login
- Password reset
- Resource access
- User/device switching
- Human-readable terminal responses

---

## 8. Centralised Telemetry System ✅

- Local JSONL logs
- Zenith Core telemetry receiver
- Central telemetry log
- Login events
- Password resets
- File-access events
- Role/device/department context
- Local logging survives Zenith Core outage

---

## 9. Live Telemetry Viewer ✅

- Stored telemetry view
- Live monitoring
- Analyst-readable event formatting
- Machine-readable telemetry preserved separately

---

## 10. Behavioural Dataset Generator V1 ✅

- Synthetic labelled behaviour generation
- 10,000-row dataset
- Normal behaviour
- Human error
- Suspicious behaviour
- Malicious behaviour
- Controlled class overlap added

---

## 11. Behavioural Feature Engineering V1 ✅

Current features include:

- Department
- Role
- Event type
- Hour
- Failed logins
- Denied accesses
- Unique resources
- Off-hours activity
- Role mismatch
- Device mismatch
- Recent password reset
- Successful recovery
- Department-resource mismatch
- Resource sensitivity
- Recently used endpoints
- Time since previous event
- Repeated-resource activity
- Resource traversal

---

## 12. Baseline Machine-Learning Models ✅

- Random Forest
- Logistic Regression
- Shared train/test split
- One-hot encoding
- Standard scaling
- Reusable scikit-learn pipelines

---

## 13. Standard Model Evaluation ✅

- Accuracy
- Precision
- Recall
- F1
- Macro F1
- Weighted F1
- Confusion matrices

---

## 14. Zenith-Specific Security Metrics ✅

- Human-error escalation rate
- Malicious → Normal miss rate
- Malicious → Suspicious rate
- Suspicious → Normal miss rate
- Security detection rate

---

## 15. Realistic Behavioural-Overlap Experiment ✅

- Removed cartoonishly obvious attack boundaries
- Introduced legitimate off-hours behaviour
- Human mistakes overlap with suspicious behaviour
- Malicious behaviour can mimic legitimate activity
- Exposed meaningful false positives / false negatives

---

## 16. Feature-Importance Analysis ✅

- Random Forest importance extraction
- Identified high-impact features
- Detected synthetic proxy / answer-sheet problem
- Historical deviation and baseline risk flagged as overly label-dependent in current implementation

---

## 17. Feature-Ablation Analysis ✅

- Individual contextual features tested
- Impact on security detection / false escalation evaluated
- Demonstrated that feature importance ≠ trustworthy evidence

---

## 18. Trusted Feature Selection ✅

Current trusted baseline excludes:

- Synthetic `sequence_pattern`
- Synthetic `historical_user_deviation`
- Synthetic `user_baseline_risk`

Current strongest trusted model:

**Random Forest — Selected Features**

Current selected-feature results:

- Accuracy: **94.85%**
- Macro F1: **93.71%**
- Human-error escalation: **0.75%**
- Malicious → Normal: **0.00%**
- Security detection: **98.50%**

---

## 19. Group Feature-Ablation Experiment ⏳ NEXT

Test evidence groups rather than random individual columns:

- Authentication / recovery context
- Identity / role context
- Resource context
- Endpoint context
- Temporal context
- Traversal context

Goal:

Identify the **smallest useful feature set** that preserves high detection while minimising false-positive escalation.

---

## 20. Finalise V1 Trusted Feature Set ⏳

- Remove genuinely redundant features
- Keep domain-important features even if raw importance is low
- Establish final Static Zenith V1 input schema
- Freeze baseline experiment results

---

## 21. True Event-Sequence Simulator ⏳

Move from isolated synthetic rows toward actual ordered activity:

```text
login failure
→ login failure
→ password reset
→ login success
→ legitimate resource access
```

versus:

```text
login success
→ restricted resource
→ another restricted resource
→ remote admin probe
→ identity admin probe
```

---

## 22. Real Recovery-Sequence Features ⏳

Replace synthetic recovery indicators with features derived from preceding telemetry:

- Failure → reset → success
- Failure → success without reset
- Repeated denial sequence
- Post-recovery normality
- Repeated privilege probing

---

## 23. Historical User Baseline Engine ⏳

Calculate genuine user history instead of generating it from labels:

- Normal work hours
- Usual endpoint count
- Typical resources
- Normal denied-access rate
- Normal event frequency
- Normal privilege range

---

## 24. Historical User Deviation Scoring ⏳

Reintroduce `historical_user_deviation`, but calculate it from actual history.

Example:

```text
Jake normally:
1–3 Finance resources
08:00–17:00
PC-FIN-01

Current:
8 resources
22:30
multiple departments

→ calculated deviation score
```

---

## 25. Real User Baseline Risk ⏳

Derive risk from genuine operating context.

Example:

- IT Manager → naturally broader privilege baseline
- Finance Assistant → naturally narrower baseline

This prevents high-privilege legitimate users from automatically appearing malicious.

---

## 26. Real Sequence-Pattern Classification ⏳

Reintroduce `sequence_pattern`, but infer it from actual events rather than assigning it from the class label.

---

## 27. Re-Evaluate Random Forest + Logistic Regression ⏳

Compare:

- Trusted static features
- Real history-aware features
- Real sequence-aware features

Key question:

**Do contextual features reduce false positives without damaging threat detection?**

---

## 28. Model Disagreement / Agreement Layer ⏳

Begin using model outputs collectively.

Example:

```text
Random Forest → Suspicious 0.72
Logistic Regression → Human Error 0.55
```

Zenith records:

- Agreement level
- Confidence gap
- Class disagreement
- Security disagreement

---

## 29. Add a Genuinely Unique Third Model ⏳

Not “another classifier because more models = better.”

Most likely:

- Anomaly-detection model for deviation from normal behaviour

Later possibly:

- Sequence-aware model

Goal:

```text
RF → nonlinear behavioural patterns
LR → linear risk relationships
Anomaly model → deviation from personal baseline
```

---

## 30. Collective Zenith Decision Engine ⏳

Combine independent evidence into one security judgement.

Inputs:

- RF probabilities
- LR probabilities
- Anomaly score
- Sequence context
- User history
- Role/resource context

Outputs:

- Predicted behaviour class
- Confidence
- Risk score
- Recommended response

---

## 31. Adaptive Risk Score ⏳

Produce a normalised score, for example:

```text
Risk: 68 / 100
Classification: Suspicious
Confidence: Moderate
```

Risk should not simply equal model probability.

---

## 32. Proportionate Response Levels ⏳

Proposed system:

```text
0 = No Action
1 = Observe
2 = Flag / Recommend
3 = Soft Intervention
4 = Endpoint Isolation
5 = Critical Containment
```

---

## 33. False-Positive-Aware Response Safeguards ⏳

- Low model agreement → avoid aggressive automation
- Recovery sequence → reduce risk
- Legitimate privileged role → contextual adjustment
- Uncertain classification → analyst review
- Historical conformity → reduce unnecessary escalation

---

## 34. Zenith Node Integration ⏳

Repurpose `office/zenith_node.py` into the Office-side enforcement/monitoring component.

Eventually:

- Local telemetry handling
- Communication with Zenith Core
- Endpoint response execution
- Resilience if HQ connection fails

---

## 35. Normal Workday Simulation ⏳

Generate complete Office workdays across all 50 employees:

- Logins
- Resource access
- Lunch/break periods
- Resets
- Mistakes
- Managers crossing departments
- IT admin behaviour
- Occasional off-hours work

---

## 36. Human-Error Experiment Suite ⏳

Scenarios:

- Forgotten password
- Repeated typo
- Wrong resource
- Legitimate late working
- Temporary endpoint change
- Manager accessing multiple departments
- IT administrator performing unusual but legitimate maintenance

---

## 37. Rule-Based Defensive Baseline ⏳

Build a simple non-ML comparison system:

- Threshold rules
- Repeated-login rules
- Off-hours flags
- Privilege mismatch rules

Needed so final research can compare ML against a simpler defensive approach.

---

## 38. Static ML Zenith Baseline ⏳

Freeze a non-adaptive ML configuration for experimental comparison.

---

## 39. First Simulated Attack Suite ⏳ 🔥

- Stolen Finance credentials
- Compromised normal employee
- Privilege probing
- Resource enumeration
- Abnormal endpoint switching
- Repeated authentication attempts
- Restricted-resource traversal

---

## 40. Lateral Movement Simulation ⏳

Model movement from:

- Compromised endpoint
- User account
- Shared service
- Internal resource
- Elevated account
- HQ/core systems

---

## 41. Compromised Privileged IT Account Experiment ⏳

Important challenge because legitimate IT activity already looks dangerous.

Test whether Zenith distinguishes:

- Normal administration
- Compromised administration
- Attempts to cross protected Zenith boundaries

---

## 42. Containment Implementation ⏳

- Block resource access
- Invalidate sessions
- Isolate endpoint
- Lock compromised account
- Flag user
- Restrict privileged operations

---

## 43. Lateral Movement Experiment ⏳

Compare:

```text
No Zenith
vs
Rule-Based Defence
vs
Static ML Zenith
vs
Adaptive Zenith
```

---

## 44. Containment Metrics ⏳

- Systems reached
- Privileged systems reached
- Resources accessed
- Resources denied
- Time to detection
- Time to containment
- Spread prevented
- Containment success

---

## 45. Operational-Impact Metrics ⏳

- Legitimate users disrupted
- Endpoints unnecessarily isolated
- Sessions unnecessarily terminated
- Analyst review volume
- False containment rate
- Human-error escalation
- Recovery time

---

## 46. Adversarial Attack Testing ⏳

Make the attacker actively try to fool Zenith:

- Slow-and-low activity
- Legitimate working hours
- Correct credentials
- Correct registered device
- Legitimate resources first
- Delayed probing
- Mimicking historical behaviour
- Distributed resource probing
- Threshold avoidance

---

## 47. Zenith-Specific Adversarial Testing ⏳

Attack the defensive system itself:

- Telemetry gaps
- Incomplete events
- Manipulated behavioural sequences
- Model disagreement exploitation
- Compromised IT user attempting Zenith access
- Protected ML/config boundary testing

---

## 48. Concept Drift / Adaptability Experiment ⏳

Change legitimate employee behaviour over time:

- Role change
- Promotion
- New working hours
- New endpoint
- Changing responsibilities

Test whether adaptive Zenith learns without treating every legitimate change as malicious.

---

## 49. Final Model / Control Comparison ⏳

Evaluate all defensive configurations using the same scenarios and datasets.

---

## 50. Experiment Result Storage ⏳

Add structured outputs under:

```text
data/experiments/
reports/
```

Store:

- Metrics
- Predictions
- Attack results
- Containment outcomes
- Experiment configs

---

## 51. Visualisation / Graphs ⏳

Produce:

- Confusion matrices
- Model comparison chart
- Security detection chart
- False-escalation chart
- Feature-group impact
- Attack spread graph
- Detection/containment latency
- Operational-disruption comparison

---

## 52. Technical Research Report ⏳

Sections:

- Research question
- Literature/background
- Architecture
- Methodology
- Synthetic-data limitations
- Feature engineering
- ML methodology
- Experimental design
- Attack scenarios
- Results
- False-positive analysis
- Limitations
- Conclusions
- Future work

---

## 53. Project Structure Cleanup ⏳

Finalise something around:

```text
zenith/
├── attacks/
├── cloud/
├── data/
│   ├── datasets/
│   ├── experiments/
│   └── logs/
├── hq/
├── models/
│   ├── evaluation/
│   ├── saved_models/
│   └── training/
├── office/
├── reports/
├── simulation/
├── shared/
├── tests/
├── README.md
├── ROADMAP.md
├── main.py
└── requirements.txt
```

---

## 54. One-Command Environment Launcher ⏳

Stop requiring approximately 46 terminals 😭

Goal:

```powershell
python main.py
```

launches the required services.

---

## 55. Testing / Reproducibility Cleanup ⏳

- Deterministic experiment seeds
- Unit tests
- Integration tests
- Experiment configs
- Requirements cleanup
- Clean first-run setup

---

## 56. README Finalisation 🔄

README exists ✅

Later update with:

- Final architecture
- Final metrics
- Actual attack results
- Graphs
- Limitations
- Demo instructions

---

## 57. GitHub Release-Ready Cleanup ⏳

- Clear commit history
- Remove unused files
- Clean sample logs
- Sensible `.gitignore`
- Screenshots
- Architecture diagram
- Licence if desired
- Reproducible instructions

---

## 58. Demo Recording ⏳

Short demo showing:

- Normal employee activity
- Telemetry appearing
- Suspicious behaviour
- Zenith classification
- Risk escalation
- Containment during an attack

---

## 59. Final GitHub Publication ⏳

Repository becomes recruiter/research ready.

---

## 60. LinkedIn / CV Project Release ⏳

Final summary can credibly describe Zenith as:

> **Zenith — Adaptive AI-Driven Cyber Defence Research Prototype**  
> Designed and developed a simulated 50-user enterprise security environment combining authentication, RBAC, endpoint trust, centralised telemetry and behavioural machine learning. Evaluated Random Forest and Logistic Regression classifiers using security-specific metrics, feature ablation and trusted feature selection, before extending the system toward adaptive risk scoring, lateral-movement detection and proportional automated containment.

---

# Current Position

```text
Trusted feature selection ✅
           ↓
GROUP FEATURE ABLATION   ← YOU ARE HERE
           ↓
Final V1 feature set
           ↓
Real sequences/history
           ↓
Collective ML decision
           ↓
Adaptive risk engine
           ↓
Response system
           ↓
ATTACKS 🔥
           ↓
Lateral movement experiments
           ↓
Adversarial testing
           ↓
Report + GitHub release
```
