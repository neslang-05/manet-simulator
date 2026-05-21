"""
experiment_manager.py — Experiment History Manager
Save, load, compare, and re-run past experiments.
"""

import json
import os
import datetime
from pathlib import Path
from typing import Optional


class ExperimentManager:
    """Manages experiment history stored as JSON records."""

    def __init__(self, history_dir: str = None):
        if history_dir is None:
            history_dir = str(Path(__file__).parent.parent / "outputs" / "history")
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.history_dir / "experiments.json"
        self._experiments = self._load_all()

    def _load_all(self) -> list:
        if self.history_file.exists():
            try:
                with open(self.history_file) as f:
                    return json.load(f)
            except Exception:
                return []
        return []

    def _save_all(self):
        with open(self.history_file, 'w') as f:
            json.dump(self._experiments, f, indent=2)

    def save(self, result: dict) -> str:
        """Save an experiment result and return its ID."""
        entry = {
            "id":          result.get("run_id", datetime.datetime.now().strftime("%Y%m%d_%H%M%S")),
            "timestamp":   datetime.datetime.now().isoformat(),
            "protocol":    result.get("config", {}).get("protocol", "Unknown"),
            "numNodes":    result.get("config", {}).get("numNodes", 0),
            "simTime":     result.get("config", {}).get("simTime", 0),
            "success":     result.get("success", False),
            "config":      result.get("config", {}),
            "output_wsl":  result.get("output_wsl", ""),
            "output_win":  result.get("output_win", ""),
        }
        self._experiments.insert(0, entry)
        self._save_all()
        return entry["id"]

    def get_all(self) -> list:
        """Return all experiments (newest first)."""
        return list(self._experiments)

    def get_by_id(self, exp_id: str) -> Optional[dict]:
        for e in self._experiments:
            if e["id"] == exp_id:
                return e
        return None

    def delete(self, exp_id: str) -> bool:
        before = len(self._experiments)
        self._experiments = [e for e in self._experiments if e["id"] != exp_id]
        if len(self._experiments) < before:
            self._save_all()
            return True
        return False

    def compare(self, id1: str, id2: str) -> dict:
        """Return a comparison dict between two experiments."""
        e1 = self.get_by_id(id1)
        e2 = self.get_by_id(id2)
        if not e1 or not e2:
            return {}
        return {
            "exp1": e1,
            "exp2": e2,
            "diff": {
                k: {"exp1": e1["config"].get(k), "exp2": e2["config"].get(k)}
                for k in set(list(e1["config"].keys()) + list(e2["config"].keys()))
                if e1["config"].get(k) != e2["config"].get(k)
            }
        }
