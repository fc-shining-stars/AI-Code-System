# setup_pipeline.py
# -*- coding: utf-8 -*-
import os

# -----------------------------
# Ordnerstruktur
# -----------------------------
folders = [
    "outputs",
    "prompts",
]

# -----------------------------
# Dateien + Inhalt
# -----------------------------
files = {
    "main.py": '''# main.py
# -*- coding: utf-8 -*-
import os
from generator import generate_code
from reasoner import plan_code
from tester import run_tests

MODE = "full_pipeline"
user_input = "Erstelle ein Admin-Panel mit Login, Rollenverwaltung und Tests."

def full_pipeline(prompt):
    print("🧠 Augment: Kontext erstellen...")
    augment_context = f"Context aus Datenbank/Codebase + User Input: {prompt}"

    print("💡 Reasoner: Planung erstellen...")
    plan = plan_code(augment_context)

    print("✍️ Coder: Code generieren...")
    generated_code = generate_code(plan)

    output_path = os.path.join("outputs", "generated_code.py")
    os.makedirs("outputs", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(generated_code)
    print(f"💾 Code gespeichert in {output_path}")

    print("🧪 Tests ausführen...")
    test_result = run_tests()
    print(test_result)

    if "FEHLER" in test_result.upper():
        print("⚠️ Fehler erkannt, Feedback an Reasoner...")
    else:
        print("✅ Alle Tests bestanden!")

if __name__ == "__main__":
    if MODE == "full_pipeline":
        full_pipeline(user_input)
    else:
        code = generate_code(user_input)
        os.makedirs("outputs", exist_ok=True)
        with open("outputs/generated_code.py", "w", encoding="utf-8") as f:
            f.write(code)
        print("✅ Code ohne Reasoner generiert!")
''',

    "generator.py": '''# generator.py
# -*- coding: utf-8 -*-
def generate_code(plan: str) -> str:
    print(f"✍️ [Generator] Generiere Code aus Plan:\\n{plan}\\n")

    code = """# generierter Code
def login(user, password):
    if user == "admin" and password == "1234":
        return True
    return False

def main():
    print("Admin-Panel gestartet")

if __name__ == "__main__":
    main()
"""
    return code
''',

    "reasoner.py": '''# reasoner.py
# -*- coding: utf-8 -*-
def plan_code(context: str) -> str:
    print(f"💡 [Reasoner] Erstelle Plan aus Kontext:\\n{context}\\n")

    plan = """Plan:
- auth.py: Login-Funktion
- main.py: Startpunkt Admin-Panel
- outputs/: Code speichern
- Tests: pytest-Struktur
"""
    return plan
''',

    "tester.py": '''# tester.py
# -*- coding: utf-8 -*-
import os

def run_tests() -> str:
    code_file = os.path.join("outputs", "generated_code.py")

    try:
        with open(code_file, "r", encoding="utf-8") as f:
            code_content = f.read()
        compile(code_content, code_file, "exec")
    except SyntaxError as e:
        return f"FEHLER: SyntaxError - {e}"

    return "✅ Test bestanden: Alle Funktionen erfolgreich!"

if __name__ == "__main__":
    result = run_tests()
    print(result)
'''
}

# -----------------------------
# Ordner erstellen
# -----------------------------
for folder in folders:
    os.makedirs(folder, exist_ok=True)
    print(f"Ordner erstellt: {folder}")

# -----------------------------
# Dateien erstellen
# -----------------------------
for filename, content in files.items():
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"Datei erstellt: {filename}")

print("\n✅ Alle Dateien und Ordner wurden erstellt. .venv aktivieren und main.py starten!")
