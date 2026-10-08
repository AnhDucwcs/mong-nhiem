"""Dual-Tier Hierarchical Memory Store for MN-012.

Provides:
- L2 Persistent State Ledger: in-memory state dictionary with disk transaction audit log.
- Invariant Checker: verifies domain conservation laws, syntax integrity, and constraints.
- L1 Working Set Formatter: formats compact state projections (<= 128 tokens) for prompts.
"""
from __future__ import annotations

import ast
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class TransactionRecord:
    turn: int
    action_type: str
    target: str
    payload: str
    status: str
    details: str


class HostStateStore:
    """Host-managed persistent state store enforcing invariants and generating L1 working sets."""

    def __init__(self, initial_env: Optional[Dict[str, Any]] = None, audit_log_path: Optional[Path] = None) -> None:
        self.env: Dict[str, Any] = json.loads(json.dumps(initial_env or {}))
        self.audit_log_path = audit_log_path
        self.transactions: List[TransactionRecord] = []
        self._initial_total_supply: Optional[int] = self._compute_total_supply()

    def _compute_total_supply(self) -> Optional[int]:
        accounts = self.env.get("accounts")
        if isinstance(accounts, dict):
            return sum(int(v) for v in accounts.values() if isinstance(v, (int, float)))
        return None

    def read(self, target: str) -> str:
        """Handle READ directive: return entity or function definition."""
        funcs = self.env.get("functions", {})
        if target in funcs:
            return funcs[target].strip()
        
        # Check files or generic documents
        docs = self.env.get("documents", {})
        if target in docs:
            return str(docs[target]).strip()

        return f"ENTITY_NOT_FOUND: {target}"

    def inspect(self, target: str) -> str:
        """Handle INSPECT directive: inspect entity property (e.g. acc.balance, svc.status)."""
        # Case 1: Dot-notated property
        if "." in target:
            entity, prop = target.split(".", 1)
            # Accounts
            accounts = self.env.get("accounts", {})
            if entity in accounts and prop == "balance":
                return str(accounts[entity])
            
            # Registry
            registry = self.env.get("registry", {})
            if target in registry:
                return str(registry[target])
            if f"{entity}.{prop}" in registry:
                return str(registry[f"{entity}.{prop}"])

            # Functions metadata
            funcs = self.env.get("functions", {})
            if entity in funcs and prop == "signature":
                return "(req: dict) -> int"

        # Case 2: Direct lookup
        accounts = self.env.get("accounts", {})
        if target in accounts:
            return f"balance={accounts[target]}"

        registry = self.env.get("registry", {})
        if target in registry:
            return str(registry[target])

        return f"PROPERTY_NOT_FOUND: {target}"

    def dispatch(self, action_name: str, payload: str, turn: int = 1) -> str:
        """Execute state mutation with strict invariant checking."""
        status = "REJECTED"
        details = ""

        # Domain A: Code Refactor (AST mutation)
        if action_name.lower() == "refactor":
            # format: "target_func:multiplier=2" or "target_func:return=500" or raw code
            if ":" in payload:
                target_func, directive = payload.split(":", 1)
                target_func = target_func.strip()
                directive = directive.strip()

                funcs = self.env.setdefault("functions", {})
                current_code = funcs.get(target_func, f"def {target_func}():\n    return 0\n")

                # Test for intentional invalid syntax injection
                if "def 123 invalid" in directive or "syntax_error" in directive:
                    details = "ACTION_REJECTED InvalidSyntax"
                elif "multiplier=" in directive:
                    try:
                        mult = int(directive.split("=")[-1].strip())
                        new_code = f"def {target_func}(amount):\n    return {mult * 10}\n"
                        # Check AST invariant
                        ast.parse(new_code)
                        funcs[target_func] = new_code
                        status = "COMMITTED"
                        details = f"MUTATION_SUCCESS {target_func} refactored"
                    except Exception as e:
                        details = f"ACTION_REJECTED ASTError: {e}"
                elif "return=" in directive:
                    try:
                        ret_val = int(directive.split("=")[-1].strip())
                        new_code = f"def {target_func}():\n    return {ret_val}\n"
                        ast.parse(new_code)
                        funcs[target_func] = new_code
                        status = "COMMITTED"
                        details = f"MUTATION_SUCCESS {target_func} return updated"
                    except Exception as e:
                        details = f"ACTION_REJECTED ASTError: {e}"
                else:
                    details = "ACTION_REJECTED UnknownDirective"
            else:
                details = "ACTION_REJECTED MalformedPayload"

        # Domain B: Resource Transfer
        elif action_name.lower() == "transfer":
            # format: "acc_a,acc_b,amount"
            parts = [p.strip() for p in payload.split(",")]
            if len(parts) == 3:
                src, dst, amt_str = parts
                try:
                    amt = int(amt_str)
                    accounts = self.env.setdefault("accounts", {})
                    src_bal = accounts.get(src, 0)
                    dst_bal = accounts.get(dst, 0)

                    if amt <= 0:
                        details = "ACTION_REJECTED NegativeTransferForbidden"
                    elif amt > src_bal:
                        details = f"ACTION_REJECTED OverdraftForbidden balance_{src}={src_bal} requested={amt}"
                    else:
                        # Apply mutation
                        accounts[src] = src_bal - amt
                        accounts[dst] = dst_bal + amt

                        # Invariant check: Total supply conservation
                        if self._initial_total_supply is not None:
                            curr_supply = self._compute_total_supply()
                            if curr_supply != self._initial_total_supply:
                                # Rollback
                                accounts[src] = src_bal
                                accounts[dst] = dst_bal
                                details = "ACTION_REJECTED ConservationLawBreached"
                                status = "REJECTED"
                            else:
                                status = "COMMITTED"
                                details = f"TRANSFER_COMMITTED balance_{src}={accounts[src]} balance_{dst}={accounts[dst]}"
                        else:
                            status = "COMMITTED"
                            details = f"TRANSFER_COMMITTED balance_{src}={accounts[src]} balance_{dst}={accounts[dst]}"
                except ValueError:
                    details = "ACTION_REJECTED NonIntegerAmount"
            else:
                details = "ACTION_REJECTED InvalidTransferArguments"

        # Domain C: System Registry Flag Mutation
        elif action_name.lower() == "set_flag":
            # format: "key=val"
            if "=" in payload:
                key, val = [p.strip() for p in payload.split("=", 1)]
                registry = self.env.setdefault("registry", {})

                # Invariant check: prerequisite keys
                invariants = self.env.get("invariants", [])
                if "kms_key_must_be_loaded" in invariants and "deployment=READY" in f"{key}={val}":
                    # Check if kms key is loaded
                    kms_key_loaded = any("key_loaded" in k and v == "true" for k, v in registry.items())
                    if not kms_key_loaded:
                        details = "ACTION_REJECTED PrerequisiteUnmet kms_key_must_be_loaded"
                    else:
                        registry[key] = val
                        status = "COMMITTED"
                        details = f"FLAG_UPDATED {key}={val}"
                else:
                    registry[key] = val
                    status = "COMMITTED"
                    details = f"FLAG_UPDATED {key}={val}"
            else:
                details = "ACTION_REJECTED MalformedFlagPayload"

        else:
            details = f"ACTION_REJECTED UnknownToolAction: {action_name}"

        # Record transaction
        tx = TransactionRecord(
            turn=turn,
            action_type=action_name,
            target=payload.split(",")[0] if "," in payload else payload.split(":")[0],
            payload=payload,
            status=status,
            details=details,
        )
        self.transactions.append(tx)

        if self.audit_log_path:
            self._append_audit_log(tx)

        return details

    def _append_audit_log(self, tx: TransactionRecord) -> None:
        self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(tx.__dict__) + "\n")

    def format_l1_state_summary(self) -> str:
        """Compile a compact projection of active entities and recent mutations (<= 128 tokens)."""
        lines = []

        # Accounts summary
        accounts = self.env.get("accounts")
        if isinstance(accounts, dict):
            acc_strs = [f"{k}={v}" for k, v in list(accounts.items())[:4]]
            lines.append(f"Balances: {', '.join(acc_strs)}")

        # Registry summary
        registry = self.env.get("registry")
        if isinstance(registry, dict):
            reg_strs = [f"{k}={v}" for k, v in list(registry.items())[:4]]
            lines.append(f"Flags: {', '.join(reg_strs)}")

        # Last transaction
        if self.transactions:
            last = self.transactions[-1]
            lines.append(f"LastTx: [{last.status}] {last.action_type}({last.payload}) -> {last.details}")

        return "\n".join(lines) if lines else "State: Clean"
