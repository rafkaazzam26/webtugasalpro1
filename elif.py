nilai1 = float(input("Masukkan nilai pertama: "))
nilai2 = float(input("Masukkan nilai kedua: "))
nilai3 = float(input("Masukkan nilai ketiga: "))
ujian_akhir = float(input("Masukkan nilai ujian akhir: "))

rata_rata = (nilai1 + nilai2 + nilai3) / 3

hasil_akhir = (rata_rata * 0.6) + (ujian_akhir * 0.4)
hasil_akhir = min(hasil_akhir, 100)  # Membatasi hasil akhir maksimal 100

print("\nrata-rata nilai: ", rata_rata)
print("Hasil akhir: ", hasil_akhir)

if hasil_akhir >= 85 and hasil_akhir <= 100:
    print("Predikat: A")

elif hasil_akhir >= 75 and hasil_akhir < 85:
    print("Predikat: B")

elif hasil_akhir >= 65 and hasil_akhir < 75 :
    print("Predikat: C")

else:
    print("Predikat: DO")