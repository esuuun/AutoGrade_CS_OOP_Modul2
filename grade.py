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

def grade_student(student_path):
    print(f"Grading {student_path}...")
    
    src_path = os.path.join(student_path, "src")
    if not os.path.exists(src_path):
        # Try to find src deeper
        for root, dirs, files in os.walk(student_path):
            if "src" in dirs:
                src_path = os.path.join(root, "src")
                break
    
    if not os.path.exists(src_path):
        print(f"  Error: 'src' folder not found in {student_path}")
        return 0

    model_path = os.path.join(src_path, "Model")
    
    # Files
    player_file = os.path.join(model_path, "Player.java")
    score_file = os.path.join(model_path, "Score.java")
    showdetail_file = os.path.join(model_path, "ShowDetail.java")
    main_file = os.path.join(src_path, "Main.java")

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
        details.append("[OK] Model package exists (+5)")
    else:
        details.append("[X] Model package missing")

    # Package declaration
    if "package Model;" in player_content and "package Model;" in score_content:
        s_score += 5
        details.append("[OK] Package declaration correct (+5)")
    else:
        details.append("[X] Package declaration missing/incorrect")

    # Private fields (Player)
    # Check for private fields. We expect at least 3 private fields.
    private_count = len(re.findall(r'private\s+\w+\s+\w+;', player_content))
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
    if "interface ShowDetail" in showdetail_content and "void showDetail();" in showdetail_content:
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
    if re.search(r'=\s*0;', player_content):
        c_score += 5
        details.append("[OK] Player: Fields initialized to 0 (+5)")
    else:
        details.append("[X] Player: Initialization to 0 missing")

    # Score: Constructor assignments
    # Look for 'this.x = x' pattern
    if len(re.findall(r'this\.\w+\s*=\s*\w+;', score_content)) >= 3:
        c_score += 5
        details.append("[OK] Score: Constructor assignments found (+5)")
    else:
        details.append("[X] Score: Constructor assignments missing/insufficient")

    total_score += (c_score / 20) * W_CONSTRUCTOR

    # 4. Logika Method (30%)
    m_score = 0
    # updateHighScore: if (new > old)
    if re.search(r'if\s*\(\s*\w+\s*>\s*\w+\s*\)', player_content):
        m_score += 10
        details.append("[OK] updateHighScore logic (if new > old) found (+10)")
    else:
        details.append("[X] updateHighScore logic missing")

    # addCoins: +=
    if "+=" in player_content and "addCoins" in player_content:
        m_score += 5
        details.append("[OK] addCoins logic (+=) found (+5)")
    else:
        details.append("[X] addCoins logic missing")

    # addDistance: +=
    if "+=" in player_content and "addDistance" in player_content:
        m_score += 5
        details.append("[OK] addDistance logic (+=) found (+5)")
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
    if main_content.count("new Player") >= 2 and main_content.count("new Score") >= 3:
        main_score += 5
        details.append("[OK] Main: Objects instantiated (2 Players, 3 Scores) (+5)")
    else:
        details.append("[X] Main: Insufficient object instantiation")

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
