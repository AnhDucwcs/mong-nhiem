#!/usr/bin/env python3
"""Validate MN-004 authority, evaluator, inventory, and tokenizer preflight without completion requests."""
from __future__ import annotations

import argparse
from pathlib import Path

import mn004


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--base-url")
    parser.add_argument("--model", choices=("llama-3.2-3b", "qwen3-4b"))
    args = parser.parse_args()
    definition = mn004.validate_definition()
    mn004.validate_evaluator_fixtures()
    frozen_failures = mn004.validate_frozen_failure_diagnostics()
    print(f"Validated authority and evaluator; frozen prior-target diagnostics={frozen_failures}")
    if not args.inventory:
        if args.base_url or args.model:
            raise mn004.ContractError("inventory reconstruction requires --inventory, --base-url, and --model")
        return
    if not args.base_url or not args.model:
        raise mn004.ContractError("inventory reconstruction requires --inventory, --base-url, and --model")
    inventory = mn004.load_json(args.inventory)
    client = mn004.ServerClient(args.base_url, definition["models"][args.model]["chat_template_kwargs"])
    mn004.validate_inventory(inventory, client, definition)
    preflight = mn004.preflight_inventory(client, inventory, args.model, definition)
    print(f"Validated inventory {inventory['inventory_fingerprint']} for {args.model}: {preflight['status']}")
    if preflight["status"] != "feasible":
        raise SystemExit(2)


if __name__ == "__main__":
    main()
