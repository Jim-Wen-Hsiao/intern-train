import bcrypt

plain_password = "Newjersey2024!"
hashed = bcrypt.hashpw(plain_password.encode('utf-8'), bcrypt.gensalt())
print(hashed.decode())