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
# Safety net for anything that changes without a registry event.
RESYNC_INTERVAL = timedelta(hours=1)

ISSUE_TOO_MANY = "too_many_exposed"
