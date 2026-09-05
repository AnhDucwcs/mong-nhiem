"""Offline-only validation for the frozen MN-004 v4 contract."""
import json

import mn004_v4

print(json.dumps(mn004_v4.validate_offline(), indent=2))
