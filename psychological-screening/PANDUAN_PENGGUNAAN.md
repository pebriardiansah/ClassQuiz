# 📋 PANDUAN PENGGUNAAN SISTEM SKRINING PSIKOLOGIS HR RUMAH SAKIT

## Daftar Isi
1. [Pengantar](#pengantar)
2. [Persiapan Awal](#persiapan-awal)
3. [Cara Menggunakan](#cara-menggunakan)
4. [Interpretasi Hasil](#interpretasi-hasil)
5. [Troubleshooting](#troubleshooting)

---

## PENGANTAR {#pengantar}

### Apa itu Sistem Ini?
Sistem Skrining Psikologis adalah alat berbasis ClassQuiz yang membantu HR Rumah Sakit melakukan penilaian awal kepribadian dan mental health calon karyawan untuk posisi:
- 👨‍⚕️ **Dokter**
- 👩‍⚕️ **Perawat**
- 👶 **Bidan**

### Keuntungan
✅ Objektif dan terukur (bukan subjektif)  
✅ Cepat (selesai dalam 30 menit per kandidat)  
✅ Tidak memerlukan psikolog (HR bisa melaksanakan)  
✅ Hasil otomatis ter-interpretasi dengan rekomendasi  
✅ Dapat di-track dan di-export untuk dokumentasi  
✅ Self-hosted di rumah sakit (data aman)

### Disclaimer
⚠️ Sistem ini adalah **alat screening awal**, BUKAN pengganti evaluasi psikolog profesional. Untuk keputusan kritis, konsultasikan dengan psikolog klinis.

---

## PERSIAPAN AWAL {#persiapan-awal}

### 1. Setup Teknis
```bash
# Clone atau download ClassQuiz
git clone https://github.com/mawoka-myblock/ClassQuiz.git
cd ClassQuiz

# Copy soal-soal dari folder psychological-screening
# ke dalam database ClassQuiz

# Setup environment
docker-compose up -d
```

### 2. Import Soal ke ClassQuiz
1. Login sebagai admin ke dashboard ClassQuiz
2. Buat Quiz baru untuk setiap posisi:
   - Skrining Psikologis - Dokter
   - Skrining Psikologis - Perawat
   - Skrining Psikologis - Bidan
3. Copy-paste soal dari file JSON ke dalam ClassQuiz

### 3. Konfigurasi HR Access
1. Buat akun HR di ClassQuiz
2. Set permissions untuk akses dashboard hasil
3. Share link quiz ke kandidat via email

---

## CARA MENGGUNAKAN {#cara-menggunakan}

### Untuk HR/Administrator

#### Step 1: Kirim Quiz ke Kandidat
1. Pilih posisi yang akan di-tes (Dokter/Perawat/Bidan)
2. Generate link khusus untuk kandidat
3. Kirim via email dengan instruksi:

```
Subyek: Tes Skrining Psikologis - Posisi [POSISI]

Yth. Calon Karyawan,

Sebagai bagian dari proses seleksi, kami meminta Anda untuk mengikuti tes skrining psikologis.
Tes ini akan membantu kami memahami kesesuaian kepribadian Anda dengan posisi yang ditawarkan.

Link Test: [URL]
Durasi: ~30 menit
Deadline: [TANGGAL]

Terima kasih,
HR Department
```

#### Step 2: Monitor Partisipasi
- Dashboard menunjukkan siapa saja yang sudah mengerjakan
- Reminder otomatis untuk yang belum selesai
- Real-time update hasil

#### Step 3: Review Hasil
1. Buka Dashboard HR
2. Lihat tabel kandidat dengan skor
3. Klik nama kandidat untuk detail lengkap
4. Baca rekomendasi di bagian "💡 Rekomendasi untuk HR"

### Untuk Kandidat

#### Persiapan
- Pastikan koneksi internet stabil
- Catat waktu tes (durasi ~30 menit)
- Jawab dengan jujur, tidak ada jawaban "benar" atau "salah"
- Pastikan lingkungan tenang untuk fokus

#### Cara Menjawab
1. Baca setiap pertanyaan dengan teliti
2. Pilih jawaban yang paling sesuai dengan diri Anda
3. Jangan terlalu lama berpikir untuk setiap soal
4. Gunakan instink/perasaan pertama Anda
5. Klik tombol "Selesai" setelah menjawab semua

---

## INTERPRETASI HASIL {#interpretasi-hasil}

### Skala Scoring
- **Overall Score**: 1-5 (semakin tinggi semakin baik)
- **Personality Traits**: 1-5 per dimensi
- **Stress Resilience**: 1-5
- **Emotional Intelligence**: 1-5

### Status Rekomendasi

#### 🟢 PROCEED (Lanjut)
**Meaning**: Kandidat menunjukkan profil psikologis yang sesuai
**Action**: Lanjut ke tahap interview berikutnya
**Score**: Overall ≥ 3.8, Red Flags: 0

#### 🟡 FURTHER ASSESSMENT (Verifikasi)
**Meaning**: Ada beberapa aspek yang perlu dikonfirmasi
**Action**: HR melakukan interview verifikasi lebih mendalam
**Score**: Overall 3.4-3.7, Red Flags: 1

#### 🔴 CAUTION (Hati-Hati)
**Meaning**: Ada indikasi signifikan yang perlu dievaluasi
**Action**: Tinjau ulang atau rujuk ke psikolog profesional
**Score**: Overall < 3.4, Red Flags: ≥ 2

### Komponen Penilaian

#### Untuk DOKTER
```
✓ Conscientiousness (25%) - Teruji, detail, disiplin
✓ Openness (20%) - Terbuka terhadap ide baru dan pembelajaran
✓ Emotional Intelligence (15%) - Komunikasi pasien & team
✓ Agreeableness (15%) - Empati, teamwork
✓ Stress Resilience (15%) - Tahan tekanan medis
✓ Emotional Stability (10%) - Stabil dalam emergency

Red Flags:
❌ Neuroticism > 4.2 (cemas berlebihan)
❌ Conscientiousness < 3.0 (risiko kesalahan)
❌ Stress handling < 3.0 (tidak siap beban kerja)
❌ Empathy < 3.0 (kurang peduli pasien)
```

#### Untuk PERAWAT
```
✓ Agreeableness (30%) - Empati & kepedulian pasien KRITIS
✓ Conscientiousness (20%) - Detail dalam perawatan
✓ Stress Resilience (20%) - Tahan dalam emergency
✓ Emotional Intelligence (20%) - Komunikasi efektif
✓ Emotional Stability (10%) - Stabil & tidak mudah burnout

Red Flags:
❌ Agreeableness < 3.5 (kurang empati)
❌ Neuroticism > 4.0 (mudah burnout)
❌ Stress resilience < 3.5 (tidak tahan emergency)
```

#### Untuk BIDAN
```
✓ Agreeableness (30%) - Maternal care membutuhkan empati tinggi
✓ Conscientiousness (25%) - Prosedur ketat untuk safety
✓ Stress Resilience (20%) - Situasi darurat obstetri
✓ Emotional Intelligence (15%) - Komunikasi ibu & bayi
✓ Emotional Stability (10%) - Pregnant women sensitif

Red Flags:
❌ Agreeableness < 3.6 (KRITIS untuk maternal care)
❌ Conscientiousness < 3.8 (risiko safety)
❌ Neuroticism > 4.0 (ibu hamil sensitif)
```

---

## TROUBLESHOOTING {#troubleshooting}

### Q: Kandidat menjawab terlalu cepat (< 5 menit)
**A**: Hasil mungkin tidak akurat. Minta kandidat untuk mengulang dengan lebih teliti.

### Q: Semua kandidat mendapat score tinggi
**A**: Kemungkinan ada bias "social desirability" (jawab apa yang diharapkan). Gunakan wawancara untuk verifikasi.

### Q: Score rendah tapi HR merasa cocok
**A**: Gunakan ini sebagai starting point diskusi, bukan determinan final. Interview mendalam untuk clarifikasi.

### Q: Ada kandidat dengan score tinggi tapi banyak red flags
**A**: Red flags adalah "warning signs" spesifik. Jika ada 2+ red flags, konsultasi psikolog sebelum hiring.

### Q: Bagaimana jika kandidat tidak selesai tes?
**A**: Data yang tersimpan tidak lengkap. Ajakin ulang dengan waktu yang cukup.

---

## DATA PRIVACY & SECURITY

✅ Semua data tersimpan di server rumah sakit (self-hosted)  
✅ Akses terbatas untuk HR staff authorized  
✅ Backup reguler dilakukan  
✅ Compliance dengan regulasi data protection  

---

## KONTAK SUPPORT

Untuk pertanyaan teknis atau interpretasi hasil:
- Email: hr-tech@rumahsakit.id
- Internal Wiki: [link]
- Training materials: [link]

---

**Last Updated**: 2026-07-22  
**Version**: 1.0  
**Maintained by**: HR Technology Team
