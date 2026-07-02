#!/usr/bin/env python3
"""Rebuild everything the site serves, in one command.

Runs the engine (docs/index.html + docs/board.json) then the rich prototype
(docs/prototype.html). This is the single entry point the scheduled GitHub
Action calls every few hours, and what you run locally to refresh by hand:

    python build_all.py
"""
import subprocess, sys, os

ROOT = os.path.dirname(os.path.abspath(__file__))
for script in ["build.py", "_prototype_data.py", "_prototype_page.py"]:
    print("== running", script)
    subprocess.check_call([sys.executable, os.path.join(ROOT, script)])
print("== done: docs/index.html, docs/board.json, docs/prototype.html")
