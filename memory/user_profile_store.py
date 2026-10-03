import json
import os

PROFILE_PATH = os.path.join(os.path.dirname(__file__), "user_profile.json")
DEFAULTS = {"home_currency": "USD"}


def get_profile() -> dict:
    if not os.path.exists(PROFILE_PATH):
        return dict(DEFAULTS)
    with open(PROFILE_PATH) as f:
        return {**DEFAULTS, **json.load(f)}


def update_profile(**kwargs) -> dict:
    profile = get_profile()
    profile.update(kwargs)
    with open(PROFILE_PATH, "w") as f:
        json.dump(profile, f, indent=2)
    return profile
