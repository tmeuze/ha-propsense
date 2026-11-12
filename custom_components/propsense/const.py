"""Constants for PropSense."""
from __future__ import annotations

from datetime import timedelta

DOMAIN = "propsense"

CONF_RULES = "rules"
CONF_SETTINGS = "settings"

# Assistants whose exposure Home Assistant can manage.
ASSISTANTS = ["conversation", "cloud.alexa", "cloud.google_assistant"]
ASSISTANT_LABELS = {
    "conversation": "Assist",
    "cloud.alexa": "Alexa",
    "cloud.google_assistant": "Google Assistant",
}

SIGNAL_UPDATED = f"{DOMAIN}_updated"

# Registry events arrive in bursts (a label edit touches many entries), so
# apply once after things settle.
DEBOUNCE_SECONDS = 2.0
# State changes can be frequent; rules that select on state re-run at most this
# often (after the quiet period).
STATE_DEBOUNCE_SECONDS = 5.0
# Safety net for anything that changes without a registry event.
RESYNC_INTERVAL = timedelta(hours=1)

ISSUE_TOO_MANY = "too_many_exposed"

# Rules that feed each other (one applies a label another selects on) can chase
# their own tail. If applying changed something this many times within the
# window, applying pauses (reporting only) and a Repairs issue explains why.
OSCILLATION_RUNS = 20
OSCILLATION_WINDOW = 60.0
OSCILLATION_PAUSE = 300.0
ISSUE_OSCILLATING = "rules_oscillating"
