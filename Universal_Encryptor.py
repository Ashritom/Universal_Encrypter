import os
import json
import base64
import time
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidKey

def derive_key(password: str, salt: bytes):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=200000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def update_progress(progress_bar, value):
    progress_bar["value"] = value
    app.update_idletasks()

def animate_progress(progress_bar):
    progress_bar.pack()
    for i in range(0, 101, 2):
        update_progress(progress_bar, i)
        time.sleep(0.1)
    progress_bar.pack_forget()

def encrypt_file(input_path, password, progress_bar):
    animate_progress(progress_bar)
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
    
    encrypted_data = {
        "salt": base64.b64encode(salt).decode(),
        "iv": base64.b64encode(iv).decode(),
        "ciphertext": base64.b64encode(ciphertext).decode(),
        "original_ext": os.path.splitext(input_path)[1]
    }
    
    encrypted_path = input_path + ".enc"
    with open(encrypted_path, "w") as f:
        json.dump(encrypted_data, f)
    
    entry_password.delete(0, tk.END)
    messagebox.showinfo("Success", f"File encrypted successfully:\n{encrypted_path}")

def decrypt_file(encrypted_path, password, progress_bar):
    try:
        animate_progress(progress_bar)
        with open(encrypted_path, "r") as f:
            encrypted_data = json.load(f)
        
        salt = base64.b64decode(encrypted_data["salt"])
        iv = base64.b64decode(encrypted_data["iv"])
        ciphertext = base64.b64decode(encrypted_data["ciphertext"])
        original_ext = encrypted_data.get("original_ext", "")
        
        key = derive_key(password, salt)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        decryptor = cipher.decryptor()
        plaintext = decryptor.update(ciphertext) + decryptor.finalize()
        pad_len = plaintext[-1]
        plaintext = plaintext[:-pad_len]
        
        original_path = encrypted_path.replace(".enc", "") + original_ext
        with open(original_path, "wb") as f:
            f.write(plaintext)
        
        messagebox.showinfo("Success", f"File decrypted successfully:\n{original_path}")
    except (InvalidKey, ValueError):
        messagebox.showerror("Error", "Decryption failed: Incorrect password or corrupted file.")

def browse_file():
    file_path = filedialog.askopenfilename()
    entry_file.delete(0, tk.END)
    entry_file.insert(0, file_path)

def encrypt_action():
    file_path = entry_file.get()
    password = entry_password.get()
    if file_path and password:
        encrypt_file(file_path, password, progress_bar)
    else:
        messagebox.showerror("Error", "Please select a file and enter a password.")

def decrypt_action():
    file_path = entry_file.get()
    password = entry_password.get()
    if file_path and password:
        decrypt_file(file_path, password, progress_bar)
    else:
        messagebox.showerror("Error", "Please select a file and enter a password.")

app = tk.Tk()
app.title("Secure File Encryption")
app.geometry("600x450")
app.configure(bg="#2E3B4E")

header_label = tk.Label(app, text="Secure File Encryption", font=("Arial", 16, "bold"), fg="white", bg="#2E3B4E")
header_label.pack(pady=15)

tk.Label(app, text="Select File:", fg="white", bg="#2E3B4E").pack()
entry_file = tk.Entry(app, width=60)
entry_file.pack()
tk.Button(app, text="Browse", command=browse_file, bg="#4CAF50", fg="white").pack(pady=5)

tk.Label(app, text="Enter Password:", fg="white", bg="#2E3B4E").pack()
entry_password = tk.Entry(app, width=60, show="*")
entry_password.pack()

progress_bar = ttk.Progressbar(app, orient="horizontal", length=400, mode="determinate")
progress_bar.pack(pady=10)
progress_bar.pack_forget()

tk.Button(app, text="Encrypt", command=encrypt_action, bg="#2196F3", fg="white").pack(pady=5)
tk.Button(app, text="Decrypt", command=decrypt_action, bg="#F44336", fg="white").pack(pady=5)

app.mainloop()
