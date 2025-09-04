# generator.py
# -*- coding: utf-8 -*-
def generate_code(plan: str) -> str:
    print(f"✍️ [Generator] Generiere Code aus Plan:\n{plan}\n")

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
