embege = ["ayam", "ikan", "pecel", "tempe", "tahu", "sayur", "buah"]
skor = 0

print("Selamat datang di permainan Tebak embege!")
print("tebak menu 3 hari yang akan datang")

embege1 = input("Tebak makanan yang akan anda makan hari 1: ")
if embege1 in embege:
    print("Tebakan anda benar!")
    skor += 1
else:
    print("Tebakan anda salah!")

embege2 = input("Tebak makanan yang akan anda makan hari 2: ")
if embege2 in embege:   
    print("Tebakan anda benar!")
    skor += 1
else:
    print("Tebakan anda salah!")

embege3 = input("Tebak makanan yang akan anda makan hari 3: ")
if embege3 in embege:
    print("Tebakan anda benar!")
    skor += 1
else:
    print("Tebakan anda salah!")

print("Skor akhir anda adalah: ", skor)