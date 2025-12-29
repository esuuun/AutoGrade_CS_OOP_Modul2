import os
import sys
import glob
import re

# Configuration
# Weights
W_STRUCTURE = 20
W_INTERFACE = 15
W_CONSTRUCTOR = 20
W_METHOD = 30
W_MAIN = 15

def find_student_folders(root_dir):
    return [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d)) and d != "GradingSystem"]

def read_file_content(path):
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except:
        return ""

def check_regex(content, pattern, flags=0):
    return bool(re.search(pattern, content, flags))

def find_path_insensitive(root, name, look_for_dir=True):
    if not os.path.exists(root):
        return None
    for item in os.listdir(root):
        if item.lower() == name.lower():
            full_path = os.path.join(root, item)
            if look_for_dir and os.path.isdir(full_path):
                return full_path
            elif not look_for_dir and os.path.isfile(full_path):
                return full_path
    return None

def grade_student(student_path):
    print(f"Grading {student_path}...")
    
    src_path = find_path_insensitive(student_path, "src", look_for_dir=True)
    if not src_path:
        # Try to find src deeper
        for root, dirs, files in os.walk(student_path):
            for d in dirs:
                if d.lower() == "src":
                    src_path = os.path.join(root, d)
                    break
            if src_path: break
    
    if not src_path:
        print(f"  Error: 'src' folder not found in {student_path}")
        return 0

    model_path = find_path_insensitive(src_path, "Model", look_for_dir=True)
    if not model_path:
         # Fallback: maybe they didn't use a package folder, or named it differently?
         # Let's try to find Player.java to locate the model folder
         for root, dirs, files in os.walk(src_path):
             if "Player.java" in files:
                 model_path = root
                 break
    
    if not model_path:
        model_path = os.path.join(src_path, "Model") # Default for error reporting

    # Files
    player_file = find_path_insensitive(model_path, "Player.java", look_for_dir=False) or os.path.join(model_path, "Player.java")
    score_file = find_path_insensitive(model_path, "Score.java", look_for_dir=False) or os.path.join(model_path, "Score.java")
    showdetail_file = find_path_insensitive(model_path, "ShowDetail.java", look_for_dir=False) or os.path.join(model_path, "ShowDetail.java")
    
    # Main usually in src or src/Main
    main_file = find_path_insensitive(src_path, "Main.java", look_for_dir=False)
    if not main_file:
         for root, dirs, files in os.walk(src_path):
             if "Main.java" in files:
                 main_file = os.path.join(root, "Main.java")
                 break
    if not main_file: main_file = os.path.join(src_path, "Main.java")

    player_content = read_file_content(player_file)
    score_content = read_file_content(score_file)
    showdetail_content = read_file_content(showdetail_file)
    main_content = read_file_content(main_file)

    total_score = 0
    details = []

    # 1. Verifikasi Struktur & Encapsulation (20%)
    s_score = 0
    # Package Model
    if os.path.exists(model_path):
        s_score += 5
        details.append(f"[OK] Model package exists at {os.path.basename(model_path)} (+5)")
    else:
        details.append("[X] Model package missing")

    # Package declaration
    # Allow 'package Model;' or 'package model;' or 'package com.example.model;'
    if re.search(r'package\s+[\w\.]*model;', player_content, re.IGNORECASE) and re.search(r'package\s+[\w\.]*model;', score_content, re.IGNORECASE):
        s_score += 5
        details.append("[OK] Package declaration correct (+5)")
    else:
        details.append("[X] Package declaration missing/incorrect")

    # Private fields (Player)
    # Check for private fields. We expect at least 3 private fields.
    # Regex updated to handle inline initialization: private Type name = val;
    private_count = len(re.findall(r'private\s+\w+\s+\w+(?:\s*=\s*[^;]+)?;', player_content))
    if private_count >= 3:
        s_score += 5
        details.append(f"[OK] Encapsulation (Private fields) in Player ({private_count} found) (+5)")
    else:
        details.append(f"[X] Encapsulation issues in Player (found {private_count} private fields)")

    # UML Types (UUID, LocalDateTime)
    if "UUID" in player_content and "LocalDateTime" in player_content:
        s_score += 5
        details.append("[OK] UML Types (UUID, LocalDateTime) used (+5)")
    else:
        details.append("[X] UML Types missing (UUID or LocalDateTime)")

    total_score += (s_score / 20) * W_STRUCTURE

    # 2. Implementasi Interface (15%)
    i_score = 0
    # ShowDetail interface
    # Allow public void showDetail(); or void showDetail();
    if "interface ShowDetail" in showdetail_content and re.search(r'(public\s+)?void\s+showDetail\(\)\s*;', showdetail_content):
        i_score += 5
        details.append("[OK] Interface ShowDetail defined correctly (+5)")
    else:
        details.append("[X] Interface ShowDetail missing or incorrect")

    # Implements
    if "implements ShowDetail" in player_content:
        i_score += 5
        details.append("[OK] Player implements ShowDetail (+5)")
    else:
        details.append("[X] Player does not implement ShowDetail")

    if "implements ShowDetail" in score_content:
        i_score += 5
        details.append("[OK] Score implements ShowDetail (+5)")
    else:
        details.append("[X] Score does not implement ShowDetail")

    total_score += (i_score / 15) * W_INTERFACE

    # 3. Logika Constructor (20%)
    c_score = 0
    # Player: UUID.randomUUID()
    if "UUID.randomUUID()" in player_content:
        c_score += 5
        details.append("[OK] Player: UUID.randomUUID() used (+5)")
    elif "UUID.fromString" in player_content:
        c_score += 2 # Partial credit for trying
        details.append("[~] Player: UUID.fromString used instead of randomUUID (+2)")
    else:
        details.append("[X] Player: UUID generation missing")

    # Player: LocalDateTime.now()
    if "LocalDateTime.now()" in player_content:
        c_score += 5
        details.append("[OK] Player: LocalDateTime.now() used (+5)")
    else:
        details.append("[X] Player: LocalDateTime.now() missing")

    # Player: Init 0
    # Allow explicit init to 0 OR just reliance on default values (it's Java)
    # We check if there are numeric fields defined.
    if re.search(r'private\s+(int|long|double|float)\s+\w+(\s*=\s*0)?\s*;', player_content):
        c_score += 5
        details.append("[OK] Player: Numeric fields present (default 0 or explicit) (+5)")
    else:
        details.append("[X] Player: Numeric fields missing")

    # Score: Constructor assignments
    # Look for 'this.x = x' OR 'x = val' inside constructor
    if len(re.findall(r'(this\.)?\w+\s*=\s*\w+;', score_content)) >= 3:
        c_score += 5
        details.append("[OK] Score: Constructor assignments found (+5)")
    else:
        details.append("[X] Score: Constructor assignments missing/insufficient")

    total_score += (c_score / 20) * W_CONSTRUCTOR

    # 4. Logika Method (30%)
    m_score = 0
    # updateHighScore: if (new > old) OR Math.max
    # Updated regex to allow 'this.field' (dots in variable names)
    if re.search(r'if\s*\(\s*[\w\.]+\s*>\s*[\w\.]+\s*\)', player_content) or "Math.max" in player_content:
        m_score += 10
        details.append("[OK] updateHighScore logic found (+10)")
    else:
        details.append("[X] updateHighScore logic missing")

    # addCoins: += OR = ... + ...
    if ("+=" in player_content or re.search(r'\w+\s*=\s*\w+\s*\+\s*\w+', player_content)) and "addCoins" in player_content:
        m_score += 5
        details.append("[OK] addCoins logic found (+5)")
    else:
        details.append("[X] addCoins logic missing")

    # addDistance: += OR = ... + ...
    if ("+=" in player_content or re.search(r'\w+\s*=\s*\w+\s*\+\s*\w+', player_content)) and "addDistance" in player_content:
        m_score += 5
        details.append("[OK] addDistance logic found (+5)")
    else:
        details.append("[X] addDistance logic missing")

    # showDetail
    if "System.out.println" in player_content and "showDetail" in player_content:
        m_score += 10
        details.append("[OK] showDetail implementation found (+10)")
    else:
        details.append("[X] showDetail implementation missing")

    total_score += (m_score / 30) * W_METHOD

    # 5. Eksekusi Main & Output (15%)
    main_score = 0
    # Instantiation
    if "new Player" in main_content and "new Score" in main_content:
        main_score += 5
        details.append("[OK] Main: Objects instantiated (+5)")
    else:
        details.append("[X] Main: Object instantiation missing")

    # Update State
    if "updateHighScore" in main_content and "addCoins" in main_content:
        main_score += 5
        details.append("[OK] Main: State updates called (+5)")
    else:
        details.append("[X] Main: State updates missing")

    # Final Output
    if "showDetail" in main_content:
        main_score += 5
        details.append("[OK] Main: showDetail called (+5)")
    else:
        details.append("[X] Main: showDetail missing")

    total_score += (main_score / 15) * W_MAIN

    # Print Report
    print("\n" + "="*40)
    print(f"REPORT FOR: {os.path.basename(student_path)}")
    print("="*40)
    for line in details:
        print(line)
    print("-" * 40)
    print(f"TOTAL SCORE: {total_score:.2f} / 100")
    print("="*40 + "\n")

    return total_score

def main():
    root_dir = ".." 
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]

    if not os.path.exists(root_dir):
        print(f"Error: The specified path does not exist: {root_dir}")
        return

    # Check if the root_dir itself is a student project (contains src)
    if os.path.isdir(os.path.join(root_dir, "src")):
        print(f"Detected single student project at {root_dir}")
        score = grade_student(root_dir)
        print("\nFinal Scores Summary:")
        print(f"{os.path.basename(root_dir)}: {score:.2f}")
        return

    students = find_student_folders(root_dir)
    print(f"Found {len(students)} student folders.")
    
    results = {}
    for student in students:
        full_path = os.path.join(root_dir, student)
        score = grade_student(full_path)
        results[student] = score

    print("\nFinal Scores Summary:")
    for student, score in results.items():
        print(f"{student}: {score:.2f}")

if __name__ == "__main__":
    main()
