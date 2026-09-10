"""Offline-only validation for the frozen MN-004 v5 efficacy contract."""

import json

import mn004_v5

print(json.dumps(mn004_v5.validate_offline(), indent=2))

