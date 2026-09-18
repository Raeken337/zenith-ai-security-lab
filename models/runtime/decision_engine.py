SECURITY_CLASSES = {
    "suspicious",
    "malicious"
}


CLASSIFICATION_POINTS = {
    "normal": 0,
    "human_error": 1,
    "suspicious": 3,
    "malicious": 5
}


PRIVILEGED_ROLES = {
    "IT Manager",
    "Senior Systems Administrator",
    "Systems Administrator",
    "Network Administrator",
    "Security Administrator",
    "Identity and Access Administrator",
    "Endpoint Administrator"
}


ELEVATED_ROLES = {
    "Finance Manager",
    "HR Manager",
    "Sales Manager",
    "Office Manager",
    "Deputy Office Manager",
    "Site Administrator",
    "Senior IT Support Engineer",
    "IT Support Engineer",
    "Monitoring and Logging Analyst"
}


SEVERITY_NAMES = {
    0: "informational",
    1: "low",
    2: "guarded",
    3: "elevated",
    4: "high",
    5: "critical"
}


IMPORTANCE_NAMES = {
    0: "routine",
    1: "low",
    2: "moderate",
    3: "high",
    4: "critical"
}


RESPONSE_NAMES = {
    0: "record_only",
    1: "observe",
    2: "alert_and_review",
    3: "soft_intervention",
    4: "containment",
    5: "critical_containment"
}


PROTOCOLS_BY_LEVEL = {
    0: [
        "record_event"
    ],

    1: [
        "record_event",
        "increase_monitoring"
    ],

    2: [
        "record_event",
        "increase_monitoring",
        "open_incident",
        "alert_administrator"
    ],

    3: [
        "record_event",
        "increase_monitoring",
        "open_incident",
        "alert_administrator",
        "require_step_up_authentication",
        "invalidate_active_sessions"
    ],

    4: [
        "record_event",
        "increase_monitoring",
        "open_incident",
        "alert_administrator",
        "require_step_up_authentication",
        "invalidate_active_sessions",
        "lock_account",
        "isolate_endpoint"
    ],

    5: [
        "record_event",
        "increase_monitoring",
        "open_incident",
        "alert_administrator",
        "require_step_up_authentication",
        "invalidate_active_sessions",
        "lock_account",
        "isolate_endpoint",
        "protect_target_resource",
        "restrict_lateral_movement",
        "send_urgent_administrator_alert"
    ]
}


class ZenithDecisionEngine:
    def __init__(self):
        self.incidents = {}

    def reset(self):
        self.incidents.clear()

    def reset_user(self, username):
        self.incidents.pop(
            username,
            None
        )

    def decide(
        self,
        event,
        features,
        assessment,
        existing_actions=None
    ):
        self._validate_inputs(
            event,
            features,
            assessment
        )

        username = event["username"]

        state = self._get_incident_state(
            username
        )

        classification = assessment[
            "classification"
        ]

        confidence = float(
            assessment["confidence"]
        )

        state["event_count"] += 1

        if classification in SECURITY_CLASSES:
            state[
                "security_assessment_count"
            ] += 1

            state[
                "consecutive_security_assessments"
            ] += 1

        else:
            state[
                "consecutive_security_assessments"
            ] = 0

        supplied_actions = set(
            existing_actions or []
        )

        state["existing_actions"] = (
            supplied_actions
        )

        privilege = self._resolve_privilege(
            features["role"]
        )

        event_importance = (
            self._calculate_event_importance(
                event,
                features
            )
        )

        severity_points, reasoning = (
            self._calculate_severity_points(
                event=event,
                features=features,
                assessment=assessment,
                state=state,
                privilege=privilege
            )
        )

        severity_level = (
            self._severity_from_points(
                severity_points
            )
        )

        response_level = severity_level

        response_level, safeguards = (
            self._apply_safeguards(
                response_level=response_level,
                classification=classification,
                confidence=confidence,
                features=features,
                assessment=assessment
            )
        )

        recommended_protocols = [
            protocol
            for protocol
            in PROTOCOLS_BY_LEVEL[
                response_level
            ]
            if protocol not in state[
                "existing_actions"
            ]
        ]

        state[
            "highest_severity_level"
        ] = max(
            state[
                "highest_severity_level"
            ],
            severity_level
        )

        state[
            "highest_response_level"
        ] = max(
            state[
                "highest_response_level"
            ],
            response_level
        )

        state["last_classification"] = (
            classification
        )

        model_reasoning = (
            self._describe_model_evidence(
                assessment
            )
        )

        full_reasoning = (
            model_reasoning
            + reasoning
        )

        return {
            "classification":
                classification,

            "confidence":
                confidence,

            "event_importance": {
                "level":
                    event_importance,

                "name":
                    IMPORTANCE_NAMES[
                        event_importance
                    ]
            },

            "severity_points":
                severity_points,

            "incident_severity": {
                "level":
                    severity_level,

                "name":
                    SEVERITY_NAMES[
                        severity_level
                    ]
            },

            "response_level":
                response_level,

            "response_name":
                RESPONSE_NAMES[
                    response_level
                ],

            "reasoning":
                full_reasoning,

            "safeguards":
                safeguards,

            "recommended_protocols":
                recommended_protocols,

            "privilege_context":
                privilege,

            "incident_state": {
                "username":
                    username,

                "event_count":
                    state[
                        "event_count"
                    ],

                "security_assessment_count":
                    state[
                        "security_assessment_count"
                    ],

                "consecutive_security_assessments":
                    state[
                        "consecutive_security_assessments"
                    ],

                "highest_severity_level":
                    state[
                        "highest_severity_level"
                    ],

                "highest_response_level":
                    state[
                        "highest_response_level"
                    ],

                "last_classification":
                    state[
                        "last_classification"
                    ],

                "existing_actions":
                    sorted(
                        state[
                            "existing_actions"
                        ]
                    )
            }
        }

    def _get_incident_state(
        self,
        username
    ):
        if username not in self.incidents:
            self.incidents[username] = {
                "event_count": 0,
                "security_assessment_count": 0,
                "consecutive_security_assessments": 0,
                "highest_severity_level": 0,
                "highest_response_level": 0,
                "last_classification": None,
                "existing_actions": set()
            }

        return self.incidents[
            username
        ]

    def _resolve_privilege(
        self,
        role
    ):
        if role in PRIVILEGED_ROLES:
            return {
                "level": 2,
                "name": "privileged",
                "role": role
            }

        if role in ELEVATED_ROLES:
            return {
                "level": 1,
                "name": "elevated",
                "role": role
            }

        return {
            "level": 0,
            "name": "standard",
            "role": role
        }

    def _calculate_event_importance(
        self,
        event,
        features
    ):
        importance = 0

        event_type = event.get(
            "event_type"
        )

        if event_type in {
            "login_failure",
            "file_access_denied"
        }:
            importance += 1

        if event_type == "account_locked":
            importance += 2

        sensitivity = features[
            "resource_sensitivity"
        ]

        if sensitivity >= 3:
            importance += 1

        if sensitivity >= 5:
            importance += 1

        if features[
            "department_resource_mismatch"
        ]:
            importance += 1

        if features[
            "device_mismatch"
        ]:
            importance += 2

        if features[
            "role_mismatch"
        ]:
            importance += 2

        if features[
            "denied_accesses_10m"
        ] >= 2:
            importance += 1

        if features[
            "resource_traversal_count"
        ] >= 2:
            importance += 1

        return min(
            importance,
            4
        )

    def _calculate_severity_points(
        self,
        event,
        features,
        assessment,
        state,
        privilege
    ):
        classification = assessment[
            "classification"
        ]

        points = CLASSIFICATION_POINTS[
            classification
        ]

        reasoning = []

        failed_logins = features[
            "failed_logins_10m"
        ]

        denied_accesses = features[
            "denied_accesses_10m"
        ]

        traversal_count = features[
            "resource_traversal_count"
        ]

        sensitivity = features[
            "resource_sensitivity"
        ]

        if failed_logins >= 2:
            points += 1

            reasoning.append(
                f"{failed_logins} failed logins "
                "occurred in the recent window."
            )

        if denied_accesses == 1:
            points += 1

            reasoning.append(
                "One denied resource request "
                "has been observed."
            )

        elif denied_accesses == 2:
            points += 2

            reasoning.append(
                "Two denied resource requests "
                "show repeated probing."
            )

        elif denied_accesses >= 3:
            points += 3

            reasoning.append(
                f"{denied_accesses} denied resource "
                "requests show persistent probing."
            )

        if traversal_count == 2:
            points += 1

            reasoning.append(
                "Activity has moved across "
                "multiple resources."
            )

        elif traversal_count >= 3:
            points += 2

            reasoning.append(
                f"Activity has traversed "
                f"{traversal_count} resources."
            )

        if sensitivity >= 4:
            points += 1

            reasoning.append(
                f"The current resource has high "
                f"sensitivity ({sensitivity}/5)."
            )

        if sensitivity >= 5:
            points += 1

            reasoning.append(
                "The current resource is a "
                "critical administrative resource."
            )

        if features[
            "department_resource_mismatch"
        ]:
            points += 1

            reasoning.append(
                "The resource belongs to another "
                "department."
            )

        if features["device_mismatch"]:
            points += 2

            reasoning.append(
                "The source endpoint is not assigned "
                "to this user."
            )

        if features["role_mismatch"]:
            points += 1

            reasoning.append(
                "The supplied identity context does "
                "not match the known user role."
            )

        if features[
            "recent_endpoints_used"
        ] > 1:
            points += 1

            reasoning.append(
                "The user recently operated from "
                "multiple endpoints."
            )

        if features[
            "repeated_resource_accesses"
        ] >= 2:
            points += 1

            reasoning.append(
                "The same resources were repeatedly "
                "accessed."
            )

        if (
            features["off_hours"]
            and (
                failed_logins > 0
                or denied_accesses > 0
                or features["device_mismatch"]
            )
        ):
            points += 1

            reasoning.append(
                "The concerning activity occurred "
                "outside expected working hours."
            )

        if features[
            "successful_recovery"
        ]:
            if denied_accesses == 0:
                points -= 1

                reasoning.append(
                    "Successful authentication recovery "
                    "reduces the immediate concern."
                )

            elif denied_accesses >= 2:
                reasoning.append(
                    "Earlier authentication recovery "
                    "does not explain the continued "
                    "resource probing."
                )

        if (
            privilege["level"] > 0
            and classification in SECURITY_CLASSES
            and (
                sensitivity >= 4
                or features["device_mismatch"]
            )
        ):
            points += privilege["level"]

            reasoning.append(
                f"The {privilege['name']} account "
                "increases the potential impact, "
                "but privilege alone is not treated "
                "as suspicious."
            )

        if (
            state[
                "consecutive_security_assessments"
            ] >= 2
        ):
            points += 1

            reasoning.append(
                "Multiple consecutive events have "
                "been classified as security-relevant."
            )

        return (
            max(points, 0),
            reasoning
        )

    def _severity_from_points(
        self,
        points
    ):
        if points == 0:
            return 0

        if points == 1:
            return 1

        if points <= 3:
            return 2

        if points <= 5:
            return 3

        if points <= 8:
            return 4

        return 5

    def _apply_safeguards(
        self,
        response_level,
        classification,
        confidence,
        features,
        assessment
    ):
        safeguards = []

        def cap_response(
            maximum,
            explanation
        ):
            nonlocal response_level

            if response_level > maximum:
                response_level = maximum

                safeguards.append(
                    explanation
                )

        if classification == "normal":
            cap_response(
                1,
                "Normal classifications cannot "
                "trigger intervention or containment."
            )

        if classification == "human_error":
            cap_response(
                2,
                "Human-error classifications cannot "
                "directly trigger containment."
            )

            if (
                features[
                    "denied_accesses_10m"
                ] <= 1
                and not features[
                    "device_mismatch"
                ]
                and not features[
                    "role_mismatch"
                ]
            ):
                cap_response(
                    1,
                    "A human-error event without "
                    "repeated denials or identity "
                    "mismatches remains observation-only."
                )

        if classification == "suspicious":
            cap_response(
                4,
                "Suspicious activity may recommend "
                "containment, but not the highest "
                "critical response."
            )

        if confidence < 0.55:
            cap_response(
                2,
                "Low model confidence limits the "
                "response to alert and review."
            )

        if assessment["agreement"] == "low":
            cap_response(
                2,
                "Low model agreement prevents "
                "automatic containment."
            )

        if assessment[
            "security_disagreement"
        ]:
            cap_response(
                2,
                "The models disagree on whether the "
                "activity is security-relevant."
            )

        if (
            features[
                "successful_recovery"
            ]
            and features[
                "denied_accesses_10m"
            ] == 0
        ):
            cap_response(
                1,
                "Successful recovery without later "
                "probing remains observation-only."
            )

        strong_containment_evidence = (
            (
                features[
                    "denied_accesses_10m"
                ] >= 3
                and features[
                    "resource_traversal_count"
                ] >= 3
                and features[
                    "resource_sensitivity"
                ] >= 4
            )
            or (
                features["device_mismatch"]
                and features[
                    "resource_sensitivity"
                ] >= 4
            )
            or (
                classification == "malicious"
                and confidence >= 0.70
                and assessment[
                    "agreement"
                ] == "high"
            )
        )

        if (
            response_level >= 4
            and not strong_containment_evidence
        ):
            cap_response(
                3,
                "Containment requires stronger "
                "corroborating behavioural evidence."
            )

        return (
            response_level,
            safeguards
        )

    def _describe_model_evidence(
        self,
        assessment
    ):
        reasoning = [
            (
                "The weighted model assessment is "
                f"{assessment['classification']} "
                f"with "
                f"{assessment['confidence']:.1%} "
                "confidence."
            )
        ]

        models = assessment.get(
            "models",
            {}
        )

        random_forest = models.get(
            "random_forest"
        )

        logistic_regression = models.get(
            "logistic_regression"
        )

        if random_forest is not None:
            reasoning.append(
                "Random Forest classified the event "
                f"as {random_forest['classification']} "
                f"with "
                f"{random_forest['confidence']:.1%} "
                "confidence."
            )

        if logistic_regression is not None:
            reasoning.append(
                "Logistic Regression classified the "
                f"event as "
                f"{logistic_regression['classification']} "
                f"with "
                f"{logistic_regression['confidence']:.1%} "
                "confidence."
            )

        return reasoning

    def _validate_inputs(
        self,
        event,
        features,
        assessment
    ):
        if not event.get("username"):
            raise ValueError(
                "Decision event requires a username."
            )

        required_features = {
            "role",
            "failed_logins_10m",
            "denied_accesses_10m",
            "off_hours",
            "role_mismatch",
            "device_mismatch",
            "successful_recovery",
            "department_resource_mismatch",
            "resource_sensitivity",
            "recent_endpoints_used",
            "repeated_resource_accesses",
            "resource_traversal_count"
        }

        missing_features = (
            required_features
            - set(features)
        )

        if missing_features:
            raise ValueError(
                "Decision features are missing: "
                f"{sorted(missing_features)}"
            )

        required_assessment = {
            "classification",
            "confidence",
            "agreement",
            "security_disagreement"
        }

        missing_assessment = (
            required_assessment
            - set(assessment)
        )

        if missing_assessment:
            raise ValueError(
                "Model assessment is missing: "
                f"{sorted(missing_assessment)}"
            )

        if assessment[
            "classification"
        ] not in CLASSIFICATION_POINTS:
            raise ValueError(
                "Unsupported model classification: "
                f"{assessment['classification']}"
            )