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
            if src_path:
                break

    # If still not found, allow grading from root (no src)
    if not src_path:
        src_path = student_path

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
    # If still not found, try parent of src_path (for cases like grading Model/ directly)
    if not main_file:
        parent_path = os.path.dirname(src_path)
        main_file = find_path_insensitive(parent_path, "Main.java", look_for_dir=False)
        if not main_file:
            for root, dirs, files in os.walk(parent_path):
                if "Main.java" in files:
                    main_file = os.path.join(root, "Main.java")
                    break
    if not main_file:
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

    # Private/protected fields (Player)
    # Accept both private and protected for encapsulation
        # Numeric fields (Player) - lenient: any int/long/double/float field
        numeric_count = len(re.findall(r'(int|long|double|float)\s+\w+(?:\s*=\s*[^;]+)?;', player_content))
        if numeric_count >= 3:
            s_score += 5
            details.append(f"[OK] Numeric fields in Player ({numeric_count} found) (+5)")
        else:
            details.append(f"[X] Numeric fields in Player (found {numeric_count})")

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
    if "interface ShowDetail" in showdetail_content:
        if re.search(r'(public\s+)?void\s+showDetail\(\)\s*;', showdetail_content):
            i_score += 5
            details.append("[OK] Interface ShowDetail defined correctly (+5)")
        else:
            i_score += 2
            details.append("[~] Interface ShowDetail ada, tapi method showDetail() belum sesuai. (+2)")
    else:
        details.append("[~] Interface ShowDetail belum ditemukan. Coba pastikan nama dan deklarasi sudah benar.")

    # Implements (partial credit)
    # More robust: allow implements ... ShowDetail with any whitespace/comments/newlines in between
    implements_showdetail_pattern = r'implements[\s\S]{0,100}?ShowDetail'
    if re.search(implements_showdetail_pattern, player_content, re.IGNORECASE):
        i_score += 5
        details.append("[OK] Player sudah mengimplementasikan ShowDetail. Bagus! (+5)")
    elif re.search(r'implements', player_content, re.IGNORECASE):
        i_score += 2
        details.append("[~] Player mengimplementasikan interface lain, pastikan ShowDetail juga diimplementasikan. (+2)")
    else:
        details.append("[~] Player belum mengimplementasikan ShowDetail. Coba pastikan deklarasi: 'implements ShowDetail'.")

    if re.search(implements_showdetail_pattern, score_content, re.IGNORECASE):
        i_score += 5
        details.append("[OK] Score sudah mengimplementasikan ShowDetail. (+5)")
    elif re.search(r'implements', score_content, re.IGNORECASE):
        i_score += 2
        details.append("[~] Score mengimplementasikan interface lain, pastikan ShowDetail juga diimplementasikan. (+2)")
    else:
        details.append("[~] Score belum mengimplementasikan ShowDetail. Pastikan deklarasi sudah benar.")

    total_score += (i_score / 15) * W_INTERFACE

    # 3. Logika Constructor (20%)
    c_score = 0
    # Player: UUID.randomUUID()
    if re.search(r'UUID\s*\.\s*randomUUID\s*\(', player_content):
        c_score += 5
        details.append("[OK] Player: UUID.randomUUID() sudah digunakan untuk ID. (+5)")
    elif re.search(r'UUID', player_content):
        c_score += 2
        details.append("[~] Player: UUID sudah digunakan, tapi belum randomUUID(). (+2)")
    else:
        details.append("[~] Player: UUID generation belum ditemukan. Coba gunakan UUID.randomUUID() untuk membuat ID unik.")

    # Player: LocalDateTime.now()
    if re.search(r'LocalDateTime\s*\.\s*now\s*\(', player_content):
        c_score += 5
        details.append("[OK] Player: LocalDateTime.now() sudah digunakan untuk createdAt. (+5)")
    elif re.search(r'LocalDateTime', player_content):
        c_score += 2
        details.append("[~] Player: LocalDateTime sudah digunakan, tapi belum .now(). (+2)")
    else:
        details.append("[~] Player: LocalDateTime.now() belum ditemukan. Pastikan createdAt diisi dengan waktu saat pembuatan objek.")

    # Player: Init 0
    # Allow explicit init to 0 OR just reliance on default values (it's Java)
    # We check if there are numeric fields defined.
    if re.search(r'(private|protected)\s+(int|long|double|float)\s+\w+(\s*=\s*0)?\s*;', player_content):
        c_score += 5
        details.append("[OK] Player: Field numerik sudah ada dan diinisialisasi (default 0 atau eksplisit). (+5)")
    elif re.search(r'(int|long|double|float)\s+\w+', player_content):
        c_score += 2
        details.append("[~] Player: Field numerik ada, tapi belum diinisialisasi 0 atau belum private/protected. (+2)")
    else:
        details.append("[~] Player: Field numerik belum ditemukan atau belum diinisialisasi. Pastikan ada highScore, totalCoins, totalDistance.")

    # Score: Constructor assignments
    # Look for 'this.x = x' OR 'x = val' inside constructor
    assign_count = len(re.findall(r'(this\.)?\w+\s*=\s*\w+;', score_content))
    if assign_count >= 3:
        c_score += 5
        details.append("[OK] Score: Constructor assignments found (+5)")
    elif assign_count > 0:
        c_score += 2
        details.append(f"[~] Score: Constructor assignment ditemukan {assign_count} kali, sebaiknya minimal 3. (+2)")
    else:
        details.append("[~] Score: Constructor assignments belum ditemukan.")

    total_score += (c_score / 20) * W_CONSTRUCTOR
    # Bonus effort jika sudah mengerjakan mayoritas bagian (>=60% instruksi)
    instruksi_terpenuhi = 0
    if i_score > 7: instruksi_terpenuhi += 1
    if c_score > 7: instruksi_terpenuhi += 1
    if s_score > 10: instruksi_terpenuhi += 1
    # Method (lihat addCoins, addDistance, updateHighScore, showDetail)
    method_count = 0
    if re.search(r'addCoins', player_content, re.IGNORECASE): method_count += 1
    if re.search(r'addDistance', player_content, re.IGNORECASE): method_count += 1
    if re.search(r'updateHighScore', player_content, re.IGNORECASE): method_count += 1
    if re.search(r'showDetail', player_content, re.IGNORECASE): method_count += 1
    if method_count >= 3: instruksi_terpenuhi += 1
    if instruksi_terpenuhi >= 3:
        total_score += 5
        details.append("[+] Bonus effort: Sudah mengerjakan mayoritas instruksi, tetap semangat! (+5)")

    # 4. Logika Method (30%)
    m_score = 0
    # updateHighScore: lenient, accept assignment to highScore
    if re.search(r'highScore\s*=\s*\w+', player_content, re.IGNORECASE):
        m_score += 10
        details.append("[OK] updateHighScore sudah ada. (+10)")
        if not re.search(r'if\s*\(\s*\w+\s*>\s*highScore', player_content):
            details.append("[~] Saran: Tambahkan pengecekan 'if (newScore > highScore)' agar hanya update jika skor baru lebih tinggi.")
    else:
        details.append("[~] updateHighScore belum ditemukan. Pastikan ada logika update hanya jika skor baru lebih tinggi dari highScore.")

    # addCoins: += OR = ... + ...
    if (re.search(r'\+=', player_content) or re.search(r'\w+\s*=\s*\w+\s*\+\s*\w+', player_content)) and re.search(r'addCoins', player_content, re.IGNORECASE):
        m_score += 5
        details.append("[OK] addCoins sudah benar menambah koin. (+5)")
    else:
        details.append("[~] addCoins belum ditemukan atau belum menambah koin dengan benar. Pastikan menggunakan '+=' atau penjumlahan.")

    # addDistance: += OR = ... + ...
    if (re.search(r'\+=', player_content) or re.search(r'\w+\s*=\s*\w+\s*\+\s*\w+', player_content)) and re.search(r'addDistance', player_content, re.IGNORECASE):
        m_score += 5
        details.append("[OK] addDistance sudah benar menambah jarak. (+5)")
    else:
        details.append("[~] addDistance belum ditemukan atau belum menambah jarak dengan benar. Pastikan menggunakan '+=' atau penjumlahan.")

    # showDetail (case-insensitive)
    if re.search(r'def\s+showdetail|void\s+showdetail', player_content, re.IGNORECASE) or re.search(r'void\s+ShowDetail', player_content):
        if re.search(r'System\.out\.println', player_content):
            m_score += 10
            details.append("[OK] showDetail implementation found (+10)")
        else:
            details.append("[X] showDetail method found but no output")
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
    # Accept both showDetail() and ShowDetail() calls, case-insensitive
    if re.search(r'\bshowDetail\s*\(', main_content, re.IGNORECASE):
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
    if total_score >= 60:
        print("Catatan: Sudah mengerjakan sebagian besar instruksi, tinggal lengkapi beberapa bagian agar lebih sempurna!")
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
