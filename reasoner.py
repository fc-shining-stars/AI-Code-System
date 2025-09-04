# reasoner.py
# -*- coding: utf-8 -*-
def plan_code(context: str) -> str:
    print(f"💡 [Reasoner] Erstelle Plan aus Kontext:\n{context}\n")

    plan = """Plan:
- auth.py: Login-Funktion
- main.py: Startpunkt Admin-Panel
- outputs/: Code speichern
- Tests: pytest-Struktur
"""
    return plan
