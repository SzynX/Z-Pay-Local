# 💎 Z-Pay 2.0 Pro: Decentralized Local Ecosystem

![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![UI](https://img.shields.io/badge/UI-CustomTkinter-blue?style=for-the-badge)
![Security](https://img.shields.io/badge/Security-Zero--Knowledge-627eea?style=for-the-badge)
![Standard](https://img.shields.io/badge/Crypto-SECP256k1-orange?style=for-the-badge)

**Z-Pay 2.0 Pro** is a high-fidelity cryptocurrency simulation platform. It features a professional **Ethereum-style Web3 interface**, multi-account management, and military-grade local encryption. Designed for practicing secure transaction logic and private key management in a 100% offline, zero-knowledge environment.

---

## ✨ Key Features

*   **🌐 Ethereum 2.0 Aesthetics:** Full-screen immersive UI with glassmorphism effects and professional Web3 color palettes.
*   **👥 Multi-Account Vault:** Create and manage multiple independent wallets. Each account is encrypted with its own unique identity.
*   **🔐 Zero-Knowledge Privacy:** Your master password is never stored. Private keys are derived locally using **PBKDF2** and encrypted with **AES-256**.
*   **⛓️ Simulated Blockchain:** A local `global_ledger.json` acts as the network, validating transactions via **ECDSA (SECP256k1) signatures**.
*   **📊 Advanced Explorer:** Real-time balance tracking, unique TXIDs (Transaction Hashes), and detailed inbound/outbound history with status icons.

---

## 🚀 Quick Start

### 1. Prerequisites
Ensure you have **Python 3.11** or newer installed in your JetBrains PyCharm environment.

### 2. Installation
Open your terminal and install the necessary libraries:

```bash
pip install customtkinter cryptography ecdsa pyperclip
```

### 🚀 3. Run the Application
To launch the professional Web3 interface, ensure all dependencies are installed and run the main script:

```bash
python main.py
```

### 🛠️ Project Architecture
The system is built on a modular architecture to ensure clean code and separation of concerns:

GUI & Controller	main.py	Handles full-screen rendering, multi-account switching, and the Web3 dashboard.
Crypto Engine	engine.py	The security core: Handles SECP256k1 keygen, AES encryption, and digital signatures.
Ledger System	ledger.py	The simulated network: Validates balances, verifies signatures, and manages the transaction database.
Secure Vault	vault.json	Local encrypted database for your private keys and wallet metadata.
Global Ledger	global_ledger.json	The public ledger containing all confirmed peer-to-peer transactions.

### 🛡️ Security Protocol

Our security model follows industry-leading blockchain standards to protect local data:

Identity: Based on the SECP256k1 elliptic curve (The global industry standard used by Bitcoin and Ethereum).

Encryption: Symmetric encryption via Fernet (AES-256-CBC) ensures your keys are safe even if the file is stolen.

Authentication: Passwords are used solely for key derivation (PBKDF2) and are never written to disk or stored in memory longer than necessary.

Integrity: Every transaction is hashed using SHA-256 and signed. The ledger rejects any transaction without a valid mathematical proof of ownership.

### 📸 Interface Overview

Experience a professional Web3 environment directly on your desktop:

Login Screen: Securely unlock your personal vault using your master password.

Dashboard: A stunning full-screen view featuring a massive balance card and a quick-copy address bar.

Send Assets: A sleek, modern form to transfer ZCOINS to any 0x-address within the local simulation.

History Explorer: A detailed, color-coded log of all blockchain activities, complete with unique TX hashes and timestamps.

### ⚠️ Disclaimer
**IMPORTANT**: This is an educational and practice tool. The "ZCOINS" handled within this application have no real-world value. Never use your real-world cryptocurrency passwords or private keys in any simulation or practice software.

**Developed with ❤️ for the Web3 Developer Community.**

Optimized for JetBrains PyCharm & Python.

