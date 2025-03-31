from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
import os
import json
import base64
import re
import random
import time
import zlib
import hmac
import hashlib
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes

def generate_otp():
    return str(random.randint(100000, 999999))

def derive_keys(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=64,
        salt=salt,
        iterations=600000,
    )
    derived_keys = kdf.derive(password.encode())
    return derived_keys[:32], derived_keys[32:]

def compress_data(data):
    return zlib.compress(data, level=9)

def decompress_data(data):
    return zlib.decompress(data)

def get_encrypted_file_name(user_filename=None):
    if user_filename:
        return f"{user_filename}.xyz"
    return base64.urlsafe_b64encode(os.urandom(16)).decode().rstrip("=") + ".xyz"

def encrypt_file(input_path, password, user_filename=None):
    salt = os.urandom(16)
    aes_key, hmac_key = derive_keys(password, salt)
    iv = os.urandom(12)
    encryption_otp = generate_otp()
    print(f"Your OTP for encryption: {encryption_otp}")
    user_otp = input("Enter the OTP for encryption: ")
    if user_otp != encryption_otp:
        return "Error: Incorrect OTP. Encryption aborted."

    with open(input_path, "rb") as f:
        plaintext = f.read()
    
    compressed_data = compress_data(plaintext)
    file_extension = os.path.splitext(input_path)[1].encode()
    
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv))
    encryptor = cipher.encryptor()
    ciphertext = encryptor.update(file_extension + b"::" + compressed_data) + encryptor.finalize()
    tag = encryptor.tag
    
    hmac_value = hmac.new(hmac_key, ciphertext, hashlib.sha256).digest()
    encrypted_data = salt + iv + tag + hmac_value + ciphertext
    encrypted_path = os.path.join("uploads", get_encrypted_file_name(user_filename))
    
    with open(encrypted_path, "wb") as f:
        f.write(encrypted_data)
    
    return encrypted_path

def decrypt_file(encrypted_path, password):
    decryption_otp = generate_otp()
    print(f"Your OTP for decryption: {decryption_otp}")
    user_otp = input("Enter the OTP for decryption: ")
    if user_otp != decryption_otp:
        return "Error: Incorrect OTP. Decryption aborted."

    with open(encrypted_path, "rb") as f:
        encrypted_data = f.read()
    
    salt, iv, tag, hmac_value, ciphertext = encrypted_data[:16], encrypted_data[16:28], encrypted_data[28:44], encrypted_data[44:76], encrypted_data[76:]
    aes_key, hmac_key = derive_keys(password, salt)
    
    expected_hmac = hmac.new(hmac_key, ciphertext, hashlib.sha256).digest()
    if not hmac.compare_digest(expected_hmac, hmac_value):
        time.sleep(3)
        return "Error: Decryption failed due to HMAC verification failure."
    
    cipher = Cipher(algorithms.AES(aes_key), modes.GCM(iv, tag))
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(ciphertext) + decryptor.finalize()
    
    file_extension, compressed_data = decrypted_data.split(b"::", 1)
    plaintext = decompress_data(compressed_data)
    
    decrypted_path = encrypted_path.replace(".xyz", "") + file_extension.decode()
    with open(decrypted_path, "wb") as f:
        f.write(plaintext)
    
    return decrypted_path

app = Flask(__name__)
if not os.path.exists('uploads'):
    os.makedirs('uploads')

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'file' not in request.files or 'password' not in request.form:
        return jsonify({"error": "File and password are required"}), 400

    file = request.files['file']
    password = request.form['password']
    user_filename = request.form.get('filename', None)

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    encrypted_path = encrypt_file(file_path, password, user_filename)
    if "Error" in encrypted_path:
        return jsonify({"error": encrypted_path}), 400
    
    return jsonify({"message": "File encrypted successfully", "encrypted_file_path": encrypted_path})

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'file' not in request.files or 'password' not in request.form:
        return jsonify({"error": "File and password are required"}), 400

    file = request.files['file']
    password = request.form['password']

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    decrypted_path = decrypt_file(file_path, password)
    if "Error" in decrypted_path:
        return jsonify({"error": decrypted_path}), 400

    return send_file(decrypted_path, as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

@app.route('/')
def index():
    return render_template('index.html')
app.run(debug=True)