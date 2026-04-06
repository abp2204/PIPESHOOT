from app.core.rule_engine import RuleEngine
import os
import json

def test_load_rules_and_match():
    root = os.path.dirname(os.path.dirname(__file__))
    rules_path = os.path.join(root, 'app', 'rules', 'rules.json')
    engine = RuleEngine(rules_path)
    logs = "ERROR FileNotFoundError: [Errno 2] No such file or directory: '/data/input/events.csv'"
    config = {"input": {}}
    res = engine.analyze(logs, config)
    assert res['matches'], 'Should find at least one match for missing file'
    ids = [m['category_id'] for m in res['matches']]
    assert 'missing_file' in ids or 'missing_param' in ids

def test_invalid_value_rule():
    root = os.path.dirname(os.path.dirname(__file__))
    rules_path = os.path.join(root, 'app', 'rules', 'rules.json')
    engine = RuleEngine(rules_path)
    config = {'runtime': {'mode': 'weirdmode'}}
    res = engine.analyze('', config)
    ids = [m['category_id'] for m in res['matches']]
    assert 'invalid_value' in ids
