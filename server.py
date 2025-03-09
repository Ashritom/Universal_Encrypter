from flask import Flask, request, jsonify, send_file, render_template, send_from_directory
import os
import json
import base64
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey

app = Flask(__name__)

# Ensure the uploads directory exists
if not os.path.exists('uploads'):
    os.makedirs('uploads')

# Function to derive encryption key from password
def derive_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

# Encrypt file function
def encrypt_file(input_path, password):
    salt = os.urandom(16)
    key = derive_key(password, salt)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    
    with open(input_path, "rb") as f:
        plaintext = f.read()
    
    # Pad plaintext to be a multiple of AES block size (16)
    pad_len = 16 - (len(plaintext) % 16)
    plaintext += bytes([pad_len] * pad_len)
    
    ciphertext = encryptor.update(plaintext) + encryptor.finalize()
    
    encrypted_data = {
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "original_ext": os.path.splitext(input_path)[1]
    }
    
    encrypted_path = os.path.join('uploads', os.path.basename(input_path) + ".enc")
    
    with open(encrypted_path, "w") as f:
        json.dump(encrypted_data, f)
    
    return encrypted_path

# Decrypt file function with additional debugging
def decrypt_file(encrypted_path, password):
    try:
        with open(encrypted_path, "r") as f:
            encrypted_data = json.load(f)
        
        # Debugging: Log decrypted data from file
        print(f"Encrypted data: {encrypted_data}")

        salt = base64.b64decode(encrypted_data["salt"])
        iv = base64.b64decode(encrypted_data["iv"])
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        original_ext = encrypted_data.get("original_ext", "")
        
        key = derive_key(password, salt)
        
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        
        # Debugging: Log decrypted data length
        print(f"Decrypted plaintext length: {len(plaintext)}")
        
        # Remove padding
        pad_len = plaintext[-1]
        plaintext = plaintext[:-pad_len]
        
        # Debugging: Log final plaintext
        print(f"Final plaintext length after padding removal: {len(plaintext)}")
        
        original_path = encrypted_path.replace(".enc", "") + original_ext
        with open(original_path, "wb") as f:
            f.write(plaintext)
        
        return original_path
    except (InvalidKey, ValueError) as e:
        return f"Decryption Error: {str(e)}"
    except Exception as e:
        return f"Unexpected error during decryption: {str(e)}"

# Encrypt route
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

    # Generate a URL for downloading the encrypted file
    encrypted_file_url = f'/uploads/{os.path.basename(encrypted_path)}'

    print(f"Encrypted file URL: {encrypted_file_url}")

    return send_file(encrypted_path, as_attachment=True)

    return jsonify({
        "message": "File encrypted successfully",
        "encrypted_file_path": encrypted_file_url
    })

# Decrypt route
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
    
    # Debugging: Check if file exists after saving
    if not os.path.exists(file_path):
        return jsonify({"error": "File could not be saved correctly. Please try again."}), 400
    
    decrypted_path = decrypt_file(file_path, password)
    
    # Handle errors during decryption
    if "Decryption Error" in decrypted_path or "Unexpected error" in decrypted_path:
        return jsonify({"error": decrypted_path}), 400
    
    return send_file(decrypted_path, as_attachment=True)

# Serve encrypted file from the uploads directory
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory('uploads', filename)

# Index route
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == "__main__":
    app.run(debug=True)
