from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
import os
import json
import base64
import re
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes, hmac
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey

app = Flask(__name__)

if not os.path.exists('uploads'):
    os.makedirs('uploads')
def derive_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def compute_hmac(key, data):
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    return h.finalize()

def verify_hmac(key, data, expected_hmac):
    h = hmac.HMAC(key, hashes.SHA256(), backend=default_backend())
    h.update(data)
    try:
        h.verify(expected_hmac)
        return True
    except InvalidKey:
        return False

def is_strong_password(password):
    if (len(password) >= 8 and
        re.search(r"[A-Z]", password) and
        re.search(r"[a-z]", password) and
        re.search(r"\d", password) and
        re.search(r"[!@#$%^&*(),.?\":{}|<>]", password)):
        return True
    return False

def encrypt_file(input_path, password):
    if not is_strong_password(password):
        return "Error: Password is too weak! Use at least 8 characters, including upper/lowercase, numbers, and special symbols."

    salt = os.urandom(16)
    key = derive_key(password, salt)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()

    with open(input_path, "rb") as f:
        plaintext = f.read()

    pad_len = 16 - (len(plaintext) % 16)
    plaintext += bytes([pad_len] * pad_len)
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()

    metadata = {
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "original_ext": os.path.splitext(input_path)[1]
    }
    metadata_json = json.dumps(metadata).encode()
    hmac_value = compute_hmac(key, metadata_json)
    encrypted_metadata = metadata_json + hmac_value

    encrypted_path = os.path.join('uploads', os.path.basename(input_path) + ".enc")
    with open(encrypted_path, "wb") as f:
        f.write(encrypted_metadata)

    return encrypted_path

def decrypt_file(encrypted_path, password):
    try:
        with open(encrypted_path, "rb") as f:
            encrypted_metadata = f.read()

        metadata_json = encrypted_metadata[:-32]
        received_hmac = encrypted_metadata[-32:]
        metadata = json.loads(metadata_json)

        salt = base64.b64decode(metadata["salt"])
        iv = base64.b64decode(metadata["iv"])
        ciphertext = base64.b64decode(metadata["ciphertext"])
        original_ext = metadata.get("original_ext", "")

        key = derive_key(password, salt)

        if not verify_hmac(key, metadata_json, received_hmac):
            return "Decryption failed: Data integrity compromised."

        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()

        pad_len = plaintext[-1]
        plaintext = plaintext[:-pad_len]

        original_path = encrypted_path.replace(".enc", "") + original_ext
        with open(original_path, "wb") as f:
            f.write(plaintext)

        return original_path
    except (InvalidKey, ValueError, json.JSONDecodeError) as e:
        return "Decryption failed: Incorrect password or corrupted file."

@app.route('/encrypt', methods=['POST'])
def encrypt():
    if 'file' not in request.files or 'password' not in request.form:
        return jsonify({"error": "File and password are required"}), 400

    file = request.files['file']
    password = request.form['password']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    encrypted_path = encrypt_file(file_path, password)

<<<<<<< HEAD:Universal_Encryptor_secure.py
    if "Error" in encrypted_path:
        return jsonify({"error": encrypted_path}), 400

    encrypted_file_url = f'/uploads/{os.path.basename(encrypted_path)}'

=======
    # Generate a URL for downloading the encrypted file
    encrypted_file_url = f'/uploads/{os.path.basename(encrypted_path)}'

    print(f"Encrypted file URL: {encrypted_file_url}")

    return send_file(encrypted_path, as_attachment=True)

>>>>>>> 15a6432cc96cdb22f5e4e3471dfd573879738748:server.py
    return jsonify({
        "message": "File encrypted successfully",
        "encrypted_file_path": encrypted_file_url
    })

@app.route('/decrypt', methods=['POST'])
def decrypt():
    if 'file' not in request.files or 'password' not in request.form:
        return jsonify({"error": "File and password are required"}), 400

    file = request.files['file']
    password = request.form['password']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    file_path = os.path.join('uploads', file.filename)
    file.save(file_path)

    if not os.path.exists(file_path):
        return jsonify({"error": "File could not be saved correctly. Please try again."}), 400

    decrypted_path = decrypt_file(file_path, password)

    if "Decryption failed" in decrypted_path:
        return jsonify({"error": decrypted_path}), 400

    return send_file(decrypted_path, as_attachment=True)

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    file_path = os.path.join('uploads', filename)
    if os.path.exists(file_path):
        return send_from_directory('uploads', filename)
    else:
        return jsonify({"error": "File not found"}), 404

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
