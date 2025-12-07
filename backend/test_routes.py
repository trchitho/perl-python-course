"""Test if routes are registered"""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app

app = create_app()

print("\n" + "=" * 60)
print("Registered Routes")
print("=" * 60)

for rule in app.url_map.iter_rules():
    if 'auth' in rule.rule:
        print(f"{rule.methods} {rule.rule}")

print("=" * 60)
