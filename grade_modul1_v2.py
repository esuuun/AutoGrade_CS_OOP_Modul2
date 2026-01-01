import os
import sys
import glob
import re

# Configuration
# Weights (Total 100)
W_STRUCTURE = 20
W_VEHICLE_TYPE = 10
W_VEHICLE = 30
W_CUSTOMER = 30
W_MAIN = 10

def find_student_folders(root_dir):
    return [d for d in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, d)) and d != "GradingSystem" and not d.startswith(".")]

def read_file_content(path):
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return ""

def check_regex(content, pattern, flags=re.IGNORECASE):
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

def find_file_recursive(root, filename):
    for dirpath, dirnames, filenames in os.walk(root):
        for f in filenames:
            if f.lower() == filename.lower():
                return os.path.join(dirpath, f)
    return None

def find_project_root(student_path):
    # Strategy 1: Find Vehicle.java to locate the heart of the project
    vehicle_path = find_file_recursive(student_path, "Vehicle.java")
    if vehicle_path:
        # If found, check if it's in a package (e.g. Model)
        # If path is .../src/Model/Vehicle.java, we want .../src
        # If path is .../src/Vehicle.java, we want .../src
        
        dir_path = os.path.dirname(vehicle_path)
        parent_dir = os.path.basename(dir_path)
        
        if parent_dir.lower() == "model":
            return os.path.dirname(dir_path) # Go up one level from Model
        else:
            return dir_path # Assume default package or root of src
            
    # Strategy 2: Look for 'src' folder
    for root, dirs, files in os.walk(student_path):
        for d in dirs:
            if d.lower() == "src":
                return os.path.join(root, d)
                
    # Strategy 3: Just use the student path
    return student_path

def grade_student(student_path):
    print(f"Grading {os.path.basename(student_path)}...")
    
    # 1. Find Source Root
    src_path = find_project_root(student_path)
    # print(f"DEBUG: Source path determined as: {src_path}")

    # 2. Locate Files (Recursive search from src_path)
    # If src_path is wrong, we might miss files. 
    # So we search in src_path first. If not found, we search in student_path (fallback).
    
    def get_file(name):
        f = find_file_recursive(src_path, name)
        if not f:
            f = find_file_recursive(student_path, name)
        return f

    # Support for English (IP) and Indonesian (Regular) naming
    vehicle_file = get_file("Vehicle.java") or get_file("Kendaraan.java")
    vehicle_type_file = get_file("VehicleType.java") or get_file("JenisKendaraan.java")
    customer_file = get_file("Customer.java") or get_file("Costumer.java") or get_file("Pelanggan.java")
    main_file = get_file("Main.java")

    # Read Content
    vehicle_content = read_file_content(vehicle_file) if vehicle_file else ""
    vehicle_type_content = read_file_content(vehicle_type_file) if vehicle_type_file else ""
    customer_content = read_file_content(customer_file) if customer_file else ""
    main_content = read_file_content(main_file) if main_file else ""

    total_score = 0
    details = []

    # Fallback for single-file submission (Main.java)
    if main_content:
        if not vehicle_content and check_regex(main_content, r"class\s+(Vehicle|Kendaraan)"):
            vehicle_content = main_content
            details.append("[!] Info: Class Vehicle ditemukan di Main.java.")
        
        if not vehicle_type_content and check_regex(main_content, r"enum\s+(VehicleType|JenisKendaraan)"):
            vehicle_type_content = main_content
            details.append("[!] Info: Enum VehicleType ditemukan di Main.java.")

        if not customer_content and check_regex(main_content, r"class\s+(C(u|o)st(o|u)mer|Pelanggan)"):
            customer_content = main_content
            details.append("[!] Info: Class Customer ditemukan di Main.java.")

    # --- Grading Logic ---

    # 1. Structure (20%)
    s_score = 0
    if vehicle_file: s_score += 5
    elif vehicle_content == main_content:
        s_score += 2.5
        details.append("[-] Vehicle.java tidak ditemukan (ada di Main).")
    else: details.append("[-] Vehicle.java / Kendaraan.java tidak ditemukan.")
    
    if vehicle_type_file: s_score += 5
    elif vehicle_type_content == main_content:
        s_score += 2.5
        details.append("[-] VehicleType.java tidak ditemukan (ada di Main).")
    else: details.append("[-] VehicleType.java tidak ditemukan.")
    
    if customer_file: 
        s_score += 5
        if customer_file and "Costumer.java" in customer_file:
            details.append("[!] Warning: Typo nama file 'Costumer.java'.")
    elif customer_content == main_content:
        s_score += 2.5
        details.append("[-] Customer.java tidak ditemukan (ada di Main).")
    else: details.append("[-] Customer.java tidak ditemukan.")
    
    if main_file: s_score += 5
    else: details.append("[-] Main.java tidak ditemukan.")
    
    if s_score == 20:
        details.append("[+] Struktur file lengkap (+20).")
    
    total_score += (s_score / 20) * W_STRUCTURE

    # 2. VehicleType (10%)
    vt_score = 0
    if vehicle_type_content:
        if check_regex(vehicle_type_content, r"enum\s+(VehicleType|JenisKendaraan)"):
            vt_score += 2.5
            details.append("[+] VehicleType didefinisikan sebagai enum.")
        else:
            details.append("[-] VehicleType bukan enum.")
            
        if check_regex(vehicle_type_content, r"Car") or check_regex(vehicle_type_content, r"Mobil"): vt_score += 2.5
        else: details.append("[-] Enum Car/Mobil tidak ditemukan.")
        
        if check_regex(vehicle_type_content, r"Motorcycle") or check_regex(vehicle_type_content, r"Motor"): vt_score += 2.5
        else: details.append("[-] Enum Motorcycle/Motor tidak ditemukan.")
        
        if check_regex(vehicle_type_content, r"Truck") or check_regex(vehicle_type_content, r"Truk"): vt_score += 2.5
        else: details.append("[-] Enum Truck/Truk tidak ditemukan.")
    
    total_score += (vt_score / 10) * W_VEHICLE_TYPE

    # 3. Vehicle Class (30%)
    v_score = 0
    if vehicle_content:
        # Fields (10 pts)
        fields_found = 0
        if check_regex(vehicle_content, r"String\s+(brand|merk)"): fields_found += 1
        if check_regex(vehicle_content, r"int\s+(year|tahun)"): fields_found += 1
        if check_regex(vehicle_content, r"(VehicleType|JenisKendaraan)\s+(type|tipe|jenis)"): fields_found += 1
        if check_regex(vehicle_content, r"(double|float|int|long)\s+(price|harga)"): fields_found += 1
        
        v_score += (fields_found / 4) * 10
        if fields_found < 4:
            details.append(f"[-] Vehicle: Atribut tidak lengkap ({fields_found}/4 ditemukan).")
        else:
            details.append("[+] Vehicle: Atribut lengkap.")

        # Constructor (10 pts)
        if check_regex(vehicle_content, r"(Vehicle|Kendaraan)\s*\(\s*String"):
            v_score += 10
            details.append("[+] Vehicle: Constructor ditemukan.")
        else:
            details.append("[-] Vehicle: Constructor tidak ditemukan.")

        # showDetail (5 pts)
        if check_regex(vehicle_content, r"void\s+showDetail"):
            v_score += 5
            details.append("[+] Vehicle: Method showDetail ditemukan.")
        else:
            details.append("[-] Vehicle: Method showDetail tidak ditemukan.")

    total_score += (v_score / 25) * W_VEHICLE

    # 4. Customer Class (30%)
    c_score = 0
    if customer_content:
        # Fields (5 pts)
        if check_regex(customer_content, r"String\s+(name|nama)") and check_regex(customer_content, r"(Vehicle|Kendaraan)\s+(vehicle|kendaraan)"):
            c_score += 5
            details.append("[+] Customer: Atribut lengkap.")
        else:
            details.append("[-] Customer: Atribut kurang (name/nama, vehicle/kendaraan).")

        # Constructor (5 pts)
        if check_regex(customer_content, r"(C(u|o)st(o|u)mer|Pelanggan)\s*\(\s*String"):
            c_score += 5
            details.append("[+] Customer: Constructor ditemukan.")
        else:
            details.append("[-] Customer: Constructor tidak ditemukan.")

        # getTotalPrice (10 pts)
        if check_regex(customer_content, r"(double|float|int|long)\s+(getTotalPrice|getTotalHarga)"):
            c_score += 5
            if check_regex(customer_content, r"return\s+.*(price|harga)"):
                c_score += 5
                details.append("[+] Customer: getTotalPrice logika tampak benar.")
            else:
                details.append("[-] Customer: getTotalPrice ada tapi logika return mungkin salah.")
        else:
            details.append("[-] Customer: Method getTotalPrice tidak ditemukan.")

        # showDetail (5 pts)
        if check_regex(customer_content, r"void\s+showDetail"):
            c_score += 5
            details.append("[+] Customer: Method showDetail ditemukan.")
        else:
            details.append("[-] Customer: Method showDetail tidak ditemukan.")

    total_score += (c_score / 25) * W_CUSTOMER

    # 5. Main Class (10%)
    m_score = 0
    if main_content:
        # Instantiation Vehicle (5 pts)
        if check_regex(main_content, r"new\s+(Vehicle|Kendaraan)"):
            m_score += 5
            details.append("[+] Main: Instansiasi Vehicle ditemukan.")
        else:
            details.append("[-] Main: Tidak ada instansiasi Vehicle.")

        # Instantiation Customer (5 pts)
        if check_regex(main_content, r"new\s+(C(u|o)st(o|u)mer|Pelanggan)"):
            m_score += 5
            details.append("[+] Main: Instansiasi Customer ditemukan.")
        else:
            details.append("[-] Main: Tidak ada instansiasi Customer.")

        # Output / showDetail calls (10 pts)
        if check_regex(main_content, r"\.showDetail(s)?\s*\("):
            m_score += 10
            details.append("[+] Main: Pemanggilan showDetail ditemukan.")
        else:
            details.append("[-] Main: Tidak ada pemanggilan showDetail.")

    total_score += (m_score / 20) * W_MAIN

    # Report
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

    # Check if single project
    is_single_project = False
    if os.path.isdir(os.path.join(root_dir, "src")):
        is_single_project = True
    else:
        # Check for java files directly
        for f in os.listdir(root_dir):
            if f.endswith(".java"):
                is_single_project = True
                break
    
    if is_single_project:
        grade_student(root_dir)
    else:
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
