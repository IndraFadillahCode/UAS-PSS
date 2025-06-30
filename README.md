# 🏫 be_simple_lms

**be_simple_lms** adalah platform Learning Management System (LMS) sederhana berbasis Django dibuat untuk UAS pss

---

## ✨ Fitur & Endpoint Utama

- [Endpoint +1] Register: untuk memungkinkan calon user mendaftar secara langsung dengan mengisikan biodata dan data login.
- [Endpoint +1] Batch Enroll Students: memungkinkan teacher untuk mendaftarkan beberapa siswa ke dalam kursus yang dimilikinya sekaligus.
- [Endpoint +1] Content Comment Moderation: memungkinkan teacher untuk menentukan apakah suatu komentar pada content course-nya boleh ditampilkan atau tidak.
    - Perubahan pada tampil komentar, di mana comment yang muncul hanya yang sudah dimoderasi.
- [Endpoint +1] User Activity Dashboard: Menampilkan statistik aktivitas pengguna dalam kursus. Data yang harus ditampilkan adalah:
    - Jumlah course yang diikuti sebagai student
    - Jumlah course yang dibuat
    - Jumlah komentar yang pernah ditulis
    - Jumlah content yang diselesaikan (jika fitur content completion dibuat)
- [Endpoint +1] Course Analytics: Menyediakan statistik course, meliputi:
    - Jumlah member pada course tersebut
    - Jumlah konten pada course tersebut
    - Jumlah komentar pada course tersebut
    - Jumlah feedback pada course tersebut (jika fitur feedback dibuat)
- [Improve +1] Content Scheduling: Teacher dapat menjadwalkan konten untuk dirilis pada waktu tertentu saja. Di luar waktu tersebut, konten tidak boleh muncul pada saat di-list.
- [Improve +1] Course Enrollment Limits: Menetapkan batasan jumlah pendaftar course:
    - Satu student hanya bisa enroll sekali pada course yang sama
    - Teacher bisa menentukan jumlah maksimal student
    - Jika kuota penuh, tidak ada lagi studen yang bisa masuk
- [Fitur | Endpoint +3] Course Completion Certificates: menampilkan halaman HTML berupa sertifikat bagi pengguna yang menyelesaikan kursus.
    - Menyelesaikan fitur ini sama dengan menyelesaikan 3 endpoint dengan syarat halaman sertifikatnya didesain dengan baik.

### [Fitur +4] Course Announcements
Fitur tambahan agar seorang teacher bisa memberikan pengumuman khusus pada course tertentu yang akan muncul pada tanggal tertentu. Endpoint yang perlu ditambahakan untuk fitur ini adalah:

    [Endpoint] Create announcement: untuk menambahkan pengumuman pada course tertentu (hanya teacher yang dapat membuat announcement)
    [Endpoint] Show announcement: untuk menampilkan semua pengumuman pada course tertentu (teacher dan student dapat menampilkan announcement)
    [Endpoint] Edit announcement: untuk mengedit announcement (hanya teacher yang dapat mengedit announcement)
    [Endpoint] Delete announcement: endpoint untuk menghapus announcement (hanya teacher yang dapat menghapus announcement)

### [Fitur +3] Content Completion Tracking
Menambahkan fitur agar student bisa menandai content yang sudah diselesaikan. Fitur ini memerlukan tabel tambahan yaitu tabel completion tracking.

    [Endpoint] Add completion tracking: student dapat menandai bahwa suatu konten sudah diselesaikan.
    [Endpoint] Show completion: student dapat menampilkan list completion pada suatu course yang dia ikuti
    [Endpoint] Delete completion: student dapat menghapus data completion-nya sendiri.

### [Fitur +4] Course Feedback
Memungkinkan teacher mengumpulkan umpan balik dari student tentang kursus yang telah diikuti.

    [Endpoint] Add Feedback: untuk menambahkan feedback pada course tertentu
    [Endpoint] Show feedback: untuk menampilkan semua feedback pada course tertentu
    [Endpoint] Edit feedback: student dapat mengedit feedback yang sudah ditulisnya
    [Endpoint] Delete feedback: student dapat menghapus feedback yang sudah ditulisnya

### [Fitur +3] Content Bookmarking
Memungkinkan pengguna menandai konten kursus untuk referensi di masa mendatang.

    [Endpoint] Add bookmarking: untuk student membuat bookmark pada course content yang bisa diakses.
    [Endpoint] Show bookmark: untuk menampilkan semua bookmark yang dibuat oleh student tersebut. Bookmark harus menampilkan konten dan course-nya juga.
    [Endpoint] Delete bookmark: untuk menghapus bookmark yang pernah dibuat student tersebut.

---

## 🚀 Cara Menjalankan Project

### 1. **Clone Repository**
```bash
# Ganti URL sesuai repo kamu
 git clone <repo-url>
 cd be_simple_lms
```

### 2. **Setup Virtual Environment & Install Dependencies**
```bash
python -m venv venv
source venv/bin/activate  # (Linux/macOS)
venv\Scripts\activate    # (Windows)
pip install -r requirements.txt
```

### 3. **Migrasi Database**
```bash
cd code
python manage.py makemigrations
python manage.py migrate
```

### 4. **Jalankan Server**
```bash
python manage.py runserver
```
Akses di: [http://localhost:8000](http://localhost:8000)

### 5. **Jalankan dengan Docker**
```bash
docker-compose up --build
```

---

## 🛠️ Teknologi
- Python, Django, NinjaAPI
- SQLite (default, bisa diganti)
- Docker & docker-compose
- Locust (load testing)

---

## 👨‍💻 Kontribusi
Pull request & issue sangat terbuka untuk pengembangan lebih lanjut!

---

## 📄 Lisensi
Proyek ini open-source, silakan gunakan dan modifikasi sesuai kebutuhan.

A11.2022.14186
Indra Fadillah