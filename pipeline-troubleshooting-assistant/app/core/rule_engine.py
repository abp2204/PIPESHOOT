import json
import re
from typing import List, Dict, Any
import os


class RuleEngine:
    def __init__(self, rules_path: str):
        self.rules_path = rules_path
        self.rules = self._load_rules()

    def _load_rules(self) -> Dict[str, Any]:
        if not os.path.exists(self.rules_path):
            return {}
        with open(self.rules_path, 'r', encoding='utf8') as f:
            return json.load(f)

    def analyze(self, logs: str, config: dict, failed_output: str = "") -> dict:
        matches = []
        for cat in self.rules.get('categories', []):
            cat_matches = []
            for rule in cat.get('matching_rules', []):
                t = rule.get('type')
                if t == 'substring':
                    for phrase in rule.get('phrases', []):
                        if phrase.lower() in logs.lower() or phrase.lower() in (failed_output or '').lower():
                            snippet = self._get_snippet(logs, phrase)
                            cat_matches.append({'rule': rule, 'evidence': snippet})
                elif t == 'regex':
                    for pattern in rule.get('patterns', []):
                        try:
                            m = re.search(pattern, logs) or re.search(pattern, failed_output)
                            if m:
                                snippet = self._get_snippet(logs, m.group(0))
                                cat_matches.append({'rule': rule, 'evidence': snippet})
                        except re.error:
                            continue
                elif t == 'missing_field':
                    field = rule.get('field')
                    if field and not self._deep_get(config, field.split('.')):
                        cat_matches.append({'rule': rule, 'evidence': f"missing config field: {field}"})
                elif t == 'invalid_value':
                    field = rule.get('field')
                    allowed = rule.get('allowed_values', [])
                    val = self._deep_get(config, field.split('.'))
                    if val is not None and allowed and val not in allowed:
                        cat_matches.append({'rule': rule, 'evidence': f"{field}={val}"})
                elif t == 'path_missing':
                    field = rule.get('field')
                    val = self._deep_get(config, field.split('.'))
                    if val and not os.path.exists(val):
                        cat_matches.append({'rule': rule, 'evidence': f"path not found: {val}"})

            if cat_matches:
                confidence = min(0.95, 0.3 + 0.2 * len(cat_matches))
                matches.append({
                    'category_id': cat.get('id'),
                    'category_name': cat.get('name'),
                    'severity': cat.get('severity', 'medium'),
                    'confidence': round(confidence, 2),
                    'evidence': [m['evidence'] for m in cat_matches],
                    'root_causes': cat.get('probable_root_causes', []),
                    'next_steps': cat.get('next_steps', [])
                })

        # sort by severity mapping then confidence
        severity_map = {'critical': 3, 'high': 2, 'medium': 1, 'low': 0}
        matches = sorted(matches, key=lambda m: (-severity_map.get(m['severity'], 1), -m['confidence']))
        result = {'matches': matches, 'top_issue': matches[0] if matches else None}
        return result

    def _deep_get(self, obj: dict, path: List[str]):
        cur = obj
        for p in path:
            if isinstance(cur, dict) and p in cur:
                cur = cur[p]
            else:
                return None
        return cur

    def _get_snippet(self, logs: str, evidence: str, context_lines: int = 2) -> str:
        """Return a small snippet (lines) containing the evidence with a couple lines of context.
        Falls back to returning the evidence itself if no lines are found.
        """
        if not logs:
            return evidence
        lines = logs.splitlines()
        lel = len(lines)
        ev_lower = evidence.strip().lower()
        for i, line in enumerate(lines):
            if ev_lower in line.lower() or (ev_lower and ev_lower in line.lower()):
                start = max(0, i - context_lines)
                end = min(lel, i + context_lines + 1)
                snippet = '\n'.join(lines[start:end])
                return snippet
        # fallback: return short slice of logs around first occurrence
        idx = logs.lower().find(ev_lower)
        if idx >= 0:
            start = max(0, idx - 80)
            end = min(len(logs), idx + len(ev_lower) + 80)
            return logs[start:end]
        return evidence
