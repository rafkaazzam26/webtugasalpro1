def petunjuk():
    print("Selamat datang di kalkulator sederhana!")
    print("masukkan dua angka dan pilih operasi yang ingin dilakukan.")
    print("Anda dapat melakukan operasi penjumlahan (+), pengurangan (-), perkalian (*), dan pembagian (/).")


def pertambahan(angka1, angka2):
    return angka1 + angka2


def pengurangan(angka1, angka2):
    return angka1 - angka2


def perkalian(angka1, angka2):
    return angka1 * angka2


def pembagian(angka1, angka2):
    return angka1 / angka2


def operasi(pilihan, angka1, angka2):
    if pilihan == "+":
        return pertambahan(angka1, angka2)
    elif pilihan == "-":
        return pengurangan(angka1, angka2)
    elif pilihan == "*":
        return perkalian(angka1, angka2)
    elif pilihan == "/":
        return pembagian(angka1, angka2)
    else:
        print("Operasi tidak valid.")
        return None


petunjuk()

angka1 = float(input("Masukkan angka pertama: "))
angka2 = float(input("Masukkan angka kedua: "))
pilihan = input("Pilih operasi (+, -, *, /): ")

hasil = operasi(pilihan, angka1, angka2)
print("Hasil dari", angka1, pilihan, angka2, "adalah:", hasil)

