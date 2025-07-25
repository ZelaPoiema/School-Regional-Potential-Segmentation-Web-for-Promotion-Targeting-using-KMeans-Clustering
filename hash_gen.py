import bcrypt

password = input("Masukkan password: ")
hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
print("Hashed password:", hashed)
