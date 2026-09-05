"""Offline-only validator for the frozen MN-004 v3 contract."""
import json

import mn004_v3

print(json.dumps(mn004_v3.validate_offline(), indent=2))
