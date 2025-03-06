# Universal_Encrypter

### **Description:**  
This Python program provides a secure encryption and decryption system for any file type. It uses **AES-256 encryption** with **PBKDF2 key derivation** to ensure high security. The program features a **graphical user interface (GUI)** using **Tkinter**, where users can select a file, enter a password, and encrypt or decrypt it. A **progress bar animation** is included to indicate encryption and decryption progress.  

---

### **Algorithm:**  

#### **Encryption Process:**  
1. Select a file using the GUI file browser.  
2. Enter a password for encryption.  
3. Generate a **random salt (16 bytes)** for key derivation.  
4. Derive a **256-bit AES key** using PBKDF2-HMAC-SHA256.  
5. Generate a **random IV (Initialization Vector, 16 bytes)** for AES-CBC mode.  
6. Read the file's content and apply **PKCS7 padding** to align with AES block size.  
7. Encrypt the padded content using AES-256 in CBC mode.  
8. Store the **salt, IV, encrypted data, and original file extension** in a JSON file with a `.enc` extension.  
9. Display a success message and clear the password field.  

---

#### **Decryption Process:**  
1. Select the encrypted `.enc` file using the GUI.  
2. Enter the correct password used for encryption.  
3. Extract the **salt, IV, and encrypted content** from the `.enc` file.  
4. Derive the **AES key** using the salt and password.  
5. Decrypt the content using AES-256 in CBC mode.  
6. Remove PKCS7 padding from the decrypted content.  
7. Restore the original file with its **correct extension**.  
8. Display a success message or an error message if the password is incorrect.  

---

This program ensures **strong security** with **randomized salts, IVs, and secure key derivation**, making it difficult to crack even with brute force.
