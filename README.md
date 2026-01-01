# Grading System

Folder ini berisi sistem penilaian otomatis untuk Studi Kasus OOP.

## Modul 1: Vehicle & Customer Service

Script: `grade_modul1_v2.py`

### Kriteria Penilaian Modul 1 (Total 100%)

1.  **Struktur File (20%)**
    - Keberadaan file `Vehicle.java`, `VehicleType.java`, `Customer.java`, `Main.java`.
    - *Note: Jika digabung dalam satu file Main.java, nilai struktur parsial.*

2.  **VehicleType (10%)**
    - Didefinisikan sebagai `enum`.
    - Memiliki nilai `CAR`, `MOTORCYCLE`, `TRUCK`.

3.  **Vehicle Class (30%)**
    - Atribut lengkap (`brand`, `year`, `type`, `price`).
    - Constructor valid.
    - Method `showDetail`.

4.  **Customer Class (30%)**
    - Atribut lengkap (`name`, `vehicle`).
    - Constructor valid.
    - Method `getTotalPrice` (return price dari vehicle).
    - Method `showDetail`.

5.  **Main Class (10%)**
    - Instansiasi objek `Vehicle` dan `Customer`.
    - Pemanggilan `showDetail`.

## Modul 2: Player & Score

Script: `grade.py`

### Kriteria Penilaian Modul 2 (Total 100%)

Sistem penilaian saat ini menggunakan analisis statis (memeriksa kode sumber) untuk poin-poin berikut:

#### 1. Struktur & Enkapsulasi (20%)

- **Package Model (5%)**: Folder `Model` harus ada.
- **Deklarasi Package (5%)**: File `Player.java` dan `Score.java` harus memiliki deklarasi `package Model;`.
- **Enkapsulasi (5%)**: Class `Player` harus memiliki minimal 3 atribut (field) yang bersifat `private`.
- **Tipe Data UML (5%)**: Class `Player` harus menggunakan tipe data `UUID` dan `LocalDateTime`.

#### 2. Implementasi Interface (15%)

- **Definisi Interface (5%)**: File `ShowDetail.java` harus mendefinisikan interface `ShowDetail` dengan method `void showDetail();`.
- **Implementasi Player (5%)**: Class `Player` harus mengimplementasikan interface `ShowDetail`.
- **Implementasi Score (5%)**: Class `Score` harus mengimplementasikan interface `ShowDetail`.

#### 3. Logika Constructor (20%)

- **Generate UUID (5%)**: Constructor `Player` harus menghasilkan ID menggunakan `UUID.randomUUID()`.
- **Waktu Saat Ini (5%)**: Constructor `Player` harus mencatat waktu pembuatan menggunakan `LocalDateTime.now()`.
- **Inisialisasi (5%)**: Field numerik pada `Player` harus diinisialisasi (misal ke 0).
- **Constructor Score (5%)**: Constructor `Score` harus melakukan assignment nilai ke field (pola `this.var = var`).

#### 4. Logika Method (30%)

- **updateHighScore (10%)**: Method ini harus memiliki logika pengecekan `if (new > old)`.
- **addCoins (5%)**: Method ini harus menggunakan operator `+=` untuk menambah koin.
- **addDistance (5%)**: Method ini harus menggunakan operator `+=` untuk menambah jarak.
- **showDetail (10%)**: Method ini harus menampilkan output menggunakan `System.out.println`.

#### 5. Main Class (15%)

- **Instansiasi Objek (5%)**: `Main.java` harus membuat minimal 2 objek `Player` dan 3 objek `Score`.
- **Update State (5%)**: `Main.java` harus memanggil method `updateHighScore` dan `addCoins`.
- **Output (5%)**: `Main.java` harus memanggil method `showDetail`.

## Cara Penggunaan

### Menilai Modul 1
```bash
python grade_modul1_v2.py <path_to_student_folders>
```

### Menilai Modul 2
```bash
python grade.py <path_to_student_folders>
```

    Contoh jika folder mahasiswa ada di folder luar:

    ```bash
    python grade.py ..
    ```

    ![picture 0](https://i.imgur.com/51grB20.png)

## Catatan

- File `GradingTest.java` disertakan untuk referensi pengujian unit (JUnit), namun script `grade.py` saat ini fokus pada pengecekan struktur dan pola kode (Static Analysis).
