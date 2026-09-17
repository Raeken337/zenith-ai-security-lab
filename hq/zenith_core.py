import json
import socket

from datetime import datetime
from pathlib import Path

from models.runtime.feature_engine import (
    FeatureEngine
)

from models.runtime.inference_engine import (
    ZenithInferenceEngine
)


HOST = "127.0.0.1"

PORT = 5003


CENTRAL_LOG_FILE = Path(
    "data/logs/central_telemetry.jsonl"
)


def ensure_log_directory():
    CENTRAL_LOG_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )


def analyse_event(
    event,
    feature_engine,
    inference_engine
):
    features = (
        feature_engine.process_event(
            event
        )
    )

    assessment = (
        inference_engine.assess(
            features
        )
    )

    return (
        features,
        assessment
    )


def store_event(
    event,
    features=None,
    assessment=None,
    analysis_error=None
):
    ensure_log_directory()

    central_event = {
        **event,

        "zenith_received_at":
            datetime.now().isoformat()
    }

    if features is not None:
        central_event[
            "zenith_features"
        ] = features

    if assessment is not None:
        central_event[
            "zenith_assessment"
        ] = assessment

    if analysis_error is not None:
        central_event[
            "zenith_analysis_error"
        ] = analysis_error

    with CENTRAL_LOG_FILE.open(
        "a",
        encoding="utf-8"
    ) as log_file:
        log_file.write(
            json.dumps(
                central_event
            )
            + "\n"
        )

    print(
        f"Telemetry stored: "
        f"{central_event['event_type']}"
    )

    if assessment is not None:
        print(
            "Zenith classification: "
            f"{assessment['classification']}"
        )

        print(
            "Zenith confidence: "
            f"{assessment['confidence']:.2%}"
        )

        print(
            "Model agreement: "
            f"{assessment['agreement']}"
        )

    return central_event


def process_event(
    event,
    feature_engine,
    inference_engine
):
    try:
        (
            features,
            assessment
        ) = analyse_event(
            event,
            feature_engine,
            inference_engine
        )

        central_event = store_event(
            event,
            features=features,
            assessment=assessment
        )

        response = {
            "received": True,
            "analysed": True,
            "reason": (
                "Telemetry accepted and "
                "analysed by Zenith Core"
            ),
            "classification":
                assessment[
                    "classification"
                ],
            "confidence":
                assessment[
                    "confidence"
                ],
            "agreement":
                assessment[
                    "agreement"
                ]
        }

        return (
            central_event,
            response
        )

    except Exception as error:
        error_message = (
            f"{type(error).__name__}: "
            f"{error}"
        )

        print(
            "Zenith analysis failed: "
            f"{error_message}"
        )

        central_event = store_event(
            event,
            analysis_error=error_message
        )

        response = {
            "received": True,
            "analysed": False,
            "reason": (
                "Telemetry stored, but Zenith "
                "analysis failed"
            ),
            "analysis_error":
                error_message
        }

        return (
            central_event,
            response
        )


def start_zenith_core():
    feature_engine = FeatureEngine()

    inference_engine = (
        ZenithInferenceEngine()
    )

    server_socket = socket.socket(
        socket.AF_INET,
        socket.SOCK_STREAM
    )

    server_socket.bind(
        (HOST, PORT)
    )

    server_socket.listen()

    print(
        f"Zenith Core listening "
        f"on {HOST}:{PORT}"
    )

    print(
        "Feature engine ready."
    )

    print(
        "Random Forest and Logistic "
        "Regression models loaded."
    )

    while True:
        (
            client_socket,
            client_address
        ) = server_socket.accept()

        print(
            "\nTelemetry connection from "
            f"{client_address}"
        )

        try:
            raw_message = (
                client_socket.recv(
                    4096
                ).decode(
                    "utf-8"
                )
            )

            event = json.loads(
                raw_message
            )

            print(
                "Event received: "
                f"{event.get('event_type', 'unknown')}"
            )

            print(
                "Source device: "
                f"{event.get('source_device', 'unknown')}"
            )

            (
                central_event,
                response
            ) = process_event(
                event,
                feature_engine,
                inference_engine
            )

            client_socket.sendall(
                json.dumps(
                    response
                ).encode(
                    "utf-8"
                )
            )

        finally:
            client_socket.close()


if __name__ == "__main__":
    start_zenith_core()