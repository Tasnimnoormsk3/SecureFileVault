
import os
import json
from datetime import datetime


# --------------------------------------------------
# AUDIT LOG STORAGE
# --------------------------------------------------

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

AUDIT_DIR = os.path.join(
    BASE_DIR,
    "audit_logs"
)

AUDIT_FILE = os.path.join(
    AUDIT_DIR,
    "security_audit.log"
)


# --------------------------------------------------
# CREATE AUDIT DIRECTORY
# --------------------------------------------------

def ensure_audit_log():

    os.makedirs(
        AUDIT_DIR,
        exist_ok=True
    )

    if not os.path.exists(
        AUDIT_FILE
    ):

        with open(
            AUDIT_FILE,
            "w",
            encoding="utf-8"
        ):
            pass


# --------------------------------------------------
# WRITE SECURITY EVENT
# --------------------------------------------------

def log_event(
    action,
    status="SUCCESS",
    file_path=None,
    details=None
):

    ensure_audit_log()

    timestamp = datetime.now().astimezone().isoformat(
        timespec="seconds"
    )

    # Only record filename, not full path
    filename = None

    if file_path:
        filename = os.path.basename(
            file_path
        )

    event = {
        "timestamp": timestamp,
        "action": action,
        "status": status,
        "file": filename,
        "details": details
    }

    with open(
        AUDIT_FILE,
        "a",
        encoding="utf-8"
    ) as log_file:

        log_file.write(
            json.dumps(event)
            + "\n"
        )


# --------------------------------------------------
# READ ACTIVITY LOG
# --------------------------------------------------

def get_audit_log_text():

    ensure_audit_log()

    lines = []

    with open(
        AUDIT_FILE,
        "r",
        encoding="utf-8"
    ) as log_file:

        for line in log_file:

            line = line.strip()

            if not line:
                continue

            try:

                event = json.loads(
                    line
                )

                timestamp = event.get(
                    "timestamp",
                    "Unknown time"
                )

                action = event.get(
                    "action",
                    "UNKNOWN"
                )

                status = event.get(
                    "status",
                    "UNKNOWN"
                )

                filename = event.get(
                    "file"
                )

                details = event.get(
                    "details"
                )

                display_line = (
                    f"{timestamp} | "
                    f"{action} | "
                    f"{status}"
                )

                if filename:

                    display_line += (
                        f" | {filename}"
                    )

                if details:

                    display_line += (
                        f" | {details}"
                    )

                lines.append(
                    display_line
                )

            except json.JSONDecodeError:

                lines.append(
                    "Invalid audit log entry"
                )

    if not lines:

        return "No security activity has been recorded yet."

    return "\n".join(
        lines
    )