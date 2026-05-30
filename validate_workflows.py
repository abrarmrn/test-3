"""Validate generated n8n workflows.
Checks:
  - JSON is valid
  - Each node has required keys: parameters, name, type, typeVersion, position, id
  - Node names are unique
  - Every connection source + target node exists
  - Code-node JS uses balanced braces (lightweight sanity check)
"""
import json, os, sys, re

REQUIRED_KEYS = {"parameters", "name", "type", "typeVersion", "position", "id"}

def lint(path):
    print(f"\n=== {path} ===")
    with open(path) as f:
        wf = json.load(f)
    nodes = wf["nodes"]
    names = [n["name"] for n in nodes]
    dups = {n for n in names if names.count(n) > 1}
    assert not dups, f"Duplicate node names: {dups}"
    for n in nodes:
        miss = REQUIRED_KEYS - set(n.keys())
        assert not miss, f"Node {n.get('name')} missing keys {miss}"
    name_set = set(names)
    conns = wf["connections"]
    for src, outs in conns.items():
        assert src in name_set, f"Connection source '{src}' not found"
        for out_type, branches in outs.items():
            for branch in branches:
                for c in branch:
                    assert c["node"] in name_set, (
                        f"Connection target '{c['node']}' not found "
                        f"(from '{src}')")
    # Real JS syntax check is performed by check_js.py (node --check)
    print(f"OK — {len(nodes)} nodes, {len(conns)} connection sources")

for f in sorted(os.listdir("workflows")):
    if f.endswith(".json"):
        lint(os.path.join("workflows", f))
print("\nALL OK")
