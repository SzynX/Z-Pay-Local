import customtkinter as ctk
import json
import os
import pyperclip
from engine import CryptoEngine
from ledger import Ledger

# Ethereum stílusú színpaletta
ETH_DARK = "#0d0e12"
ETH_CARD = "#1a1c23"
ETH_ACCENT = "#627eea"
ETH_TEXT = "#ffffff"
ETH_GRAY = "#94a3b8"

ctk.set_appearance_mode("dark")


class ZPayApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Z-Pay Pro v1.6 - Stable UI")
        self.geometry("1100x720")
        self.configure(fg_color=ETH_DARK)

        self.ledger = Ledger()
        self.current_user = None
        self.vault_path = "vault.json"

        self.content_area = None
        self.sidebar = None

        if not os.path.exists(self.vault_path):
            with open(self.vault_path, "w") as f:
                json.dump({"accounts": []}, f)

        self.show_account_selector()

    def clear_screen(self):
        for widget in self.winfo_children():
            widget.destroy()

    # --- 1. NÉZET: FIÓK VÁLASZTÓ ---

    def show_account_selector(self):
        self.clear_screen()
        self.current_user = None

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=0, column=0)

        ctk.CTkLabel(container, text="Z-PAY PRO", font=("Arial", 42, "bold"), text_color=ETH_ACCENT).pack(pady=(0, 10))
        ctk.CTkLabel(container, text="Válasszon fiókot a folytatáshoz", font=("Arial", 16), text_color=ETH_GRAY).pack(
            pady=(0, 30))

        list_frame = ctk.CTkScrollableFrame(container, width=450, height=300, fg_color=ETH_CARD, corner_radius=15,
                                            border_width=1, border_color="#2d2f36")
        list_frame.pack(pady=10)

        with open(self.vault_path, "r") as f:
            vault = json.load(f)

        if not vault["accounts"]:
            ctk.CTkLabel(list_frame, text="Nincs még mentett fiók", text_color=ETH_GRAY).pack(pady=40)
        else:
            for acc in vault["accounts"]:
                acc_btn = ctk.CTkButton(
                    list_frame,
                    text=f"  {acc['name']}\n  {acc['address'][:18]}...",
                    font=("Arial", 14, "bold"),
                    anchor="w",
                    fg_color="#252730",
                    hover_color="#2d303d",
                    height=70,
                    corner_radius=10,
                    command=lambda a=acc: self.show_login(a)
                )
                acc_btn.pack(fill="x", pady=5, padx=10)

        ctk.CTkButton(container, text="+ Új tárca létrehozása", font=("Arial", 16, "bold"), fg_color=ETH_ACCENT,
                      height=50, corner_radius=10, command=self.show_create_account).pack(pady=20, fill="x")

    # --- 2. NÉZET: REGISZTRÁCIÓ ---

    def show_create_account(self):
        self.clear_screen()
        container = ctk.CTkFrame(self, fg_color=ETH_CARD, corner_radius=20, border_width=1, border_color="#2d2f36")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(container, text="Új Ethereum-stílusú tárca", font=("Arial", 22, "bold")).pack(pady=(30, 20),
                                                                                                   padx=40)

        name_in = ctk.CTkEntry(container, placeholder_text="Fiók neve", width=320, height=45, fg_color=ETH_DARK)
        name_in.pack(pady=10, padx=40)

        pwd_in = ctk.CTkEntry(container, placeholder_text="Mester jelszó", show="*", width=320, height=45,
                              fg_color=ETH_DARK)
        pwd_in.pack(pady=10, padx=40)

        status_lbl = ctk.CTkLabel(container, text="", text_color="#E74C3C")
        status_lbl.pack()

        def perform_creation():
            name = name_in.get()
            pwd = pwd_in.get()
            if not name or not pwd: return

            priv, addr, pub = CryptoEngine.generate_keypair()
            enc_priv = CryptoEngine.encrypt_private_key(priv, pwd)

            with open(self.vault_path, "r") as f: vault = json.load(f)
            vault["accounts"].append({"name": name, "address": addr, "pub": pub, "vault": enc_priv})
            with open(self.vault_path, "w") as f: json.dump(vault, f, indent=4)
            self.show_account_selector()

        ctk.CTkButton(container, text="Tárca Generálása", font=("Arial", 15, "bold"), command=perform_creation,
                      fg_color=ETH_ACCENT, height=45, width=320).pack(pady=20)
        ctk.CTkButton(container, text="Mégse", fg_color="transparent", text_color=ETH_GRAY,
                      command=self.show_account_selector).pack(pady=(0, 20))

    # --- 3. NÉZET: BELÉPÉS ---

    def show_login(self, acc_data):
        self.clear_screen()
        container = ctk.CTkFrame(self, fg_color=ETH_CARD, corner_radius=20, border_width=1, border_color="#2d2f36")
        container.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(container, text=acc_data['name'], font=("Arial", 26, "bold"), text_color=ETH_ACCENT).pack(
            pady=(30, 5), padx=60)
        ctk.CTkLabel(container, text=f"Unlock {acc_data['address'][:15]}...", font=("Arial", 12),
                     text_color=ETH_GRAY).pack(pady=(0, 20))

        pwd_in = ctk.CTkEntry(container, placeholder_text="Adja meg a jelszót", show="*", width=320, height=45,
                              fg_color=ETH_DARK)
        pwd_in.pack(pady=10, padx=40)

        def unlock():
            priv = CryptoEngine.decrypt_private_key(acc_data['vault'], pwd_in.get())
            if priv:
                self.current_user = {"name": acc_data['name'], "priv": priv, "pub": acc_data['pub'],
                                     "addr": acc_data['address']}
                self.build_main_interface()
            else:
                pwd_in.configure(border_color="#E74C3C")

        ctk.CTkButton(container, text="Fiók Feloldása", font=("Arial", 15, "bold"), command=unlock, fg_color=ETH_ACCENT,
                      height=45, width=320).pack(pady=20)
        ctk.CTkButton(container, text="Vissza", fg_color="transparent", text_color=ETH_GRAY,
                      command=self.show_account_selector).pack(pady=(0, 20))

    # --- 4. NÉZET: FŐ DASHBOARD ---

    def build_main_interface(self):
        self.clear_screen()
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)

        self.sidebar = ctk.CTkFrame(self, width=260, fg_color=ETH_CARD, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        self.sidebar.grid_rowconfigure(4, weight=1)

        ctk.CTkLabel(self.sidebar, text="Z-PAY PRO", font=("Arial", 22, "bold"), text_color=ETH_ACCENT).pack(pady=40)

        for t, c in [("Dashboard", self.draw_dashboard), ("Küldés", self.draw_send), ("Előzmények", self.draw_history)]:
            ctk.CTkButton(self.sidebar, text=t, fg_color="transparent", anchor="w", command=c, height=50).pack(fill="x",
                                                                                                               padx=15,
                                                                                                               pady=2)

        ctk.CTkButton(self.sidebar, text="Kijelentkezés", fg_color="#252730", text_color="#E74C3C",
                      command=self.show_account_selector).pack(side="bottom", pady=30, padx=20, fill="x")

        self.content_area = ctk.CTkFrame(self, fg_color="transparent")
        self.content_area.grid(row=0, column=1, sticky="nsew", padx=40, pady=40)
        self.draw_dashboard()

    def draw_dashboard(self):
        self.clear_content()
        balance = self.ledger.get_balance(self.current_user['addr'])

        ctk.CTkLabel(self.content_area, text=f"Üdvözöljük, {self.current_user['name']}!",
                     font=("Arial", 28, "bold")).pack(anchor="w")

        card = ctk.CTkFrame(self.content_area, fg_color=ETH_ACCENT, corner_radius=20, height=180)
        card.pack(fill="x", pady=30)
        card.pack_propagate(False)

        ctk.CTkLabel(card, text="Összesített egyenleg", font=("Arial", 16), text_color="#e2e8f0").pack(pady=(35, 0))
        ctk.CTkLabel(card, text=f"{balance:,.2f} ZCOIN", font=("Arial", 46, "bold")).pack()

        info = ctk.CTkFrame(self.content_area, fg_color=ETH_CARD, corner_radius=15, border_width=1,
                            border_color="#2d2f36")
        info.pack(fill="x", pady=10)

        ctk.CTkLabel(info, text=f"Címed: {self.current_user['addr']}", font=("Consolas", 14)).pack(side="left", padx=20,
                                                                                                   pady=20)

        def copy():
            pyperclip.copy(self.current_user['addr'])
            copy_btn.configure(text="Másolva!", fg_color="#2ECC71")
            self.after(2000, lambda: copy_btn.configure(text="Másolás",
                                                        fg_color=ETH_ACCENT) if copy_btn.winfo_exists() else None)

        copy_btn = ctk.CTkButton(info, text="Másolás", width=90, fg_color=ETH_ACCENT, command=copy)
        copy_btn.pack(side="right", padx=20)

    def draw_send(self):
        self.clear_content()
        ctk.CTkLabel(self.content_area, text="Pénz küldése", font=("Arial", 24, "bold")).pack(anchor="w", pady=(0, 30))

        # JAVÍTÁS: padx és pady eltávolítva a konstruktorból, átrakva a pack()-be
        form = ctk.CTkFrame(self.content_area, fg_color=ETH_CARD, corner_radius=20, border_width=1,
                            border_color="#2d2f36")
        form.pack(fill="x", padx=0, pady=0)  # Itt lehetne padding, de a belső elemeknél jobb

        inner_container = ctk.CTkFrame(form, fg_color="transparent")
        inner_container.pack(padx=30, pady=30, fill="x")

        target_in = ctk.CTkEntry(inner_container, placeholder_text="Fogadó 0x címe", width=550, height=45,
                                 fg_color=ETH_DARK)
        target_in.pack(pady=10)

        amt_in = ctk.CTkEntry(inner_container, placeholder_text="Összeg (ZCOIN)", width=550, height=45,
                              fg_color=ETH_DARK)
        amt_in.pack(pady=10)

        status_lbl = ctk.CTkLabel(inner_container, text="")
        status_lbl.pack()

        def initiate():
            try:
                amt = float(amt_in.get())
                target = target_in.get()
                msg = f"{self.current_user['addr']}-{target}-{amt}"
                sig = CryptoEngine.sign_transaction(self.current_user['priv'], msg)
                ok, res = self.ledger.add_transaction(self.current_user['pub'], self.current_user['addr'], target, amt,
                                                      sig)
                status_lbl.configure(text=res, text_color="#2ECC71" if ok else "#E74C3C")
            except:
                status_lbl.configure(text="Hiba: Érvénytelen összeg!", text_color="#E74C3C")

        ctk.CTkButton(inner_container, text="Tranzakció Aláírása és Küldése", font=("Arial", 16, "bold"),
                      fg_color=ETH_ACCENT, height=50, width=300, command=initiate).pack(pady=20)

    def draw_history(self):
        self.clear_content()
        ctk.CTkLabel(self.content_area, text="Tranzakciós előzmények", font=("Arial", 24, "bold")).pack(anchor="w",
                                                                                                        pady=(0, 20))

        scroll = ctk.CTkScrollableFrame(self.content_area, fg_color="transparent", height=450)
        scroll.pack(fill="both", expand=True)

        history = self.ledger.get_history(self.current_user['addr'])
        for tx in history:
            is_in = tx['receiver_addr'] == self.current_user['addr']
            f = ctk.CTkFrame(scroll, fg_color=ETH_CARD, height=80, corner_radius=12)
            f.pack(fill="x", pady=4)

            color = "#2ECC71" if is_in else "#E74C3C"
            ctk.CTkLabel(f, text="↙" if is_in else "↗", font=("Arial", 24, "bold"), text_color=color).pack(side="left",
                                                                                                           padx=20)

            info = ctk.CTkFrame(f, fg_color="transparent")
            info.pack(side="left", pady=10)
            ctk.CTkLabel(info, text=tx['date'], font=("Arial", 11), text_color=ETH_GRAY).pack(anchor="w")
            ctk.CTkLabel(info, text=f"ID: {tx['tx_id']}", font=("Consolas", 11), text_color="#4f5159").pack(anchor="w")

            ctk.CTkLabel(f, text=f"{'+' if is_in else '-'}{tx['amount']} ZCOIN", font=("Arial", 18, "bold"),
                         text_color=color).pack(side="right", padx=25)

    def clear_content(self):
        if self.content_area:
            for widget in self.content_area.winfo_children():
                widget.destroy()


if __name__ == "__main__":
    app = ZPayApp()
    app.mainloop()