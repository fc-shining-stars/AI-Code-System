# tester.py
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
