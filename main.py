import customtkinter as ctk
import json
import os
from engine import CryptoEngine
from ledger import Ledger

ctk.set_appearance_mode("dark")


class ZPayApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Z-Pay Local (Zero Knowledge Practice)")
        self.geometry("500x600")
        self.ledger = Ledger()
        self.current_wallet = None  # Memóriában tartott kulcs (ideiglenes)

        self.setup_ui()

    def setup_ui(self):
        self.main_container = ctk.CTkFrame(self)
        self.main_container.pack(fill="both", expand=True, padx=20, pady=20)

        if os.path.exists("wallet.json"):
            self.show_login()
        else:
            self.show_registration()

    def show_registration(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_container, text="Új Tárca Létrehozása", font=("Arial", 20)).pack(pady=20)
        pwd_entry = ctk.CTkEntry(self.main_container, placeholder_text="Mester Jelszó", show="*")
        pwd_entry.pack(pady=10)

        def create():
            priv, pub = CryptoEngine.generate_keypair()
            enc_priv = CryptoEngine.encrypt_private_key(priv, pwd_entry.get())
            with open("wallet.json", "w") as f:
                json.dump({"address": pub, "vault": enc_priv}, f)
            self.show_login()

        ctk.CTkButton(self.main_container, text="Generálás", command=create).pack(pady=20)

    def show_login(self):
        self.clear_frame()
        ctk.CTkLabel(self.main_container, text="Bejelentkezés (Feloldás)", font=("Arial", 20)).pack(pady=20)
        pwd_entry = ctk.CTkEntry(self.main_container, placeholder_text="Jelszó", show="*")
        pwd_entry.pack(pady=10)

        def unlock():
            with open("wallet.json", "r") as f:
                data = json.load(f)
            priv = CryptoEngine.decrypt_private_key(data['vault'], pwd_entry.get())
            if priv:
                self.current_wallet = {"priv": priv, "pub": data['address']}
                self.show_dashboard()
            else:
                print("Hibás jelszó!")

        ctk.CTkButton(self.main_container, text="Feloldás", command=unlock).pack(pady=20)

    def show_dashboard(self):
        self.clear_frame()
        addr = self.current_wallet['pub']
        balance = self.ledger.get_balance(addr)

        ctk.CTkLabel(self.main_container, text="Irányítópult", font=("Arial", 20)).pack(pady=10)
        ctk.CTkLabel(self.main_container, text=f"Címed: {addr[:15]}...", text_color="gray").pack()
        ctk.CTkLabel(self.main_container, text=f"Egyenleg: {balance} ZCOIN", font=("Arial", 24, "bold")).pack(pady=20)

        recipient_entry = ctk.CTkEntry(self.main_container, placeholder_text="Fogadó címe")
        recipient_entry.pack(fill="x", pady=5)
        amount_entry = ctk.CTkEntry(self.main_container, placeholder_text="Összeg")
        amount_entry.pack(fill="x", pady=5)

        def send():
            rec = recipient_entry.get()
            amo = float(amount_entry.get())
            msg = f"{addr}-{rec}-{amo}"
            sig = CryptoEngine.sign_transaction(self.current_wallet['priv'], msg)
            success, info = self.ledger.add_transaction(addr, rec, amo, sig)
            print(info)
            self.show_dashboard()

        ctk.CTkButton(self.main_container, text="Küldés", command=send, fg_color="green").pack(pady=20)
        ctk.CTkButton(self.main_container, text="Kijelentkezés", command=self.show_login, fg_color="red").pack(pady=10)

    def clear_frame(self):
        for widget in self.main_container.winfo_children():
            widget.destroy()


if __name__ == "__main__":
    app = ZPayApp()
    app.mainloop()