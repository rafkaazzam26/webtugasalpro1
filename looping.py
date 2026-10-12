menu_angkringan = ["Nasi ati", "Nasi cumi", "Nasi kulit", "Nasi kucing", "Nasi bakar"]
harga_per_porsi = 10000
biaya_parkir = 2000
pesanan = []
total_harga = 0

print("Halo, berikut adalah menu angkringan kami:")

for nomor, nama_menu in enumerate(menu_angkringan):
    print(str(nomor) + ". " + nama_menu + " - Rp" + str(harga_per_porsi))

continue_ordering = True

while continue_ordering:
    answer = input("Apakah kamu ingin memesan makanan? (y/t): ").lower()

    if answer == "y":
        valid_choice = False

        while not valid_choice:
            pilihan = input("Pilih nomor menu: ")

            if pilihan.isdigit() and 0 <= int(pilihan) < len(menu_angkringan):
                nama_menu = menu_angkringan[int(pilihan)]
                pesanan.append(nama_menu)
                total_harga += harga_per_porsi
                print("Menambahkan " + nama_menu + " ke dalam pesanan.")
                valid_choice = True
            else:
                print("Tolong masukkan nomor yang tersedia di menu.")
    else:
        continue_ordering = False

print("\nPesanan kamu:")
for nama_menu in pesanan:
    print("- " + nama_menu)

print("Total harga makanan: Rp" + str(total_harga))
print("Biaya parkir: Rp" + str(biaya_parkir))
total_bayar = total_harga + biaya_parkir
print("Total yang harus dibayar: Rp" + str(total_bayar))
print("Terima kasih sudah berkunjung!")