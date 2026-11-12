# Secure File Vault

## Project Overview

Secure File Vault is a local desktop application made to protect sensitive files. The main idea of the project is to let users securely encrypt, decrypt, verify, store, and manage files using a simple graphical interface.

The project uses different cybersecurity techniques such as AES-256-GCM encryption, Argon2id password protection, SHA-256 integrity checking, and security activity logging.

---

## Main Features

The application includes:

- Master password authentication
- Argon2id password hashing and key derivation
- AES-256-GCM file encryption
- AES-256-GCM file decryption
- SHA-256 file integrity checking
- Tamper detection
- Automatic integrity checking before decryption
- Dedicated storage for encrypted files
- Separate storage for decrypted files
- View Vault Files option
- Duplicate filename protection
- Secure file removal with confirmation
- Manual vault locking
- Error handling
- Security audit logging

---

## How the Security Works

The main security process is:

Master Password
      ↓
Argon2id
      ↓
256-bit Key
      ↓
AES-256-GCM Encryption
      ↓
Encrypted File Stored in Vault
      ↓
SHA-256 Integrity Check
      ↓
AES-256-GCM Decryption


If an encrypted file is modified, the integrity check fails and the application blocks decryption.

---

## Technologies Used

- Python
- CustomTkinter
- Tkinter
- AES-256-GCM
- SHA-256
- Argon2id
- Git
- GitHub
- Trello
- Visual Studio Code

Main Python libraries:

customtkinter
argon2-cffi
cryptography


---

## Project Structure

SecureFileVault/
│
├── main.py
├── crypto.py
├── integrity.py
├── password_manager.py
├── file_manager.py
├── audit_logger.py
├── requirements.txt
├── .gitignore
│
├── vault_files/        # Created automatically
├── retrieved_files/    # Created automatically
├── audit_logs/         # Created automatically
└── vault_config.json   # Created after vault setup


Sensitive files such as encrypted vault files, logs, and vault configuration are ignored by Git and are not uploaded to the public repository.

---

## Installation

### 1. Clone the repository

git clone https://github.com/Tasnimnoormsk3/205-Group-Project.git


### 2. Open the project folder

cd 205-Group-Project


### 3. Install the required libraries

pip3 install -r requirements.txt


### 4. Run the application

python3 main.py

---

## How to Use

### Unlock the Vault

On the first run, enter a master password of at least 12 characters. 
This password will be used to unlock the vault in future sessions.

Enter the master password and click:

**Create / Unlock Vault**

If the password is correct, the protected functions will become available.

### Encrypt a File

1. Click **Add File**
2. Select a file
3. Click **Encrypt**
4. The encrypted file will be stored inside `vault_files/`

A SHA-256 integrity record is also created.

### Decrypt a File

1. Click **View Vault Files**
2. Select a `.vault` file
3. Click **Decrypt**
4. The system checks the file integrity first
5. If the file is safe, it is decrypted into `retrieved_files/`

### Verify Integrity

Select a vault file and click:

**Verify Integrity**

If the file has been changed, the application displays an integrity warning.

### Lock the Vault

Click:

**Lock Vault**

This disables the protected functions until the correct master password is entered again.

### View Security Activity

Click:

**View Activity Log**

The application records events such as successful or failed unlock attempts, encryption, decryption, integrity checks, and file removal.

---


## Security Principles

The project mainly focuses on:

**Confidentiality**  
AES-256-GCM is used to protect file contents.

**Integrity**  
SHA-256 is used to check whether encrypted files have been changed.

**Authentication**  
The master password and Argon2id are used to protect access to the vault.

**Accountability**  
The audit log records important security activities.

---


## Team Members

### Tasnim Noor Muskan

### Masrafe Hasan Tuhin



## Repository

GitHub:

https://github.com/Tasnimnoormsk3/205-Group-Project


---

## Conclusion

Secure File Vault shows how different cybersecurity techniques can be combined in one simple desktop application.

The final system can encrypt and decrypt files, verify file integrity, detect tampering, protect access using a master password, safely manage protected files, and record important security events.

Overall, the project helped us understand how encryption, authentication, integrity checking, and secure file management can be used together in a practical application.