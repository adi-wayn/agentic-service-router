import json
import os
from dataclasses import dataclass
from typing import List, Optional, Any, Dict

@dataclass
class GroundTruthTargets:
    expected_template: Optional[str]
    expected_routing_action: str
    expected_real_urgency: str
    expected_missing_fields: List[str]

def load_ground_truth(filepath: str = "data/eval_cases.json") -> Dict[str, GroundTruthTargets]:
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Evaluation cases file not found at {filepath}")
        
    with open(filepath, "r") as f:
        data = json.load(f)
        
    cases = {}
    for req_id, item in data.items():
        cases[req_id] = GroundTruthTargets(
            expected_template=item["expected_template"],
            expected_routing_action=item["expected_routing_action"],
            expected_real_urgency=item["expected_real_urgency"],
            expected_missing_fields=item.get("expected_missing_fields", [])
        )
    return cases

class AssertionTracker:
    def __init__(self):
        self.total = 0
        self.passed = 0
        self.failed = 0
        self.failures = []

    def assert_equals(self, case_id: str, field_name: str, expected: Any, actual: Any):
        self.total += 1
        if expected == actual:
            self.passed += 1
        else:
            self.failed += 1
            self.failures.append(f"[{case_id}] {field_name} mismatch: Expected '{expected}', got '{actual}'")

    def print_summary(self):
        print(f"--- Assertion Summary ---")
        print(f"Total: {self.total}, Passed: {self.passed}, Failed: {self.failed}")
        for f in self.failures:
            print(f"  - {f}")
