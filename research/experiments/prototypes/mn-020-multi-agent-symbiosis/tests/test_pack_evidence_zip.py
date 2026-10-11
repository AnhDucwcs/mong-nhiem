"""Unit tests for Standard Library Zip Evidence Packaging Engine."""
import json
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from pack_evidence_zip import EvidenceZipPacker


def test_zip_packaging_and_inspection():
    with tempfile.TemporaryDirectory() as tmp_dir:
        run_path = Path(tmp_dir)
        audit_path = run_path / "audit_logs"
        audit_path.mkdir()

        # Create sample audit logs
        for i in range(5):
            log_f = audit_path / f"CASE-{i:03d}_arm3_audit.json"
            log_f.write_text(json.dumps({"case_id": f"CASE-{i:03d}", "status": "PASS", "turn": i}), encoding="utf-8")

        # 1. Pack into zip
        res = EvidenceZipPacker.pack_audit_logs(run_path, remove_loose_files=True)
        assert res["file_count"] == 5
        assert Path(res["archive_path"]).exists()
        assert len(res["sha256"]) == 64
        assert not audit_path.exists()  # Loose files pruned

        # 2. Inspect file without extraction
        data = EvidenceZipPacker.inspect_archive_file(res["archive_path"], "CASE-002_arm3_audit.json")
        assert data["case_id"] == "CASE-002"
        assert data["status"] == "PASS"

        # 3. List archived files
        file_list = EvidenceZipPacker.list_archived_files(res["archive_path"])
        assert len(file_list) == 5
        assert "audit_logs/CASE-000_arm3_audit.json" in file_list
