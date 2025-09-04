# main.py
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
