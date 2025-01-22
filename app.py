import os
import sys
import time
import requests
import base64
from datetime import datetime
from Crypto.Cipher import AES
from Crypto.Hash import SHA256
from Crypto import Random

# Функция для получения текущего пароля с веб-сайта
def get_current_password():
    try:
        response = requests.get('http://localhost:5000/password')
        if response.status_code == 200:
            data = response.json()
            return data['password']
        else:
            print('Ошибка при получении пароля с сервера.')
            sys.exit()
    except Exception as e:
        print('Ошибка при подключении к серверу:', e)
        sys.exit()

# Функции для шифрования и расшифровки
def encrypt_file(key, filename):
    chunksize = 64 * 1024
    outputFile = filename + ".enc"
    filesize = str(os.path.getsize(filename)).zfill(16)
    IV = Random.new().read(16)

    encryptor = AES.new(key, AES.MODE_CBC, IV)

    with open(filename, 'rb') as infile:
        with open(outputFile, 'wb') as outfile:
            outfile.write(filesize.encode('utf-8'))
            outfile.write(IV)

            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                elif len(chunk) % 16 != 0:
                    chunk += b' ' * (16 - len(chunk) % 16)

                outfile.write(encryptor.encrypt(chunk))
    print(f"Файл {filename} зашифрован и сохранен как {outputFile}")

def decrypt_file(key, filename):
    chunksize = 64 * 1024
    outputFile = filename[:-4]  # Убираем '.enc'

    with open(filename, 'rb') as infile:
        filesize = int(infile.read(16))
        IV = infile.read(16)

        decryptor = AES.new(key, AES.MODE_CBC, IV)

        with open(outputFile, 'wb') as outfile:
            while True:
                chunk = infile.read(chunksize)
                if len(chunk) == 0:
                    break
                outfile.write(decryptor.decrypt(chunk))
            outfile.truncate(filesize)
    print(f"Файл {filename} расшифрован и сохранен как {outputFile}")

# Функция для получения ключа из пароля
def get_key(password):
    hasher = SHA256.new(password.encode('utf-8'))
    return hasher.digest()

# Основная функция
def main():
    # Аутентификация
    password = get_current_password()
    user_input = input("Введите текущий пароль для доступа к приложению: ")
    if user_input != password:
        print("Неверный пароль!")
        sys.exit()

    print("\nВыберите действие:")
    print("1. Зашифровать файл")
    print("2. Расшифровать файл")
    choice = input("Введите число (1 или 2): ")

    if choice == '1':
        filename = input("Введите путь к файлу для шифрования: ")
        if not os.path.exists(filename):
            print("Файл не найден!")
            sys.exit()
          
        encrypt_file(get_key(password), filename)

    elif choice == '2':
        filename = input("Введите путь к файлу для расшифровки: ")
        if not os.path.exists(filename):
            print("Файл не найден!")
            sys.exit()
        decrypt_file(get_key(password), filename)
    else:
        print("Неверный выбор!")
        sys.exit()

if __name__ == '__main__':
    main()
